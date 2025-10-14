import pytest
from httpx import AsyncClient


class TestBoardCreate:
    """Tests de creación de boards"""

    @pytest.mark.asyncio
    async def test_create_board_success(self, client: AsyncClient, auth_headers):
        """Crear board exitosamente"""
        board_data = {
            "title": "Mi Tablero de Prueba",
            "description": "Descripción del tablero"
        }

        response = await client.post(
            "/api/v1/boards/",
            json=board_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == board_data["title"]
        assert data["description"] == board_data["description"]
        assert "id" in data
        assert "owner_id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_board_without_description(self, client: AsyncClient, auth_headers):
        """Crear board sin descripción"""
        board_data = {"title": "Tablero Sin Descripción"}

        response = await client.post(
            "/api/v1/boards/",
            json=board_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        assert response.json()["description"] is None

    @pytest.mark.asyncio
    async def test_create_board_unauthorized(self, client: AsyncClient):
        """Crear board sin autenticación"""
        board_data = {"title": "Tablero"}

        response = await client.post("/api/v1/boards/", json=board_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_board_empty_title(self, client: AsyncClient, auth_headers):
        """Título vacío no permitido"""
        board_data = {"title": ""}

        response = await client.post(
            "/api/v1/boards/",
            json=board_data,
            headers=auth_headers
        )

        assert response.status_code == 422


class TestBoardList:
    """Tests de listado de boards"""

    @pytest.mark.asyncio
    async def test_list_boards_empty(self, client: AsyncClient, auth_headers):
        """Listar boards vacío"""
        response = await client.get("/api/v1/boards/", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_boards_with_data(self, client: AsyncClient, auth_headers):
        """Listar boards con datos"""
        # Crear 3 boards
        for i in range(3):
            await client.post(
                "/api/v1/boards/",
                json={"title": f"Tablero {i}"},
                headers=auth_headers
            )

        response = await client.get("/api/v1/boards/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_list_boards_only_own(self, client: AsyncClient, auth_headers, second_auth_headers):
        """Solo ver propios boards"""
        # Usuario 1 crea board
        await client.post(
            "/api/v1/boards/",
            json={"title": "Board Usuario 1"},
            headers=auth_headers
        )

        # Usuario 2 crea board
        await client.post(
            "/api/v1/boards/",
            json={"title": "Board Usuario 2"},
            headers=second_auth_headers
        )

        # Usuario 1 solo ve su board
        response = await client.get("/api/v1/boards/", headers=auth_headers)
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Board Usuario 1"

    @pytest.mark.asyncio
    async def test_list_boards_pagination(self, client: AsyncClient, auth_headers):
        """Paginación de boards"""
        # Crear 15 boards
        for i in range(15):
            await client.post(
                "/api/v1/boards/",
                json={"title": f"Board {i}"},
                headers=auth_headers
            )

        # Primera página
        response = await client.get("/api/v1/boards/?skip=0&limit=10", headers=auth_headers)
        assert len(response.json()) == 10

        # Segunda página
        response = await client.get("/api/v1/boards/?skip=10&limit=10", headers=auth_headers)
        assert len(response.json()) == 5


class TestBoardDetail:
    """Tests de detalle de board"""

    @pytest.mark.asyncio
    async def test_get_board_success(self, client: AsyncClient, auth_headers):
        """Obtener board existente"""
        # Crear board
        create_response = await client.post(
            "/api/v1/boards/",
            json={"title": "Mi Tablero"},
            headers=auth_headers
        )
        board_id = create_response.json()["id"]

        # Obtener board
        response = await client.get(f"/api/v1/boards/{board_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == board_id
        assert data["title"] == "Mi Tablero"

    @pytest.mark.asyncio
    async def test_get_board_not_found(self, client: AsyncClient, auth_headers):
        """Board no existe"""
        response = await client.get("/api/v1/boards/99999", headers=auth_headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_board_no_permission(self, client: AsyncClient, auth_headers, second_auth_headers):
        """No puede ver board de otro usuario"""
        # Usuario 1 crea board
        create_response = await client.post(
            "/api/v1/boards/",
            json={"title": "Board Privado"},
            headers=auth_headers
        )
        board_id = create_response.json()["id"]

        # Usuario 2 intenta acceder
        response = await client.get(
            f"/api/v1/boards/{board_id}",
            headers=second_auth_headers
        )

        assert response.status_code == 403


class TestBoardUpdate:
    """Tests de actualización de board"""

    @pytest.mark.asyncio
    async def test_update_board_success(self, client: AsyncClient, auth_headers):
        """Actualizar board exitosamente"""
        # Crear board
        create_response = await client.post(
            "/api/v1/boards/",
            json={"title": "Título Original"},
            headers=auth_headers
        )
        board_id = create_response.json()["id"]

        # Actualizar
        update_data = {
            "title": "Título Actualizado",
            "description": "Nueva descripción"
        }
        response = await client.put(
            f"/api/v1/boards/{board_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_board_partial(self, client: AsyncClient, auth_headers):
        """Actualización parcial"""
        # Crear board
        create_response = await client.post(
            "/api/v1/boards/",
            json={"title": "Original", "description": "Desc Original"},
            headers=auth_headers
        )
        board_id = create_response.json()["id"]

        # Actualizar solo título
        response = await client.put(
            f"/api/v1/boards/{board_id}",
            json={"title": "Nuevo Título"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Nuevo Título"
        assert data["description"] == "Desc Original"


class TestBoardDelete:
    """Tests de eliminación de board"""

    @pytest.mark.asyncio
    async def test_delete_board_success(self, client: AsyncClient, auth_headers):
        """Eliminar board exitosamente"""
        # Crear board
        create_response = await client.post(
            "/api/v1/boards/",
            json={"title": "Board a Eliminar"},
            headers=auth_headers
        )
        board_id = create_response.json()["id"]

        # Eliminar
        response = await client.delete(
            f"/api/v1/boards/{board_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar que no existe
        get_response = await client.get(
            f"/api/v1/boards/{board_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_board_no_permission(self, client: AsyncClient, auth_headers, second_auth_headers):
        """No puede eliminar board de otro usuario"""
        # Usuario 1 crea board
        create_response = await client.post(
            "/api/v1/boards/",
            json={"title": "Board"},
            headers=auth_headers
        )
        board_id = create_response.json()["id"]

        # Usuario 2 intenta eliminar
        response = await client.delete(
            f"/api/v1/boards/{board_id}",
            headers=second_auth_headers
        )

        assert response.status_code == 403
