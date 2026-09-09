import json

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_cleaning_service,
    get_map_store,
    get_session_history,
)
from app.api.main import app


@pytest.fixture
def client(map_store, session_history, cleaning_service):
    app.dependency_overrides[get_map_store] = lambda: map_store
    app.dependency_overrides[get_session_history] = lambda: session_history
    app.dependency_overrides[get_cleaning_service] = lambda: cleaning_service
    # raise_server_exceptions=False so the app's exception handler turns domain
    # errors into HTTP responses instead of the client re-raising them.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# same as sample_23_map fixture --> for http
_JSON_MAP_23 = json.dumps(
    {
        "rows": 2,
        "cols": 3,
        "tiles": [
            {"x": 0, "y": 0, "walkable": True, "dirty": True},
            {"x": 1, "y": 0, "walkable": True, "dirty": False},
            {"x": 2, "y": 0, "walkable": False, "dirty": False},
            {"x": 0, "y": 1, "walkable": True, "dirty": True},
            {"x": 1, "y": 1, "walkable": True, "dirty": True},
            {"x": 2, "y": 1, "walkable": True, "dirty": True},
        ],
    }
).encode()


def _upload_map(client: TestClient, filename: str, content: bytes):
    return client.put("/map", files={"file": (filename, content)})


def _clean(client: TestClient, **payload):
    return client.post("/clean", json=payload)


class TestHttp:
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}


class TestHappyPath:
    def test_json_map_upload_then_clean(self, client: TestClient):
        upload = _upload_map(client, "map.json", _JSON_MAP_23)
        assert upload.status_code == status.HTTP_200_OK
        assert upload.json() == {"rows": 2, "cols": 3, "walkable_tiles": 5}

        response = _clean(
            client,
            start={"x": 0, "y": 0},
            robot_model="basic",
            actions=[
                {"direction": "south", "steps": 1},
                {"direction": "east", "steps": 2},
            ],
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["state"] == "completed"
        assert body["error"] is None
        assert body["final_position"] == {"x": 2, "y": 1}
        assert body["cleaned_tiles"] == [
            {"x": 0, "y": 0},
            {"x": 0, "y": 1},
            {"x": 1, "y": 1},
            {"x": 2, "y": 1},
        ]

    def test_txt_map_upload_then_clean(self, client: TestClient):
        # 'o' tiles are walkable + dirty; proves the .txt loader path is wired.
        upload = _upload_map(client, "map.txt", b"oo\noo")
        assert upload.status_code == status.HTTP_200_OK

        response = _clean(
            client,
            start={"x": 0, "y": 0},
            robot_model="basic",
            actions=[
                {"direction": "east", "steps": 1},
                {"direction": "south", "steps": 1},
            ],
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["state"] == "completed"
        assert body["cleaned_tiles"] == [
            {"x": 0, "y": 0},
            {"x": 1, "y": 0},
            {"x": 1, "y": 1},
        ]


class TestCollision:
    def test_obstacle_collision_returns_409(self, client: TestClient):
        _upload_map(client, "map.json", _JSON_MAP_23)

        response = _clean(
            client,
            start={"x": 0, "y": 0},
            robot_model="basic",
            actions=[
                {"direction": "east", "steps": 2},  # (2,0) is an obstacle
                {"direction": "south", "steps": 1},
            ],
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        body = response.json()
        assert body["state"] == "error"
        assert body["error"]["code"] == "collision"
        assert body["error"]["position"] == {"x": 2, "y": 0}  # blocked target
        assert body["final_position"] == {"x": 1, "y": 0}  # last valid position
        assert body["cleaned_tiles"] == [{"x": 0, "y": 0}, {"x": 1, "y": 0}]


class TestEdgeCases:
    def test_clean_without_map_returns_409(self, client: TestClient):
        response = _clean(
            client,
            start={"x": 0, "y": 0},
            robot_model="basic",
            actions=[],
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_invalid_start_returns_422(self, client: TestClient):
        _upload_map(client, "map.json", _JSON_MAP_23)

        response = _clean(
            client,
            start={"x": 9, "y": 9},  # out of bounds
            robot_model="basic",
            actions=[],
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unsupported_map_format_returns_415(self, client: TestClient):
        response = _upload_map(client, "map.csv", b"0,1,2")

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


class TestHistory:
    _CSV_HEADERS = [  # noqa: RUF012
        "id",
        "started_at",
        "state",
        "robot_model",
        "submitted_actions",
        "successful_steps",
        "cleaned_tiles",
        "duration_ms",
    ]

    def test_completed_run_is_recorded_in_history(self, client: TestClient):
        _upload_map(client, "map.json", _JSON_MAP_23)
        _clean(
            client,
            start={"x": 0, "y": 0},
            robot_model="basic",
            actions=[{"direction": "south", "steps": 1}],
        )

        history = client.get("/history")

        assert history.status_code == status.HTTP_200_OK
        assert history.headers["content-type"].startswith("text/csv")
        rows = [line for line in history.text.splitlines() if line]
        assert len(rows) == 2  # header + the single recorded run
        assert "completed" in rows[1]
        assert "basic" in rows[1]

    def test_completed_multiple_runs_in_history(self, client: TestClient):
        _upload_map(client, "map.json", _JSON_MAP_23)
        _clean(
            client,
            start={"x": 0, "y": 0},
            robot_model="basic",
            actions=[{"direction": "south", "steps": 1}],
        )
        _clean(
            client,
            start={"x": 0, "y": 0},
            robot_model="basic",
            actions=[{"direction": "east", "steps": 1}],
        )

        history = client.get("/history")

        assert history.status_code == status.HTTP_200_OK
        assert history.headers["content-type"].startswith("text/csv")
        rows = [line for line in history.text.splitlines() if line]
        assert len(rows) == 3  # header + two recorded runs
        assert "completed" in rows[1]
        assert "completed" in rows[2]
        assert "basic" in rows[1]
        assert "basic" in rows[2]

    def test_history_header(self, client: TestClient):
        _upload_map(client, "map.json", _JSON_MAP_23)
        _clean(
            client,
            start={"x": 0, "y": 0},
            robot_model="basic",
            actions=[{"direction": "south", "steps": 1}],
        )

        history = client.get("/history")

        assert history.status_code == status.HTTP_200_OK
        assert history.headers["content-type"].startswith("text/csv")
        rows = [line for line in history.text.splitlines() if line]
        assert len(rows) >= 1  # at least the header
        header = rows[0].split(",")
        expected_columns = TestHistory._CSV_HEADERS
        for i, column in enumerate(expected_columns):
            assert column == header[i]
