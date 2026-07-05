"""API tests for GET /events endpoint — T034."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.domain_event import DomainEvent


def _insert_event(session: Session, **kw) -> DomainEvent:
    """Helper to create a DomainEvent row directly for test setup."""
    import json
    from datetime import datetime
    defaults = dict(
        event_id=f"evt-{__import__('uuid').uuid4()}",
        event_type="package.created",
        topic="packages",
        occurred_at=datetime.utcnow(),
        actor_id="jim-halpert",
        actor_name="Jim Halpert",
        actor_persona=None,
        actor_type="human",
        source="ui",
        entity_type="package",
        entity_id="PKG-001",
        correlation_id=None,
        payload=json.dumps({}),
        summary="Test event",
    )
    defaults.update(kw)
    de = DomainEvent(**defaults)
    session.add(de)
    session.commit()
    return de


@pytest.fixture(name="client")
def client_fixture(engine, publisher):
    from app.database import get_session
    from app.main import app

    def override_session():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestGetEvents:
    def test_returns_list(self, client, session):
        _insert_event(session)
        r = client.get("/events")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_newest_first(self, client, session):
        from datetime import datetime, timedelta
        base = datetime.utcnow()
        _insert_event(session, event_id="old", occurred_at=base - timedelta(hours=1), summary="old")
        _insert_event(session, event_id="new", occurred_at=base, summary="new")
        r = client.get("/events?limit=10")
        items = r.json()
        assert len(items) >= 2
        summaries = [i["summary"] for i in items]
        assert summaries.index("new") < summaries.index("old")

    def test_topic_filter(self, client, session):
        _insert_event(session, event_id="e1", topic="packages", entity_id="PKG-AAA")
        _insert_event(session, event_id="e2", topic="audit-log", entity_id="PKG-BBB")
        r = client.get("/events?topic=packages")
        items = r.json()
        assert all(i["topic"] == "packages" for i in items)

    def test_entity_id_filter(self, client, session):
        _insert_event(session, event_id="e3", entity_id="PKG-FILTER-ME")
        _insert_event(session, event_id="e4", entity_id="PKG-OTHER")
        r = client.get("/events?entity_id=PKG-FILTER-ME")
        items = r.json()
        assert all(i["entity_id"] == "PKG-FILTER-ME" for i in items)

    def test_correlation_id_filter(self, client, session):
        corr = "aaaabbbb-cccc-dddd-eeee-ffffgggghhh0"
        _insert_event(session, event_id="e5", correlation_id=corr)
        _insert_event(session, event_id="e6", correlation_id=None)
        r = client.get(f"/events?correlation_id={corr}")
        items = r.json()
        assert len(items) == 1
        assert items[0]["correlation_id"] == corr

    def test_limit_respected(self, client, session):
        for i in range(10):
            _insert_event(session, event_id=f"lim-{i}")
        r = client.get("/events?limit=3")
        assert len(r.json()) <= 3

    def test_actor_block_in_response(self, client, session):
        _insert_event(session, event_id="actor-test", actor_id="dwight", actor_name="Dwight")
        r = client.get("/events?limit=100")
        items = [i for i in r.json() if i.get("entity_id") == "PKG-001"]
        if items:
            actor = items[0]["actor"]
            assert "actor_id" in actor
            assert "actor_name" in actor
            assert "actor_type" in actor
