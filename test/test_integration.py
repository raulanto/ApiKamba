import pytest
from httpx import AsyncClient


class TestCompleteKanbanFlow:
    """Test de flujo completo de Kanban"""

    @pytest.mark.asyncio
    async def test_complete_kanban_workflow(self, client: AsyncClient):
        """Flujo completo: registro, login, crear board, listas, tareas y moverlas"""

        # 1. Registrar usuario
        user_data = {
            "email": "workflow@example.com",
            "username": "workflowuser",
            "password": "Test1234"
        }
        register_response = await client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201

        # 2. Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Crear board
        board_response = await client.post(
            "/api/v1/boards/",
            json={"title": "Proyecto Personal", "description": "Mi proyecto"},
            headers=headers
        )
        assert board_response.status_code == 201
        board_id = board_response.json()["id"]

        # 4. Crear listas
        lists = []
        for i, title in enumerate(["Pendiente", "En Progreso", "Terminado"]):
            list_response = await client.post(
                "/api/v1/lists/",
                json={"title": title, "position": i, "board_id": board_id},
                headers=headers
            )
            assert list_response.status_code == 201
            lists.append(list_response.json())

        # 5. Crear tareas en "Pendiente"
        task1_response = await client.post(
            "/api/v1/tasks/",
            json={
                "title": "Implementar login",
                "description": "Sistema de autenticación",
                "priority": "high",
                "list_id": lists[0]["id"]
            },
            headers=headers
        )
        assert task1_response.status_code == 201
        task1_id = task1_response.json()["id"]

        task2_response = await client.post(
            "/api/v1/tasks/",
            json={
                "title": "Diseñar UI",
                "priority": "medium",
                "list_id": lists[0]["id"]
            },
            headers=headers
        )
        assert task2_response.status_code == 201

        # 6. Mover tarea a "En Progreso"
        move_response = await client.post(
            f"/api/v1/tasks/{task1_id}/move",
            json={"list_id": lists[1]["id"]},
            headers=headers
        )
        assert move_response.status_code == 200
        assert move_response.json()["list_id"] == lists[1]["id"]

        # 7. Actualizar tarea
        update_response = await client.put(
            f"/api/v1/tasks/{task1_id}",
            json={"description": "Autenticación con JWT completada"},
            headers=headers
        )
        assert update_response.status_code == 200

        # 8. Mover tarea a "Terminado"
        final_move = await client.post(
            f"/api/v1/tasks/{task1_id}/move",
            json={"list_id": lists[2]["id"]},
            headers=headers
        )
        assert final_move.status_code == 200

        # 9. Verificar board con todas las listas y tareas
        board_detail = await client.get(f"/api/v1/boards/{board_id}", headers=headers)
        assert board_detail.status_code == 200

        # 10. Listar tareas de "Terminado"
        completed_tasks = await client.get(
            f"/api/v1/tasks/list/{lists[2]['id']}",
            headers=headers
        )
        assert completed_tasks.status_code == 200
        assert len(completed_tasks.json()) == 1

