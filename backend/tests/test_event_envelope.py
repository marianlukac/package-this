"""Unit tests for event envelope structure and ActorBlock — T032."""
import pytest

from app.events.envelope import ActorBlock, make_envelope


def _env(**kw):
    defaults = dict(
        event_type="package.created", topic="packages",
        actor_id="jim-halpert", actor_name="Jim Halpert",
        source="ui", entity_type="package", entity_id="PKG-001",
        payload={}, summary="created",
    )
    defaults.update(kw)
    return make_envelope(**defaults)


class TestActorBlock:
    def test_defaults(self):
        a = ActorBlock(actor_id="x", actor_name="X")
        assert a.actor_type == "human"
        assert a.persona is None

    def test_all_actor_types_accepted(self):
        for t in ("human", "demo", "agent", "system"):
            a = ActorBlock(actor_id="x", actor_name="X", actor_type=t)
            assert a.actor_type == t

    def test_invalid_actor_type_rejected(self):
        with pytest.raises(Exception):
            ActorBlock(actor_id="x", actor_name="X", actor_type="robot")

    def test_persona_stored(self):
        a = ActorBlock(actor_id="m", actor_name="Michael", persona="manager")
        assert a.persona == "manager"


class TestMakeEnvelope:
    def test_event_id_is_uuid_format(self):
        env = _env()
        assert len(env.eventId) == 36
        assert env.eventId.count("-") == 4

    def test_unique_event_ids(self):
        ids = {_env().eventId for _ in range(10)}
        assert len(ids) == 10

    def test_actor_block_populated(self):
        env = _env(actor_id="dwight-schrute", actor_name="Dwight Schrute", persona="assistant_to_rm")
        assert isinstance(env.actor, ActorBlock)
        assert env.actor.actor_id == "dwight-schrute"
        assert env.actor.actor_name == "Dwight Schrute"
        assert env.actor.persona == "assistant_to_rm"
        assert env.actor.actor_type == "human"

    def test_actor_type_system(self):
        env = _env(actor_id="sim", actor_name="Simulation", actor_type="system")
        assert env.actor.actor_type == "system"

    def test_correlation_id_preserved(self):
        corr = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        env = _env(correlation_id=corr)
        assert env.correlationId == corr

    def test_correlation_id_none_by_default(self):
        env = _env()
        assert env.correlationId is None

    def test_occurred_at_is_iso_string(self):
        env = _env()
        assert "T" in env.occurredAt
        assert env.occurredAt.endswith("Z")

    def test_payload_stored(self):
        env = _env(payload={"pkg_id": "PKG-001", "status": "packaged"})
        assert env.payload["pkg_id"] == "PKG-001"

    def test_entity_fields(self):
        env = _env(entity_type="truck", entity_id="DM-TRUCK-01")
        assert env.entityType == "truck"
        assert env.entityId == "DM-TRUCK-01"

    def test_all_envelope_fields_present(self):
        env = _env()
        for field in ("eventId", "eventType", "topic", "occurredAt", "actor",
                      "source", "entityType", "entityId", "correlationId",
                      "payload", "summary"):
            assert hasattr(env, field)
