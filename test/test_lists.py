import pytest
from httpx import AsyncClient


@pytest.fixture
async def board(client: AsyncClient, auth_headers):
    """Board fixture para tests de listas"""
    response = await client.post(
        "/api/v1/boards/",
        json={"title": "Board Test"},
        headers=auth_headers
    )
    return response.json()


class TestListCreate:
    """Tests de creación de listas"""

    @pytest.mark.asyncio
    async def test_create_list_success(self, client: AsyncClient, auth_headers, board):
        """Crear lista exitosamente"""
        list_data = {
            "title": "Pendiente",
            "position": 0,
            "board_id": board["id"]
        }

        response = await client.post(
            "/api/v1/lists/",
            json=list_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == list_data["title"]
        assert data["position"] == list_data["position"]
        assert data["board_id"] == board["id"]

    @pytest.mark.asyncio
    async def test_create_list_invalid_board(self, client: AsyncClient, auth_headers):
        """Board no existe"""
        list_data = {
            "title": "Lista",
            "position": 0,
            "board_id": 99999
        }

        response = await client.post(
            "/api/v1/lists/",
            json=list_data,
            headers=auth_headers
        )

        assert response.status_code == 404


class TestListOperations:
    """Tests de operaciones con listas"""

    @pytest.mark.asyncio
    async def test_list_lists_by_board(self, client: AsyncClient, auth_headers, board):
        """Listar listas de un board"""
        # Crear 3 listas
        for i in range(3):
            await client.post(
                "/api/v1/lists/",
                json={"title": f"Lista {i}", "position": i, "board_id": board["id"]},
                headers=auth_headers
            )

        response = await client.get(
            f"/api/v1/lists/board/{board['id']}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_update_list(self, client: AsyncClient, auth_headers, board):
        """Actualizar lista"""
        # Crear lista
        create_response = await client.post(
            "/api/v1/lists/",
            json={"title": "Original", "position": 0, "board_id": board["id"]},
            headers=auth_headers
        )
        list_id = create_response.json()["id"]

        # Actualizar
        response = await client.put(
            f"/api/v1/lists/{list_id}",
            json={"title": "Actualizado"},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Actualizado"

    @pytest.mark.asyncio
    async def test_delete_list(self, client: AsyncClient, auth_headers, board):
        """Eliminar lista"""
        # Crear lista
        create_response = await client.post(
            "/api/v1/lists/",
            json={"title": "Lista", "position": 0, "board_id": board["id"]},
            headers=auth_headers
        )
        list_id = create_response.json()["id"]

        # Eliminar
        response = await client.delete(
            f"/api/v1/lists/{list_id}",
            headers=auth_headers
        )

        assert response.status_code == 204