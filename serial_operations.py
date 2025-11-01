import time
import serial
import serial.tools.list_ports

def open_serial_connection(port='COM4', baudrate=115200):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        return ser
    except serial.SerialException as e:
        print(f"Failed to open serial connection: {e}")
        return None

def send_serial_command(ser, command):
    try:
        if ser and ser.is_open:
            ser.write((command).encode())
            ser.flush()
            response = ser.readline().decode().strip()            
            return response
        else:
            print("Serial connection is not open.")
            return None
    except serial.SerialException as e:
        print(f"Failed to send command: {e}")
        return None

def close_serial_connection(ser):
    if ser and ser.is_open:
        ser.close()

def find_busy_tag_device():
    ports = serial.tools.list_ports.comports()
    for port_info in ports:
        port = port_info.device
        try:
            ser = serial.Serial(port, baudrate=115200, timeout=1)
            ser.write(b'AT+GDN\r\n')
            response = ser.readline().decode('utf-8').strip()
            ser.close()
            if response.startswith("+DN:busytag-"):
                return port
        except (serial.SerialException, UnicodeDecodeError):
            continue
    return 
 
        