from app.core.map import Map


class MapStore:
    """Stores the map data"""

    def __init__(self, map: Map | None = None):
        self._map = map

    def current(self) -> Map | None:
        return self._map

    def load(self, map: Map) -> None:
        self._map = map
