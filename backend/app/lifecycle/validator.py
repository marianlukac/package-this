from app.lifecycle.transitions import VALID_TRANSITIONS, InvalidTransitionError
from app.models.package import TERMINAL_STATUSES


class LifecycleValidator:
    @staticmethod
    def validate(current: str, target: str) -> None:
        allowed = VALID_TRANSITIONS.get(current, [])
        if target not in allowed:
            raise InvalidTransitionError(current, target)

    @staticmethod
    def is_terminal(status: str) -> bool:
        return status in TERMINAL_STATUSES
