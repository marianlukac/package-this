from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        connect_args = {}
        if "sqlite" in settings.database_url:
            connect_args["check_same_thread"] = False
        _engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)
    return _engine


def _ensure_mssql_database_exists() -> None:
    """Create the target database on SQL Server if it doesn't exist yet."""
    from app.config import get_settings
    import re
    url = get_settings().database_url
    # Only applies to mssql/pyodbc connections
    if "mssql" not in url:
        return
    # Extract database name from the URL (…/dm_packages?…)
    m = re.search(r"/([^/?]+)\?", url)
    if not m:
        return
    db_name = m.group(1)
    # Connect to master to run CREATE DATABASE
    master_url = url.replace(f"/{db_name}?", "/master?")
    master_engine = create_engine(master_url, echo=False, isolation_level="AUTOCOMMIT")
    with master_engine.connect() as conn:
        conn.execute(
            __import__("sqlalchemy").text(
                f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{db_name}') "
                f"CREATE DATABASE [{db_name}]"
            )
        )
    master_engine.dispose()


def create_db_and_tables() -> None:
    _ensure_mssql_database_exists()
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session
