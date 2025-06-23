"""
Platform-agnostic timestamp helper for Python
---------------------------------------------
Döndürdüğü değer her zaman:
  • UTC (Zulu)           → "+00:00" veya "Z" takısı
  • ISO-8601 / RFC 3339
  • Millisaniye hassasiyetli
"""

from datetime import datetime, timezone
from typing import Optional
import pytz


def date_now_iso() -> str:
    """
    Return current UTC time in ISO-8601 / RFC 3339 format.
    Works consistently across:
    - Local machine (Windows, macOS, Linux)
    - Docker/WSL containers
    - Remote servers (any Linux distro, PaaS, etc.)
    
    Returns:
        str: UTC timestamp in ISO-8601 format (e.g., "2025-06-22T19:45:30.123+00:00")
    """
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def date_now_unix() -> int:
    """
    Return current UTC timestamp as Unix milliseconds.
    
    Returns:
        int: Unix timestamp in milliseconds
    """
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def date_now_local(timezone_name: str = "Europe/Istanbul") -> str:
    """
    Return local time string for display purposes.
    Format: "2025-06-22 22:45:30 (Turkey Time)"
    
    Args:
        timezone_name: IANA timezone identifier (default: 'Europe/Istanbul')
        
    Returns:
        str: Local time string with timezone
    """
    try:
        tz = pytz.timezone(timezone_name)
        local_time = datetime.now(tz)
        
        # Format: YYYY-MM-DD HH:MM:SS
        time_str = local_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Get timezone abbreviation
        tz_abbr = local_time.strftime("%Z")
        
        return f"{time_str} ({tz_abbr})"
    except Exception as e:
        print(f"Error formatting local time: {e}")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S (Local)")


def format_to_turkey_time(
    iso_string: str, 
    show_seconds: bool = True,
    show_date: bool = True,
    show_timezone: bool = False
) -> str:
    """
    Format UTC ISO string to Turkey timezone for display.
    
    Args:
        iso_string: UTC ISO-8601 string
        show_seconds: Include seconds in time format
        show_date: Include date in output
        show_timezone: Include timezone info
        
    Returns:
        str: Formatted local time
    """
    try:
        # Parse UTC time
        utc_time = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        
        # Convert to Turkey timezone
        turkey_tz = pytz.timezone('Europe/Istanbul')
        turkey_time = utc_time.astimezone(turkey_tz)
        
        result = ""
        
        if show_date:
            result += turkey_time.strftime("%d.%m.%Y ") 
        
        if show_seconds:
            result += turkey_time.strftime("%H:%M:%S")
        else:
            result += turkey_time.strftime("%H:%M")
            
        if show_timezone:
            result += " (Turkey Time)"
            
        return result.strip()
    except Exception as e:
        print(f"Error formatting date: {e}")
        return "--:--"


def is_today_in_turkey(iso_string: str) -> bool:
    """
    Check if a date is today in Turkey timezone.
    
    Args:
        iso_string: UTC ISO-8601 string
        
    Returns:
        bool: True if the date is today in Turkey timezone
    """
    try:
        # Parse UTC time
        utc_time = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        
        # Convert to Turkey timezone
        turkey_tz = pytz.timezone('Europe/Istanbul')
        turkey_time = utc_time.astimezone(turkey_tz)
        turkey_today = datetime.now(turkey_tz)
        
        return turkey_time.date() == turkey_today.date()
    except Exception as e:
        print(f"Error checking if date is today: {e}")
        return False


def get_relative_time(iso_string: str) -> str:
    """
    Get relative time string (e.g., "2 hours ago", "in 30 minutes").
    
    Args:
        iso_string: UTC ISO-8601 string
        
    Returns:
        str: Relative time string in Turkish
    """
    try:
        # Parse UTC time
        target_time = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        diff_seconds = (target_time - now).total_seconds()
        diff_minutes = round(diff_seconds / 60)
        
        if abs(diff_minutes) < 1:
            return "şimdi"
        elif diff_minutes < 0:
            abs_diff = abs(diff_minutes)
            if abs_diff < 60:
                return f"{abs_diff} dakika önce"
            elif abs_diff < 1440:  # 24 hours
                hours = round(abs_diff / 60)
                return f"{hours} saat önce"
            else:
                days = round(abs_diff / 1440)
                return f"{days} gün önce"
        else:
            if diff_minutes < 60:
                return f"{diff_minutes} dakika sonra"
            elif diff_minutes < 1440:  # 24 hours
                hours = round(diff_minutes / 60)
                return f"{hours} saat sonra"
            else:
                days = round(diff_minutes / 1440)
                return f"{days} gün sonra"
    except Exception as e:
        print(f"Error getting relative time: {e}")
        return "bilinmiyor"


def debug_current_time() -> None:
    """Debug helper: Print current time in multiple formats."""
    print("🕐 Current Time Debug (Python):")
    print(f"  UTC ISO-8601: {date_now_iso()}")
    print(f"  Unix timestamp: {date_now_unix()}")
    print(f"  Turkey local: {date_now_local()}")
    print(f"  Turkey formatted: {format_to_turkey_time(date_now_iso())}")


# Example usage and testing
if __name__ == "__main__":
    debug_current_time()
    
    # Test with a sample ISO string
    sample_iso = "2025-06-22T19:45:30.123Z"
    print(f"\n📅 Sample ISO: {sample_iso}")
    print(f"  Turkey format: {format_to_turkey_time(sample_iso)}")
    print(f"  Is today?: {is_today_in_turkey(sample_iso)}")
    print(f"  Relative: {get_relative_time(sample_iso)}")
