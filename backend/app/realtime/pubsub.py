import json
from typing import Any

from app.realtime.broadcaster import RealtimeBroadcaster

HUB_NAME = "dm-packages"


class WebPubSubBroadcaster(RealtimeBroadcaster):
    async def broadcast(self, event_type: str, data: dict[str, Any]) -> None:
        from azure.messaging.webpubsubservice.aio import WebPubSubServiceClient

        from app.config import get_settings

        settings = get_settings()
        async with WebPubSubServiceClient.from_connection_string(
            settings.azure_web_pubsub_connection_string, hub=HUB_NAME
        ) as client:
            await client.send_to_all(
                message=json.dumps({"type": event_type, "data": data}),
                content_type="application/json",
            )
