"""
Tests for the MeterDevice hierarchy.
"""

import pytest
from datetime import datetime

from src.meters import SinglePhaseMeter, ThreePhaseMeter, SolarFeedMeter, MeterDevice
from src.exceptions import OverloadError


def test_meter_device_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        MeterDevice("M001", "Hostel A", 230.0)


def test_single_phase_meter_basic_reading():
    meter = SinglePhaseMeter("SP001", "Hostel A", 230.0)
    reading = meter.take_reading(voltage=230.0, current=5.0,
                                  timestamp=datetime(2026, 6, 1, 10, 0))
    expected_kwh = (230.0 * 5.0) / 1000.0
    assert reading.kwh == pytest.approx(expected_kwh)
    assert reading.meter_id == "SP001"


def test_single_phase_meter_overload_raises():
    meter = SinglePhaseMeter("SP002", "Hostel B", 230.0)
    # A huge current relative to rating should trigger overload.
    with pytest.raises(OverloadError):
        meter.take_reading(voltage=230.0, current=500.0,
                            timestamp=datetime(2026, 6, 1, 11, 0))


def test_three_phase_meter_basic_reading():
    meter = ThreePhaseMeter("TP001", "Electronics Lab", 400.0)
    reading = meter.take_reading(voltage=400.0, current=10.0,
                                  timestamp=datetime(2026, 6, 1, 9, 0),
                                  power_factor=0.9)
    import math
    expected_kwh = (math.sqrt(3) * 400.0 * 10.0 * 0.9) / 1000.0
    assert reading.kwh == pytest.approx(expected_kwh)


def test_three_phase_meter_overload_raises():
    meter = ThreePhaseMeter("TP002", "Workshop", 400.0)
    with pytest.raises(OverloadError):
        meter.take_reading(voltage=400.0, current=300.0,
                            timestamp=datetime(2026, 6, 1, 12, 0))


def test_solar_feed_meter_allows_negative_reading():
    meter = SolarFeedMeter("SF001", "Rooftop Array", 230.0)
    reading = meter.take_reading(voltage=230.0, current=-3.0,
                                  timestamp=datetime(2026, 6, 1, 13, 0))
    assert reading.kwh < 0


def test_solar_feed_meter_never_overloads():
    meter = SolarFeedMeter("SF002", "Rooftop Array 2", 230.0)
    reading = meter.take_reading(voltage=230.0, current=1000.0,
                                  timestamp=datetime(2026, 6, 1, 14, 0))
    assert meter.is_overloaded(reading) is False


def test_meter_records_readings_history():
    meter = SinglePhaseMeter("SP003", "Admin Block", 230.0)
    meter.take_reading(voltage=230.0, current=2.0, timestamp=datetime(2026, 6, 1, 8, 0))
    meter.take_reading(voltage=230.0, current=3.0, timestamp=datetime(2026, 6, 1, 9, 0))
    assert len(meter.readings) == 2


def test_meter_str_and_repr():
    meter = SinglePhaseMeter("SP004", "Library", 230.0)
    assert "SP004" in str(meter)
    assert "SinglePhaseMeter" in repr(meter)
