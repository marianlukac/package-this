from app.events.envelope import EventEnvelope
from app.events.publisher import EventPublisher


class ServiceBusEventPublisher(EventPublisher):
    def __init__(self) -> None:
        from azure.servicebus.aio import ServiceBusClient

        from app.config import get_settings
        settings = get_settings()
        self._connection_string = settings.azure_service_bus_connection_string
        self._client: ServiceBusClient | None = None

    async def publish(self, event: EventEnvelope) -> None:
        from azure.servicebus import ServiceBusMessage
        from azure.servicebus.aio import ServiceBusClient

        async with ServiceBusClient.from_connection_string(self._connection_string) as client:
            async with client.get_topic_sender(topic_name=event.topic) as sender:
                message = ServiceBusMessage(
                    body=event.model_dump_json(),
                    content_type="application/json",
                    subject=event.eventType,
                )
                await sender.send_messages(message)
