#!/usr/bin/env python3
"""
BusyTag Volume Refresh Module

Provides functionality to remount a BusyTag e-ink display volume
to trigger display refresh after image updates.

Usage:
    from busytag_refresh import refresh_busytag

    # After saving image
    save_spotify_image('/Volumes/NO NAME/now_playing.bmp')
    refresh_busytag(volume_name="NO NAME")
"""

import subprocess
import time
import logging
import re
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_disk_identifier(volume_name: str) -> Optional[str]:
    """
    Find the disk identifier (e.g., 'disk4') for a given volume name.

    Args:
        volume_name: The name of the volume to find (e.g., "NO NAME", "BUSYTAG")

    Returns:
        The disk identifier (e.g., "disk4") or None if not found
    """
    try:
        logger.debug(f"Searching for volume '{volume_name}'...")
        result = subprocess.run(
            ['diskutil', 'list'],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse diskutil list output to find the disk identifier
        # Look for lines like:   1:                 FAT32 NO NAME               104.9 MB   disk4s1
        # or:  /dev/disk4 (external, physical):

        lines = result.stdout.split('\n')
        current_disk = None

        for line in lines:
            # Check if this line defines a disk device
            disk_match = re.search(r'/dev/(disk\d+)\s+\(external', line)
            if disk_match:
                current_disk = disk_match.group(1)
                logger.debug(f"Found external disk: {current_disk}")
                continue

            # Check if this line contains our volume name
            if volume_name in line and current_disk:
                logger.debug(f"Found volume '{volume_name}' on {current_disk}")
                return current_disk

        logger.warning(f"Volume '{volume_name}' not found in diskutil list output")
        return None

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to execute diskutil list: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while searching for disk: {e}")
        return None


def mount_disk(disk_identifier: str) -> bool:
    """
    Remount the specified disk to trigger BusyTag display refresh.

    Args:
        disk_identifier: The disk identifier (e.g., "disk4")

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.debug(f"Remounting disk '{disk_identifier}'...")

        result = subprocess.run(
            ['diskutil', 'mount', f"/dev/{disk_identifier}"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            logger.debug(f"✓ Disk '{disk_identifier}' remounted successfully")
            return True
        else:
            # Check if it's already mounted - that's actually fine
            if "already mounted" in result.stderr.lower() or "already mounted" in result.stdout.lower():
                logger.debug(f"✓ Disk '{disk_identifier}' already mounted (triggered refresh)")
                return True
            else:
                logger.error(f"Failed to remount '{disk_identifier}': {result.stderr}")
                return False

    except subprocess.TimeoutExpired:
        logger.error(f"Remount operation timed out for '{disk_identifier}'")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during remount: {e}")
        return False


def verify_mount(volume_name: str, timeout: int = 3) -> bool:
    """
    Verify that a volume is mounted by checking if its path exists.

    Args:
        volume_name: The name of the volume to verify
        timeout: Maximum seconds to wait for mount to appear

    Returns:
        True if volume is accessible, False otherwise
    """
    import os
    mount_path = f"/Volumes/{volume_name}"

    for attempt in range(timeout):
        if os.path.exists(mount_path):
            logger.debug(f"✓ Volume '{volume_name}' is accessible at {mount_path}")
            return True
        if attempt < timeout - 1:
            logger.debug(f"Waiting for mount to appear (attempt {attempt + 1}/{timeout})...")
            time.sleep(1)

    logger.warning(f"Volume '{volume_name}' not accessible after {timeout} seconds")
    return False


def refresh_busytag(volume_name: str = "NO NAME", mount_delay: float = 0.5) -> bool:
    """
    Refresh BusyTag e-ink display by remounting its volume.

    This function:
    1. Finds the disk identifier for the specified volume
    2. Remounts the disk to trigger display refresh
    3. Verifies the volume is still accessible

    Args:
        volume_name: Name of the BusyTag volume (default: "NO NAME")
        mount_delay: Seconds to wait after remounting (default: 0.5)

    Returns:
        True if refresh was successful, False otherwise

    Example:
        >>> save_spotify_image('/Volumes/NO NAME/now_playing.bmp')
        >>> if refresh_busytag():
        ...     print("BusyTag display refreshed!")
    """
    logger.info("Refreshing BusyTag display...")

    # Step 1: Find the disk identifier
    disk_id = get_disk_identifier(volume_name)
    if not disk_id:
        logger.error(f"✗ Cannot refresh: BusyTag volume '{volume_name}' not found")
        logger.error("  → Is the BusyTag connected?")
        logger.error("  → Check the volume name with: diskutil list")
        return False

    # Step 2: Remount the disk
    if not mount_disk(disk_id):
        logger.error("✗ Refresh failed: Could not remount disk")
        return False

    # Wait to ensure mount completes
    if mount_delay > 0:
        logger.debug(f"Waiting {mount_delay}s for remount to complete...")
        time.sleep(mount_delay)

    # Step 3: Verify the volume is still accessible
    if not verify_mount(volume_name):
        logger.warning("Volume not accessible after remount (may still work)")
        # Don't return False here - the remount may have worked anyway

    logger.info("✓ BusyTag refresh completed")
    return True


def get_volume_path(volume_name: str = "NO NAME") -> Optional[str]:
    """
    Get the full path to a volume if it exists and is mounted.

    Args:
        volume_name: Name of the volume to find

    Returns:
        Full path to the volume (e.g., "/Volumes/NO NAME") or None if not found
    """
    import os
    volume_path = f"/Volumes/{volume_name}"

    if os.path.exists(volume_path):
        return volume_path
    else:
        logger.warning(f"Volume '{volume_name}' not found at {volume_path}")
        return None


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BusyTag Volume Refresh - Test Mode")
    print("=" * 60 + "\n")

    # Test 1: Check if volume exists
    print("Test 1: Checking if BusyTag volume exists...")
    volume_path = get_volume_path("NO NAME")

    if volume_path:
        print(f"✓ BusyTag found at: {volume_path}")

        # Test 2: Get disk identifier
        print("\nTest 2: Finding disk identifier...")
        disk_id = get_disk_identifier("NO NAME")
        if disk_id:
            print(f"✓ Disk identifier: {disk_id}")
        else:
            print("✗ Could not find disk identifier")

        # Test 3: Perform refresh
        print("\nTest 3: Performing remount refresh...")
        user_input = input("Proceed with remount test? (y/n): ")

        if user_input.lower() == 'y':
            success = refresh_busytag(volume_name="NO NAME")

            if success:
                print("\n✓ SUCCESS: BusyTag refresh completed!")
                print("  → The display should update now")
            else:
                print("\n✗ FAILED: Could not complete refresh")
                print("  → Check the log messages above for details")
        else:
            print("\nTest skipped by user")

    else:
        print("✗ BusyTag not found")
        print("\nTroubleshooting:")
        print("  1. Ensure BusyTag is connected via USB")
        print("  2. Check if the volume appears in Finder")
        print("  3. Try running: diskutil list")
        print("  4. Verify the volume name (may be 'BUSYTAG' or 'NO NAME')")

        # Offer to search for alternative volume names
        print("\nSearching for common BusyTag volume names...")
        for alt_name in ["BUSYTAG", "BusyTag", "NO NAME", "NONAME"]:
            if get_volume_path(alt_name):
                print(f"  → Found volume: '{alt_name}'")
                print(f"  → Use: refresh_busytag(volume_name='{alt_name}')")
