from enum import StrEnum


class RobotModel(StrEnum):
    BASIC = "basic"
    PREMIUM = "premium"

    def should_clean(self, *, dirty: bool) -> bool:
        # BASIC robots always clean, PREMIUM robots clean only if dirty
        return dirty or self is RobotModel.BASIC
