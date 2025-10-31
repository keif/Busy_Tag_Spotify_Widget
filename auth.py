import webbrowser
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib.parse import urlencode, urlparse, parse_qs
import hashlib
import base64
import random
import string

REDIRECT_URI = 'http://127.0.0.1:8080/callback'
SCOPE = 'user-read-currently-playing user-read-private user-read-email'

def generate_random_string(length):
    possible = string.ascii_letters + string.digits + '-._~'
    return ''.join(random.choice(possible) for _ in range(length))

def generate_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')
    return code_challenge

class AuthHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress HTTP server log messages for cleaner output
        pass

    def do_GET(self):
        parsed_path = urlparse(self.path)

        # Only handle /callback requests - ignore everything else
        if parsed_path.path != '/callback':
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Not found. Waiting for Spotify callback...")
            return

        query = parsed_path.query
        params = parse_qs(query)

        # Check for errors from Spotify
        error = params.get('error', [None])[0]
        if error:
            error_description = params.get('error_description', ['Unknown error'])[0]
            print(f"\n✗ Spotify authorization error: {error}")
            print(f"  Description: {error_description}")
            self.server.auth_code = None

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"Authorization failed: {error_description}".encode())

            threading.Thread(target=self.server.shutdown).start()
            return

        self.server.auth_code = params.get('code', [None])[0]

        if self.server.auth_code:
            print("\n✓ Received authorization code from Spotify")

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Authorization successful. You can close this window.")

        threading.Thread(target=self.server.shutdown).start()

def authorize_user(client_id):
    code_verifier = generate_random_string(64)
    code_challenge = generate_code_challenge(code_verifier)
    
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': SCOPE,
        'code_challenge_method': 'S256',
        'code_challenge': code_challenge,
        'redirect_uri': REDIRECT_URI,
    }
    
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    print(f"\nOpening browser for Spotify authorization...")
    print(f"If authorization fails, ensure this redirect URI is added to your Spotify App:")
    print(f"  → {REDIRECT_URI}")
    print(f"  → Add it at: https://developer.spotify.com/dashboard\n")

    webbrowser.open(auth_url)

    server_address = ('127.0.0.1', 8080)
    httpd = HTTPServer(server_address, AuthHandler)

    print("Waiting for user authorization...")

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()

    # Wait up to 120 seconds for authorization
    timeout_seconds = 120
    elapsed = 0

    try:
        while server_thread.is_alive() and elapsed < timeout_seconds:
            server_thread.join(timeout=1)
            elapsed += 1
    except KeyboardInterrupt:
        print("\nAuthorization cancelled by user.")
        httpd.shutdown()

    # If timed out, shut down server
    if elapsed >= timeout_seconds:
        print(f"\n✗ Authorization timed out after {timeout_seconds} seconds")
        httpd.shutdown()
        server_thread.join()
        return None, None

    if hasattr(httpd, 'auth_code') and httpd.auth_code:
        print(f"Authorization: Ok.")
        return httpd.auth_code, code_verifier
    else:
        print("Authorization failed.")
        return None, None

def get_access_token(client_id, code, code_verifier):
    token_url = "https://accounts.spotify.com/api/token"
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': client_id,
        'code_verifier': code_verifier,
    }
    
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    try:
        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        token_response.raise_for_status()
        token_json = token_response.json()
        return token_json.get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Error while requesting access token: {e}")
        return None