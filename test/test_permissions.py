import pytest
from httpx import AsyncClient


class TestPermissions:
    """Tests de permisos y autorización"""

    @pytest.mark.asyncio
    async def test_cannot_access_other_user_board(
            self, client: AsyncClient, auth_headers, second_auth_headers
    ):
        """No puede acceder a board de otro usuario"""
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

    @pytest.mark.asyncio
    async def test_cannot_create_list_in_other_user_board(
            self, client: AsyncClient, auth_headers, second_auth_headers
    ):
        """No puede crear lista en board de otro usuario"""
        # Usuario 1 crea board
        create_response = await client.post(
            "/api/v1/boards/",
            json={"title": "Board"},
            headers=auth_headers
        )
        board_id = create_response.json()["id"]

        # Usuario 2 intenta crear lista
        response = await client.post(
            "/api/v1/lists/",
            json={"title": "Lista", "position": 0, "board_id": board_id},
            headers=second_auth_headers
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_cannot_move_task_to_other_user_list(
            self, client: AsyncClient, auth_headers, second_auth_headers, board
    ):
        """No puede mover tarea a lista de otro usuario"""
        # Usuario 1 crea lista y tarea
        list1_response = await client.post(
            "/api/v1/lists/",
            json={"title": "Lista 1", "position": 0, "board_id": board["id"]},
            headers=auth_headers
        )
        list1_id = list1_response.json()["id"]

        task_response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Tarea", "list_id": list1_id},
            headers=auth_headers
        )
        task_id = task_response.json()["id"]

        # Usuario 2 crea su propio board y lista
        board2_response = await client.post(
            "/api/v1/boards/",
            json={"title": "Board 2"},
            headers=second_auth_headers
        )
        list2_response = await client.post(
            "/api/v1/lists/",
            json={"title": "Lista 2", "position": 0, "board_id": board2_response.json()["id"]},
            headers=second_auth_headers
        )
        list2_id = list2_response.json()["id"]

        # Usuario 1 intenta mover su tarea a lista de Usuario 2
        response = await client.post(
            f"/api/v1/tasks/{task_id}/move",
            json={"list_id": list2_id},
            headers=auth_headers
        )

        assert response.status_code == 403

