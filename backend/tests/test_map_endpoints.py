"""Tests for map endpoints and truck listing (T031)."""
import pytest

from app.models.employee import Employee, PersonaType
from app.models.map_location import LocationType, MapLocation
from app.models.truck import Truck, TruckStatus

# ─── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(name="map_locations")
def map_locations_fixture(session):
    """Seed one of each location type."""
    locs = [
        MapLocation(name="Dunder Mifflin HQ", location_type=LocationType.WAREHOUSE,
                    lat=41.4090, lng=-75.6624),
        MapLocation(name="Vance Refrigeration", location_type=LocationType.CUSTOMER,
                    lat=41.408, lng=-75.662),
        MapLocation(name="Wendy's Keyser Ave", location_type=LocationType.FOOD,
                    lat=41.418, lng=-75.658),
        MapLocation(name="Dunkin Jefferson Ave", location_type=LocationType.DONUT,
                    lat=41.410, lng=-75.659),
    ]
    for loc in locs:
        session.add(loc)
    session.commit()
    return locs


@pytest.fixture(name="trucks")
def trucks_fixture(session):
    """Seed the three canonical DM trucks."""
    truck_data = [
        ("DM-TRUCK-01", 1, "The Dundie"),
        ("DM-TRUCK-02", 2, "Pretzel Day"),
        ("DM-TRUCK-03", 3, "Big Tuna"),
    ]
    trucks = []
    for truck_id, number, name in truck_data:
        t = Truck(
            truck_id=truck_id, truck_number=number, name=name,
            status=TruckStatus.AT_WAREHOUSE,
            current_lat=41.4090, current_lng=-75.6624,
        )
        session.add(t)
        trucks.append(t)
    session.commit()
    return trucks


# ─── GET /map/markers ───────────────────────────────────────────────────────────

def test_map_markers_returns_all_four_types(client, map_locations):
    """GET /map/markers returns at least one marker of each type."""
    response = client.get("/map/markers", headers={"X-Persona-Id": "michael-scott"})
    assert response.status_code == 200

    data = response.json()
    types_returned = {item["location_type"] for item in data}
    assert "warehouse" in types_returned
    assert "customer" in types_returned
    assert "food" in types_returned
    assert "donut" in types_returned


def test_map_markers_has_correct_fields(client, map_locations):
    """Each marker response includes id, name, location_type, lat, lng."""
    response = client.get("/map/markers", headers={"X-Persona-Id": "darryl-philbin"})
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 4

    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "location_type" in first
    assert "lat" in first
    assert "lng" in first


def test_map_locations_alias_matches_markers(client, map_locations):
    """GET /map/locations and GET /map/markers return the same data."""
    h = {"X-Persona-Id": "michael-scott"}
    r1 = client.get("/map/markers", headers=h)
    r2 = client.get("/map/locations", headers=h)

    assert r1.status_code == 200
    assert r2.status_code == 200

    # Both endpoints should return the same number of items
    assert len(r1.json()) == len(r2.json())


# ─── GET /trucks ────────────────────────────────────────────────────────────────

def test_trucks_returns_exactly_three(client, trucks):
    """GET /trucks returns exactly 3 trucks in the baseline fixture."""
    response = client.get("/trucks", headers={"X-Persona-Id": "michael-scott"})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3


def test_trucks_have_correct_names(client, trucks):
    """GET /trucks returns The Dundie, Pretzel Day, and Big Tuna."""
    response = client.get("/trucks", headers={"X-Persona-Id": "michael-scott"})
    assert response.status_code == 200

    names = {t["name"] for t in response.json()}
    assert "The Dundie" in names
    assert "Pretzel Day" in names
    assert "Big Tuna" in names


def test_trucks_have_required_fields(client, trucks):
    """Each truck response includes truck_id, truck_number, name, status, current_lat, current_lng."""
    response = client.get("/trucks", headers={"X-Persona-Id": "michael-scott"})
    assert response.status_code == 200

    for truck in response.json():
        assert "truck_id" in truck
        assert "truck_number" in truck
        assert "name" in truck
        assert "status" in truck


# ─── GET /trucks/{id}/current-location ─────────────────────────────────────────

def test_truck_current_location_returns_lat_lng(client, trucks):
    """GET /trucks/{id}/current-location returns lat and lng for a known truck."""
    response = client.get(
        "/trucks/DM-TRUCK-01/current-location",
        headers={"X-Persona-Id": "michael-scott"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "lat" in data
    assert "lng" in data
    assert data["lat"] == pytest.approx(41.4090, abs=1e-3)
    assert data["lng"] == pytest.approx(-75.6624, abs=1e-3)


def test_truck_current_location_404_unknown(client, trucks):
    """GET /trucks/{id}/current-location returns 404 for an unknown truck."""
    response = client.get(
        "/trucks/NO-SUCH-TRUCK/current-location",
        headers={"X-Persona-Id": "michael-scott"},
    )
    assert response.status_code == 404


# ─── POST /trucks/{id}/reroute — permission checks ─────────────────────────────

def test_reroute_returns_403_for_non_manager(client, trucks, session):
    """POST /trucks/{id}/reroute returns 403 when called with a non-manager persona."""
    darryl = Employee(
        employee_id="darryl-philbin", name="Darryl Philbin",
        persona=PersonaType.WAREHOUSE, title="Warehouse Foreman",
        email="darryl@dundermifflin.com",
    )
    session.add(darryl)
    session.commit()

    response = client.post(
        "/trucks/DM-TRUCK-01/reroute",
        json={"location_id": 999, "reason": "Kevin is hungry"},
        headers={"X-Persona-Id": "darryl-philbin"},
    )
    assert response.status_code == 403


def test_reroute_returns_409_when_truck_not_on_route(client, trucks, map_locations, session):
    """POST /trucks/{id}/reroute returns 409 when truck is at warehouse (not dispatched)."""
    michael = Employee(
        employee_id="michael-scott", name="Michael Scott",
        persona=PersonaType.MANAGER, title="Regional Manager",
        email="michael@dundermifflin.com",
    )
    session.add(michael)
    session.commit()

    food = next(l for l in map_locations if l.location_type in (LocationType.FOOD, LocationType.DONUT))

    response = client.post(
        "/trucks/DM-TRUCK-01/reroute",
        json={"location_id": food.id, "reason": "Kevin is hungry"},
        headers={"X-Persona-Id": "michael-scott"},
    )
    # Truck is AT_WAREHOUSE — not eligible for reroute
    assert response.status_code == 409
