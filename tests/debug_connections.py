import sys
import os
import requests

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from auth.providers.auth0 import Auth0Provider

def list_connections():
    print("--- Debugging Auth0 Connections ---")
    
    provider = Auth0Provider()
    token = provider.get_token()
    
    if not token:
        print("❌ Could not obtain Management Token. Check your .env credentials.")
        return

    print("✅ Management Token obtained.")
    
    url = f"https://{settings.auth0_domain}/api/v2/connections"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        connections = response.json()
        
        print(f"\nFound {len(connections)} connections:")
        print("-" * 50)
        
        db_connection_found = False
        
        for conn in connections:
            print(f"Name: {conn['name']}")
            print(f"Strategy: {conn['strategy']}")
            print(f"ID: {conn['id']}")
            print("-" * 20)
            
            if conn['strategy'] == 'auth0':
                db_connection_found = True
                print(f"👉 POSSIBLE TARGET: This is a Database connection.")
                if conn['name'] == 'Username-Password-Authentication':
                    print("   (Matches default configuration)")
                else:
                    print(f"   ⚠️ DOES NOT MATCH default 'Username-Password-Authentication'.")
                    print(f"   Update 'connection' parameter in your code to: '{conn['name']}'")
            print("-" * 50)
            
        if not db_connection_found:
             print("❌ No Database connection (strategy='auth0') found!")
             
    except Exception as e:
        print(f"❌ Error fetching connections: {e}")

if __name__ == "__main__":
    list_connections()
