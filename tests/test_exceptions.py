"""
Tests for the custom exception hierarchy.

Run with:  pytest tests/test_exceptions.py -v
"""

import pytest
from datetime import datetime

from src.exceptions import MeterFaultError, OverloadError, TariffConfigError


def test_meter_fault_error_stores_fields():
    err = MeterFaultError("M001", "GEN_FAULT", "Voltage dropout detected")
    assert err.meter_id == "M001"
    assert err.fault_code == "GEN_FAULT"
    assert err.detail == "Voltage dropout detected"
    assert isinstance(err.timestamp, datetime)


def test_meter_fault_error_message_format():
    err = MeterFaultError("M002", "GEN_FAULT", "Something went wrong")
    assert "M002" in str(err)
    assert "GEN_FAULT" in str(err)


def test_overload_error_is_a_meter_fault_error():
    err = OverloadError("M003", "OVERLOAD", "150% capacity exceeded")
    assert isinstance(err, MeterFaultError)
    assert err.fault_code == "OVERLOAD"


def test_tariff_config_error_is_a_meter_fault_error():
    err = TariffConfigError("N/A", "BAD_TARIFF", "Negative rate supplied")
    assert isinstance(err, MeterFaultError)


def test_overload_error_can_be_raised_and_caught():
    with pytest.raises(OverloadError) as exc_info:
        raise OverloadError("M004", "OVERLOAD", "Reading exceeded limit")
    assert exc_info.value.meter_id == "M004"
