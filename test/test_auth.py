import pytest
from httpx import AsyncClient


class TestUserRegistration:
    """Tests de registro de usuarios"""

    @pytest.mark.asyncio
    async def test_register_user_success(self, client: AsyncClient):
        """Registro exitoso de usuario"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "Test1234"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, registered_user):
        """No permitir email duplicado"""
        user_data = {
            "email": registered_user["email"],
            "username": "different_username",
            "password": "Test1234"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, registered_user):
        """No permitir username duplicado"""
        user_data = {
            "email": "different@example.com",
            "username": registered_user["username"],
            "password": "Test1234"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 409
        assert "already taken" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Email inválido"""
        user_data = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "Test1234"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Password débil"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_username(self, client: AsyncClient):
        """Username muy corto"""
        user_data = {
            "email": "test@example.com",
            "username": "ab",
            "password": "Test1234"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422


class TestUserLogin:
    """Tests de login"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, user_data, registered_user):
        """Login exitoso"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, registered_user):
        """Login con password incorrecto"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": registered_user["email"],
                "password": "WrongPassword123"
            }
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Login con usuario inexistente"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "Test1234"
            }
        )

        assert response.status_code == 401


class TestCurrentUser:
    """Tests de obtener usuario actual"""

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers, registered_user):
        """Obtener usuario actual"""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == registered_user["email"]
        assert data["username"] == registered_user["username"]
        assert data["id"] == registered_user["id"]

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Sin token"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401


class TestRefreshToken:
    """Tests de refresh token"""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, user_data, registered_user):
        """Refresh token exitoso"""
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Refresh token inválido"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token(self, client: AsyncClient, user_data, registered_user):
        """No se puede usar access token como refresh token"""
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )
        access_token = login_response.json()["access_token"]

        # Intentar refresh con access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token}
        )

        assert response.status_code == 401