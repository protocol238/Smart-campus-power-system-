"""
BuildingZone — groups multiple MeterDevice instances under one
building/zone (e.g. a hostel, a lab, an administrative block) and
computes the zone's total power consumption.
"""

from src.meters import MeterDevice
from src.power_reading import PowerReading


class BuildingZone:
    """
    Represents a single building or zone on campus that owns one or
    more MeterDevice instances (composition: meters belong to exactly
    one zone and are created/destroyed with it).

    Attributes:
        name (str): Name of the building/zone, e.g. "Hostel A".
        zone_type (str): Category, e.g. "Hostel", "Lab", "Admin".
    """

    def __init__(self, name: str, zone_type: str):
        if not name:
            raise ValueError("BuildingZone name must not be empty.")
        if not zone_type:
            raise ValueError("BuildingZone zone_type must not be empty.")
        self._name = name
        self._zone_type = zone_type
        self._meters = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def zone_type(self) -> str:
        return self._zone_type

    def add_meter(self, meter: MeterDevice) -> None:
        """Register a MeterDevice as part of this zone."""
        if not isinstance(meter, MeterDevice):
            raise TypeError("Only MeterDevice instances can be added to a zone.")
        self._meters.append(meter)

    @property
    def meters(self) -> list:
        return list(self._meters)

    def compute_zone_total(self) -> float:
        """
        Sum the kwh of the most recent reading from every meter in
        this zone. Returns total kWh as a float.

        Uses sum() over PowerReading objects, relying on __radd__
        defined on PowerReading.
        """
        latest_readings = []
        for meter in self._meters:
            if meter.readings:
                latest_readings.append(meter.readings[-1])
        if not latest_readings:
            return 0.0
        return sum(latest_readings)

    def __len__(self) -> int:
        """Number of meters registered in this zone."""
        return len(self._meters)

    def __contains__(self, meter_id: str) -> bool:
        """Check whether a meter with the given meter_id exists in this zone."""
        return any(m.meter_id == meter_id for m in self._meters)

    def __str__(self):
        return f"BuildingZone({self._name}, type={self._zone_type}, meters={len(self._meters)})"

    def __repr__(self):
        return (f"BuildingZone(name={self._name!r}, zone_type={self._zone_type!r}, "
                f"meter_count={len(self._meters)})")
