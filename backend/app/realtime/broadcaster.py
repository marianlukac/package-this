from abc import ABC, abstractmethod
from typing import Any


class RealtimeBroadcaster(ABC):
    @abstractmethod
    async def broadcast(self, event_type: str, data: dict[str, Any]) -> None: ...


_broadcaster_instance: RealtimeBroadcaster | None = None


def get_broadcaster() -> RealtimeBroadcaster:
    global _broadcaster_instance
    if _broadcaster_instance is None:
        from app.config import get_settings
        settings = get_settings()
        if settings.realtime_publisher == "web_pubsub":
            from app.realtime.pubsub import WebPubSubBroadcaster
            _broadcaster_instance = WebPubSubBroadcaster()
        else:
            from app.realtime.websocket import LocalWebSocketBroadcaster
            _broadcaster_instance = LocalWebSocketBroadcaster()
    return _broadcaster_instance


def reset_broadcaster(broadcaster: RealtimeBroadcaster | None = None) -> None:
    global _broadcaster_instance
    _broadcaster_instance = broadcaster
