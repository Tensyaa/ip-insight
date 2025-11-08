# Script to fetch and display IP address information using ipapi.co
import requests
from typing import Optional, Dict
import sys
import json


def get_ip_info() -> Optional[Dict]:

    # Fetch IP address information from ipapi.co
    # Returns:    Dict with IP information or None if the request fails

    try:
        # Make request to ipapi.co with proper headers
        headers = {"User-Agent": "IPInfoApp/1.0", "Accept": "application/json"}
        response = requests.get("https://ipapi.co/json/", headers=headers, timeout=5)

        # Check for rate limiting
        if response.status_code == 429:
            print("Error: Rate limit reached. Please wait before trying again.")
            return None

        response.raise_for_status()  # Raises an exception for other 4XX/5XX status codes

        # Parse the JSON data
        data = response.json()

        # Verify we got valid data (ipapi.co returns error field if there's an issue)
        if "error" in data:
            print(f"API Error: {data.get('reason', 'Unknown error')}")
            return None

        return data

    except requests.Timeout:
        print("Error: Request timed out. Please check your internet connection.")
        return None
    except requests.RequestException as e:
        print(f"Error fetching IP information: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Received invalid JSON response")
        return None


def main():
    # Fetch IP information
    ip_info = get_ip_info()

    if not ip_info:
        print("Failed to retrieve IP information")
        sys.exit(1)

    # Print information with consistent formatting
    print("\n=== IP Address Information ===")
    print(f"IP Address : {ip_info.get('ip', 'Unknown')}")
    print(f"City      : {ip_info.get('city', 'Unknown')}")
    print(f"Country   : {ip_info.get('country', 'Unknown')}")
    print(f"ISP       : {ip_info.get('org', 'Unknown')}")
    print(f"ASN       : {ip_info.get('asn', 'Unknown')}")
    print("===========================\n")


if __name__ == "__main__":
    main()
