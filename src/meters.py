"""
Meter device hierarchy for the Smart Campus Power Management System.

MeterDevice is an abstract base class defining the contract every metering
device must follow. SinglePhaseMeter, ThreePhaseMeter, and SolarFeedMeter
are concrete implementations for different building/zone types.
"""

import math
from abc import ABC, abstractmethod
from datetime import datetime

from src.power_reading import PowerReading
from src.exceptions import OverloadError


class MeterDevice(ABC):
    """
    Abstract base class for all metering devices on the campus grid.

    Attributes:
        meter_id (str): Unique identifier for this meter.
        location (str): Building/zone location description.
        voltage_rating (float): Rated voltage capacity of this meter.
    """

    def __init__(self, meter_id: str, location: str, voltage_rating: float):
        if not meter_id:
            raise ValueError("meter_id must not be empty.")
        if voltage_rating <= 0:
            raise ValueError("voltage_rating must be positive.")
        self._meter_id = meter_id
        self._location = location
        self._voltage_rating = float(voltage_rating)
        self._readings = []

    @property
    def meter_id(self) -> str:
        return self._meter_id

    @property
    def location(self) -> str:
        return self._location

    @property
    def voltage_rating(self) -> float:
        return self._voltage_rating

    @property
    def readings(self) -> list:
        """All PowerReading objects recorded so far on this meter."""
        return list(self._readings)

    @abstractmethod
    def take_reading(self, voltage: float, current: float,
                      timestamp: datetime, power_factor: float = 1.0) -> PowerReading:
        """Compute and record a new PowerReading from raw measurements."""
        raise NotImplementedError

    @abstractmethod
    def is_overloaded(self, reading: PowerReading) -> bool:
        """Return True if the given reading exceeds 150% rated capacity."""
        raise NotImplementedError

    def _record(self, reading: PowerReading) -> PowerReading:
        """Store the reading and raise OverloadError if it's unsafe."""
        self._readings.append(reading)
        if self.is_overloaded(reading):
            raise OverloadError(
                self._meter_id,
                "OVERLOAD",
                f"Reading of {reading.kwh:.2f} kWh exceeds 150% of rated capacity."
            )
        return reading

    def __str__(self):
        return f"{self.__class__.__name__}({self._meter_id} @ {self._location})"

    def __repr__(self):
        return (f"{self.__class__.__name__}(meter_id={self._meter_id!r}, "
                f"location={self._location!r}, voltage_rating={self._voltage_rating!r})")


class SinglePhaseMeter(MeterDevice):
    """Single-phase meter for hostels and offices. P = V x I."""

    def take_reading(self, voltage: float, current: float,
                      timestamp: datetime, power_factor: float = 1.0) -> PowerReading:
        watts = voltage * current
        kwh = watts / 1000.0
        reading = PowerReading(self._meter_id, kwh, voltage, current, timestamp)
        return self._record(reading)

    def is_overloaded(self, reading: PowerReading) -> bool:
        rated_capacity_kwh = (self._voltage_rating * reading.current) / 1000.0
        return reading.kwh > 1.5 * rated_capacity_kwh if rated_capacity_kwh else False


class ThreePhaseMeter(MeterDevice):
    """Three-phase meter for labs and workshops. P = sqrt(3) x V x I x PF."""

    def take_reading(self, voltage: float, current: float,
                      timestamp: datetime, power_factor: float = 0.9) -> PowerReading:
        watts = math.sqrt(3) * voltage * current * power_factor
        kwh = watts / 1000.0
        reading = PowerReading(self._meter_id, kwh, voltage, current, timestamp)
        return self._record(reading)

    def is_overloaded(self, reading: PowerReading) -> bool:
        rated_capacity_kwh = (math.sqrt(3) * self._voltage_rating * reading.current * 0.9) / 1000.0
        return reading.kwh > 1.5 * rated_capacity_kwh if rated_capacity_kwh else False


class SolarFeedMeter(MeterDevice):
    """
    Tracks energy fed back into the grid from solar generation.
    Readings may be negative when generation exceeds local consumption.
    """

    def take_reading(self, voltage: float, current: float,
                      timestamp: datetime, power_factor: float = 1.0) -> PowerReading:
        watts = voltage * current
        kwh = watts / 1000.0
        reading = PowerReading(self._meter_id, kwh, voltage, current, timestamp)
        # Solar feed meters can't "overload" in the traditional sense,
        # since negative kwh means generation -- skip the overload check.
        self._readings.append(reading)
        return reading

    def is_overloaded(self, reading: PowerReading) -> bool:
        # Solar feed is exempt from overload logic by design.
        return False
