from abc import ABC, abstractmethod

from app.events.envelope import EventEnvelope


class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: EventEnvelope, session=None) -> None: ...


_publisher_instance: EventPublisher | None = None


def get_publisher() -> EventPublisher:
    global _publisher_instance
    if _publisher_instance is None:
        from app.config import get_settings
        settings = get_settings()
        if settings.event_publisher == "service_bus":
            from app.events.service_bus import ServiceBusEventPublisher
            _publisher_instance = ServiceBusEventPublisher()
        else:
            from app.events.inmemory import InMemoryEventPublisher
            _publisher_instance = InMemoryEventPublisher()
    return _publisher_instance


def reset_publisher(publisher: EventPublisher | None = None) -> None:
    global _publisher_instance
    _publisher_instance = publisher
