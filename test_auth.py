# test_auth.py
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("🧪 Probando autenticación...")

# 1. Registrar usuario
print("\n1. Registrando usuario...")
register_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test1234"
}

try:
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 201:
        print(f"✅ Usuario registrado: {response.json()}")
    elif response.status_code == 409:
        print("ℹ️ Usuario ya existe, continuando...")
    else:
        print(f"❌ Error al registrar: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. Login
print("\n2. Haciendo login...")
login_data = {
    "username": "test@example.com",  # OAuth2 usa 'username'
    "password": "Test1234"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"✅ Token obtenido: {access_token[:30]}...")

        # 3. Probar /me
        print("\n3. Probando /me...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

        if response.status_code == 200:
            print(f"✅ Usuario actual: {response.json()}")
        else:
            print(f"❌ Error en /me: {response.status_code} - {response.text}")
    else:
        print(f"❌ Error al hacer login: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")