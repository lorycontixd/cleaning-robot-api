from app.services.cleaning_service import CleaningService
from app.storage.map_store import MapStore
from app.storage.session_history import SessionHistory

_map_store: MapStore | None = None
_history: SessionHistory | None = None

cleaning_service: CleaningService | None = None


def get_map_store():
    global _map_store

    if _map_store is None:
        _map_store = MapStore()

    return _map_store


def get_session_history():
    global _history

    if _history is None:
        _history = SessionHistory()

    return _history


def get_cleaning_service():
    global _map_store, _history, cleaning_service

    if cleaning_service is None:
        if _map_store is None:
            _map_store = MapStore()
        if _history is None:
            _history = SessionHistory()
        cleaning_service = CleaningService(map_store=_map_store, history=_history)

    return cleaning_service
