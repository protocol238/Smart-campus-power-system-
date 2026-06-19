"""
Custom exception hierarchy for the Smart Campus Power Management System.

Every exception carries structured diagnostic fields (meter_id, fault_code,
detail, timestamp) so that callers can programmatically inspect *why*
something went wrong, not just read a message string.
"""

from datetime import datetime


class MeterFaultError(Exception):
    """
    Base exception for any fault detected on a metering device.

    Attributes:
        meter_id (str): ID of the meter that raised the fault.
        fault_code (str): Short machine-readable fault code, e.g. 'OVERLOAD'.
        detail (str): Human-readable explanation of the fault.
        timestamp (datetime): When the fault was detected.
    """

    def __init__(self, meter_id: str, fault_code: str, detail: str,
                 timestamp: datetime = None):
        self.meter_id = meter_id
        self.fault_code = fault_code
        self.detail = detail
        self.timestamp = timestamp or datetime.now()
        message = f"[{meter_id}] Fault {fault_code}: {detail}"
        super().__init__(message)


class OverloadError(MeterFaultError):
    """Raised when a meter reading exceeds 150% of its rated capacity."""
    pass


class TariffConfigError(MeterFaultError):
    """Raised when a TariffSchedule is constructed with invalid rates."""
    pass
