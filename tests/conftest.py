import pytest

from app.core.map import Map, Tile
from app.core.models.coordinate import Coordinate
from app.services.cleaning_service import CleaningService
from app.storage.map_store import MapStore
from app.storage.session_history import SessionHistory


@pytest.fixture()
def map_store():
    return MapStore()


@pytest.fixture()
def session_history():
    return SessionHistory()


@pytest.fixture
def cleaning_service(map_store, session_history) -> CleaningService:
    return CleaningService(map_store, session_history)


@pytest.fixture
def sample_23_map():
    # replica of JSON map format example in docs
    return Map(
        2,
        3,
        tiles={
            Coordinate(0, 0): Tile(is_walkable=True, is_dirty=True),
            Coordinate(1, 0): Tile(is_walkable=True, is_dirty=False),
            Coordinate(2, 0): Tile(is_walkable=False, is_dirty=False),
            Coordinate(0, 1): Tile(is_walkable=True, is_dirty=True),
            Coordinate(1, 1): Tile(is_walkable=True, is_dirty=True),
            Coordinate(2, 1): Tile(is_walkable=True, is_dirty=True),
        },
    )


@pytest.fixture
def sample_map() -> Map:
    # new map per test - clean() doesn't affect other tests

    return Map(
        3,
        3,
        {
            Coordinate(0, 0): Tile(is_walkable=True, is_dirty=True),
            Coordinate(0, 1): Tile(is_walkable=False, is_dirty=False),
            Coordinate(0, 2): Tile(is_walkable=False, is_dirty=True),
            Coordinate(1, 0): Tile(is_walkable=True, is_dirty=False),
            Coordinate(1, 1): Tile(is_walkable=True, is_dirty=True),
            Coordinate(1, 2): Tile(is_walkable=False, is_dirty=False),
            Coordinate(2, 0): Tile(is_walkable=True, is_dirty=True),
            Coordinate(2, 1): Tile(is_walkable=False, is_dirty=False),
            Coordinate(2, 2): Tile(is_walkable=True, is_dirty=False),
        },
    )
