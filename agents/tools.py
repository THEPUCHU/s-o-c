import requests
from langchain_core.tools import tool

@tool
def get_ip_info(ip_address: str) -> str:
    """
    Queries a public IP database to find the physical location and ISP of an IP address.
    Use this tool whenever you need to investigate a suspicious IP.
    """
    try:
        # Using a free, no-key-required API for this example
        response = requests.get(f"https://ipapi.co/{ip_address}/json/")
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                return f"Error finding IP: {data.get('reason')}"
            
            city = data.get("city", "Unknown")
            country = data.get("country_name", "Unknown")
            org = data.get("org", "Unknown ISP")
            
            return f"IP {ip_address} is located in {city}, {country}. Registered to ISP: {org}."
        else:
            return "API Error: Could not retrieve data."
    except Exception as e:
        return f"Request failed: {str(e)}"
