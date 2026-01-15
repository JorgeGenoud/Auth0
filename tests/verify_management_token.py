import os
import requests
from dotenv import load_dotenv

# 1. Cargar variables del archivo .env
load_dotenv() 

# 2. Obtener las credenciales
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUDIENCE = os.getenv('AUTH0_API_AUDIENCE')

def get_management_token():
    print("--- Verificando obtención de Token de Management API ---")
    
    # Validación simple
    missing = []
    if not AUTH0_DOMAIN: missing.append("AUTH0_DOMAIN")
    if not CLIENT_ID: missing.append("AUTH0_CLIENT_ID")
    if not CLIENT_SECRET: missing.append("AUTH0_CLIENT_SECRET")
    if not AUDIENCE: missing.append("AUTH0_API_AUDIENCE")
    
    if missing:
        print(f"❌ Faltan variables en el archivo .env: {', '.join(missing)}")
        return

    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": AUDIENCE, 
        "grant_type": "client_credentials"
    }
    
    headers = {'content-type': "application/json"}

    try:
        print(f"Solicitando token a: {url}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        token = data.get('access_token')
        
        if token:
            print("✅ Token de Management API obtenido exitosamente.")
            print(f"Token (primeros 20 cars): {token[:20]}...")
            return token
        else:
             print("❌ La respuesta no contenía un 'access_token'")
             print(data)
        
    except requests.exceptions.HTTPError as err:
        print(f"❌ Error HTTP: {err}")
        try:
            print(f"Detalle: {response.text}")
        except: pass
    except Exception as err:
        print(f"❌ Error: {err}")

if __name__ == "__main__":
    get_management_token()
