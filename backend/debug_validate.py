import requests
import sys

def debug_validate(ip, port, p_type):
    proxy_url = f"{p_type}://{ip}:{port}"
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    print(f"Testing {proxy_url}...")
    try:
        response = requests.get(
            'http://httpbin.org/ip',
            proxies=proxies,
            timeout=10
        )
        print(f"Success! Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed! Error: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        # Defaults for a known speedx socks5 list if possible or just use what we have
        # Let's try to pick one from the GeoNode list if we had it
        print("Usage: python debug_validate.py <ip> <port> <type>")
        sys.exit(1)
    
    debug_validate(sys.argv[1], sys.argv[2], sys.argv[3])
