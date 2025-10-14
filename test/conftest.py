# tests/conftest.py
import asyncio
from typing import AsyncGenerator, Dict

import pytest
from faker import Faker
from httpx import AsyncClient, ASGITransport  # ← Agregar ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app

# Base de datos de test
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

fake = Faker()


@pytest.fixture(scope="session")
def event_loop():
    """Crear event loop para toda la sesión de tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Crear engine de base de datos para tests"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False}
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Sesión de base de datos para cada test"""
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP para tests"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # ✅ CORRECCIÓN: Usar ASGITransport en lugar de app directamente
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def user_data() -> Dict[str, str]:
    """Datos de usuario para tests"""
    return {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": "Test1234"
    }


@pytest.fixture
async def registered_user(client: AsyncClient, user_data: Dict) -> Dict:
    """Usuario registrado"""
    response = await client.post("/api/v1/auth/register", json=user_data)
    return {**user_data, **response.json()}


@pytest.fixture
async def auth_headers(client: AsyncClient, user_data: Dict, registered_user: Dict) -> Dict:
    """Headers con token de autenticación"""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def second_user(client: AsyncClient) -> Dict:
    """Segundo usuario para tests de permisos"""
    user_data = {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": "Test1234"
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    return {**user_data, **response.json()}


@pytest.fixture
async def second_auth_headers(client: AsyncClient, second_user: Dict) -> Dict:
    """Headers del segundo usuario"""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": second_user["email"], "password": second_user["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Agregar al final de conftest.py

@pytest.fixture
async def board(client: AsyncClient, auth_headers: Dict) -> Dict:
    """Board fixture para tests de listas"""
    response = await client.post(
        "/api/v1/boards/",
        json={"title": "Board Test"},
        headers=auth_headers
    )
    return response.json()


@pytest.fixture
async def list_fixture(client: AsyncClient, auth_headers: Dict, board: Dict) -> Dict:
    """Lista fixture para tests de tareas"""
    response = await client.post(
        "/api/v1/lists/",
        json={"title": "Pendiente", "position": 0, "board_id": board["id"]},
        headers=auth_headers
    )
    return response.json()


@pytest.fixture
async def second_list(client: AsyncClient, auth_headers: Dict, board: Dict) -> Dict:
    """Segunda lista para tests de mover tareas"""
    response = await client.post(
        "/api/v1/lists/",
        json={"title": "En Progreso", "position": 1, "board_id": board["id"]},
        headers=auth_headers
    )
    return response.json()
