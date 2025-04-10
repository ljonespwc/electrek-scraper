# electrek_scraper/utils/proxy_manager.py
import os
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

load_dotenv()

class ProxyManager:
    def __init__(self):
        """Initialize proxy manager with same settings from your working app"""
        self.use_proxy = os.getenv('USE_PROXY') == 'true'
        
        if self.use_proxy:
            # Get the proxy base username and add numbers
            proxy_base = os.getenv('PROXY_USERNAME', 'jlydmftx')
            self.proxy_usernames = []
            for i in range(1, 11):  # Use proxies 1-10
                self.proxy_usernames.append(f"{proxy_base}-{i}")
            
            self.proxy_password = os.getenv('PROXY_PASSWORD')
            print(f"Proxy enabled with {len(self.proxy_usernames)} usernames based on {proxy_base}")
        else:
            self.proxy_usernames = []
            self.proxy_password = None
            print("Proxy usage is disabled")

    def make_request(self, url, method='GET', **kwargs):
        """Make a request using the exact same proxy logic as your working app"""
        last_error = None
        
        # Try with each proxy in sequence
        for attempt, proxy_username in enumerate(self.proxy_usernames if self.use_proxy else [None]):
            try:
                print(f"Making request to {url} (Attempt {attempt+1})")
                
                # Set up proxies exactly as in your working code
                proxies = None
                if self.use_proxy and proxy_username and self.proxy_password:
                    print(f"Using proxy username: {proxy_username}")
                    
                    # Format: {scheme://username:password@proxy:port}
                    proxy_url = f"http://{proxy_username}:{self.proxy_password}@p.webshare.io:80/"
                    proxies = {
                        'http': proxy_url,
                        'https': proxy_url
                    }
                    print(f"Proxy URL created: {proxy_url.replace(self.proxy_password, '****')}")
                
                # Use the proxies directly
                print(f"Making {method} request with proxies: {proxies is not None}")
                
                # Apply kwargs and add proxies if configured
                request_kwargs = kwargs.copy()
                if proxies:
                    request_kwargs['proxies'] = proxies
                
                # Make the request exactly as in your working code
                response = requests.request(method=method, url=url, **request_kwargs)
                
                if response.status_code == 200:
                    print(f"Successfully retrieved with {proxy_username if proxy_username else 'no proxy'}")
                    return response
                else:
                    print(f"Request failed with status code {response.status_code}")
                    # Continue to next proxy
                    
            except Exception as e:
                last_error = e
                print(f"Attempt {attempt+1} failed with proxy {proxy_username}: {str(e)}")
                # Continue to next proxy
        
        # If we get here, all attempts failed
        if self.use_proxy:
            error_msg = f"Failed after trying all {len(self.proxy_usernames)} proxies. Last error: {str(last_error)}"
        else:
            error_msg = f"Failed without proxy: {str(last_error)}"
            
        print(error_msg)
        
        # Try a direct connection as last resort
        if self.use_proxy:
            try:
                print("Trying direct connection as fallback...")
                response = requests.request(method=method, url=url, **kwargs)
                if response.status_code == 200:
                    print("Direct connection successful")
                    return response
            except Exception as e:
                print(f"Direct connection failed: {e}")
                
        return None