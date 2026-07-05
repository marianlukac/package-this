from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./dm_packages_dev.db"
    event_publisher: str = "inmemory"
    azure_service_bus_connection_string: str = ""
    realtime_publisher: str = "websocket"
    azure_web_pubsub_connection_string: str = ""
    azure_maps_key: str = ""
    simulation_tick_interval_seconds: int = 5
    simulation_location_event_every_n_ticks: int = 5
    app_env: str = "local"
    app_port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
