import pytest
from httpx import AsyncClient


@pytest.fixture
async def list_fixture(client: AsyncClient, auth_headers, board):
    """Lista fixture para tests de tareas"""
    response = await client.post(
        "/api/v1/lists/",
        json={"title": "Pendiente", "position": 0, "board_id": board["id"]},
        headers=auth_headers
    )
    return response.json()


@pytest.fixture
async def second_list(client: AsyncClient, auth_headers, board):
    """Segunda lista para tests de mover tareas"""
    response = await client.post(
        "/api/v1/lists/",
        json={"title": "En Progreso", "position": 1, "board_id": board["id"]},
        headers=auth_headers
    )
    return response.json()


class TestTaskCreate:
    """Tests de creación de tareas"""

    @pytest.mark.asyncio
    async def test_create_task_success(self, client: AsyncClient, auth_headers, list_fixture):
        """Crear tarea exitosamente"""
        task_data = {
            "title": "Mi primera tarea",
            "description": "Descripción de la tarea",
            "priority": "high",
            "position": 0,
            "list_id": list_fixture["id"]
        }

        response = await client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["priority"] == task_data["priority"]
        assert data["list_id"] == list_fixture["id"]

    @pytest.mark.asyncio
    async def test_create_task_minimal(self, client: AsyncClient, auth_headers, list_fixture):
        """Crear tarea con campos mínimos"""
        task_data = {
            "title": "Tarea simple",
            "list_id": list_fixture["id"]
        }

        response = await client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["priority"] == "medium"  # Default


class TestTaskOperations:
    """Tests de operaciones con tareas"""

    @pytest.mark.asyncio
    async def test_list_tasks_by_list(self, client: AsyncClient, auth_headers, list_fixture):
        """Listar tareas de una lista"""
        # Crear 5 tareas
        for i in range(5):
            await client.post(
                "/api/v1/tasks/",
                json={"title": f"Tarea {i}", "list_id": list_fixture["id"]},
                headers=auth_headers
            )

        response = await client.get(
            f"/api/v1/tasks/list/{list_fixture['id']}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_get_task_detail(self, client: AsyncClient, auth_headers, list_fixture):
        """Obtener detalle de tarea"""
        # Crear tarea
        create_response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Tarea Detalle", "list_id": list_fixture["id"]},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Obtener detalle
        response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Tarea Detalle"

    @pytest.mark.asyncio
    async def test_update_task(self, client: AsyncClient, auth_headers, list_fixture):
        """Actualizar tarea"""
        # Crear tarea
        create_response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Original", "priority": "low", "list_id": list_fixture["id"]},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Actualizar
        update_data = {
            "title": "Actualizado",
            "priority": "urgent",
            "description": "Nueva descripción"
        }
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["priority"] == update_data["priority"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_delete_task(self, client: AsyncClient, auth_headers, list_fixture):
        """Eliminar tarea"""
        # Crear tarea
        create_response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Tarea a Eliminar", "list_id": list_fixture["id"]},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Eliminar
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar eliminación
        get_response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


class TestTaskMove:
    """Tests de mover tareas entre listas"""

    @pytest.mark.asyncio
    async def test_move_task_success(self, client: AsyncClient, auth_headers, list_fixture, second_list):
        """Mover tarea exitosamente"""
        # Crear tarea en primera lista
        create_response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Tarea a Mover", "list_id": list_fixture["id"]},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Mover a segunda lista
        response = await client.post(
            f"/api/v1/tasks/{task_id}/move",
            json={"list_id": second_list["id"]},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["list_id"] == second_list["id"]

    @pytest.mark.asyncio
    async def test_move_task_with_position(self, client: AsyncClient, auth_headers, list_fixture, second_list):
        """Mover tarea con posición específica"""
        # Crear tarea
        create_response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Tarea", "list_id": list_fixture["id"]},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Mover con posición
        response = await client.post(
            f"/api/v1/tasks/{task_id}/move",
            json={"list_id": second_list["id"], "position": 5},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["list_id"] == second_list["id"]
        assert data["position"] == 5

    @pytest.mark.asyncio
    async def test_move_task_to_invalid_list(self, client: AsyncClient, auth_headers, list_fixture):
        """No se puede mover a lista inexistente"""
        # Crear tarea
        create_response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Tarea", "list_id": list_fixture["id"]},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Intentar mover a lista inexistente
        response = await client.post(
            f"/api/v1/tasks/{task_id}/move",
            json={"list_id": 99999},
            headers=auth_headers
        )

        assert response.status_code == 404