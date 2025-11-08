import requests
from typing import Optional, Dict
import json
from flask import Flask, jsonify, request

# Initialize the Flask app
app = Flask(__name__)

def is_private_ip(ip: str) -> bool:
    """
    Check if an IP address is private/reserved.
    """
    # Common private IP patterns
    private_patterns = [
        '10.',
        '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.',
        '172.24.', '172.25.', '172.26.', '172.27.',
        '172.28.', '172.29.', '172.30.', '172.31.',
        '192.168.',
        '127.',
        'localhost'
    ]
    return any(ip.startswith(pattern) for pattern in private_patterns)

def get_visitor_ip() -> str:
    """
    Gets the visitor's real IP address from the request headers.
    Handles common proxy headers and private IPs.
    """
    # Check for X-Forwarded-For (set by most proxies)
    if 'X-Forwarded-For' in request.headers:
        # The header can contain a comma-separated list, the first one is the client
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        # Fallback to the remote address
        ip = request.remote_addr
    
    # For development/testing: if we detect a private IP, use a default public one
    if is_private_ip(ip):
        return '8.8.8.8'  # Google's public DNS IP for testing
        
    return ip

def get_ip_info(ip_address: str) -> Optional[Dict]:
    """
    Fetch IP address information from ipapi.co for a *specific* IP.
    
    Args:
        ip_address: The IP address to look up.

    Returns:
        Dict with IP information or None if the request fails.
    """
    
    # Use the API's ability to look up a specific IP
    url = f"https://ipapi.co/{ip_address}/json/"
    
    try:
        headers = {
            'User-Agent': 'IPInfoApp/1.0 (Web Service)',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 429:
            print("Error: Rate limit reached.")
            return {"error": "Rate limit reached. Please wait."}
            
        response.raise_for_status()  # Raises an exception for 4XX/5XX
        
        data = response.json()
        
        if 'error' in data:
            print(f"API Error: {data.get('reason', 'Unknown error')}")
            return {"error": data.get('reason', 'Unknown error')}
            
        return data
        
    except requests.Timeout:
        print("Error: Request timed out.")
        return {"error": "Request to IP API timed out."}
    except requests.RequestException as e:
        print(f"Error fetching IP information: {e}")
        return {"error": f"Could not fetch IP data: {e}"}
    except json.JSONDecodeError:
        print("Error: Received invalid JSON response")
        return {"error": "Received invalid response from IP API."}

@app.route('/')
def main_route():
    """
    Main web route. Fetches visitor IP and returns info as JSON.
    """
    # 1. Get the visitor's IP address
    visitor_ip = get_visitor_ip()
    original_ip = request.remote_addr  # Keep track of original IP for logging
    
    if not visitor_ip:
        return jsonify({"error": "Could not determine client IP address."}), 400

    # 2. Get the info for that IP
    ip_info = get_ip_info(visitor_ip)
    
    # Log whether we're using a test IP due to private IP detection
    if is_private_ip(original_ip):
        print(f"Note: Using test IP {visitor_ip} instead of private IP {original_ip}")
    
    if not ip_info or 'error' in ip_info:
        return jsonify({"error": "Using test IP for local development", 
                       "original_ip": original_ip,
                       "test_ip": visitor_ip}), 200  # Return 200 for development

    # 3. Return the info as a JSON response
    # We filter to show only the relevant fields
    filtered_info = {
        "ip": ip_info.get('ip'),
        "city": ip_info.get('city'),
        "country_name": ip_info.get('country_name'),
        "isp": ip_info.get('org'),
        "asn": ip_info.get('asn'),
        "latitude": ip_info.get('latitude'),
        "longitude": ip_info.get('longitude')
    }
    
    return jsonify(filtered_info)

if __name__ == "__main__":
    # Run the app in debug mode for local testing
    # In production, this is run by Gunicorn (see Dockerfile)
    app.run(debug=True, host='0.0.0.0', port=5000)