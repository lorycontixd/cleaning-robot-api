from app.core.models.session_report import SessionReport


class SessionHistory:
    def __init__(self):
        self.history = []

    def record(self, report: SessionReport):
        self.history.append(report)

    def get_history(self) -> list[SessionReport]:
        # return a copy so callers can't mutate the internal list
        return list(self.history)

    def clear_history(self):
        self.history.clear()
