"""
Tests for BuildingZone.
"""

import pytest
from datetime import datetime

from src.building_zone import BuildingZone
from src.meters import SinglePhaseMeter, SolarFeedMeter


def test_building_zone_construction():
    zone = BuildingZone("Hostel A", "Hostel")
    assert zone.name == "Hostel A"
    assert zone.zone_type == "Hostel"
    assert len(zone) == 0


def test_building_zone_rejects_empty_name():
    with pytest.raises(ValueError):
        BuildingZone("", "Hostel")


def test_add_meter_increases_len():
    zone = BuildingZone("Hostel A", "Hostel")
    meter = SinglePhaseMeter("SP001", "Hostel A", 230.0)
    zone.add_meter(meter)
    assert len(zone) == 1


def test_add_meter_rejects_non_meter_objects():
    zone = BuildingZone("Hostel A", "Hostel")
    with pytest.raises(TypeError):
        zone.add_meter("not a meter")


def test_contains_checks_meter_id():
    zone = BuildingZone("Lab Block", "Lab")
    meter = SinglePhaseMeter("SP002", "Lab Block", 230.0)
    zone.add_meter(meter)
    assert "SP002" in zone
    assert "SP999" not in zone


def test_compute_zone_total_sums_latest_readings():
    zone = BuildingZone("Admin Block", "Admin")
    meter1 = SinglePhaseMeter("SP003", "Admin Block", 230.0)
    meter2 = SinglePhaseMeter("SP004", "Admin Block", 230.0)
    meter1.take_reading(voltage=230.0, current=2.0, timestamp=datetime(2026, 6, 1, 8, 0))
    meter2.take_reading(voltage=230.0, current=3.0, timestamp=datetime(2026, 6, 1, 8, 0))
    zone.add_meter(meter1)
    zone.add_meter(meter2)

    total = zone.compute_zone_total()
    expected = (230.0 * 2.0 / 1000.0) + (230.0 * 3.0 / 1000.0)
    assert total == pytest.approx(expected)


def test_compute_zone_total_with_no_readings_is_zero():
    zone = BuildingZone("Empty Zone", "Admin")
    meter = SinglePhaseMeter("SP005", "Empty Zone", 230.0)
    zone.add_meter(meter)
    assert zone.compute_zone_total() == 0.0


def test_compute_zone_total_handles_solar_negative_contribution():
    zone = BuildingZone("Rooftop Zone", "Solar")
    solar = SolarFeedMeter("SF001", "Rooftop Zone", 230.0)
    solar.take_reading(voltage=230.0, current=-2.0, timestamp=datetime(2026, 6, 1, 12, 0))
    zone.add_meter(solar)
    assert zone.compute_zone_total() < 0


def test_zone_str_and_repr():
    zone = BuildingZone("Hostel B", "Hostel")
    assert "Hostel B" in str(zone)
    assert "BuildingZone" in repr(zone)
