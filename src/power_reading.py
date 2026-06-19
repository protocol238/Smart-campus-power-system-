"""
PowerReading — an immutable snapshot of a single meter measurement.
"""

from datetime import datetime
from functools import total_ordering


@total_ordering
class PowerReading:
    """
    Immutable record of one power measurement taken from a meter.

    Attributes:
        meter_id (str): ID of the meter that produced this reading.
        kwh (float): Energy consumed (or generated, if negative, for solar).
        voltage (float): Voltage at time of reading.
        current (float): Current at time of reading.
        timestamp (datetime): When the reading was taken.
    """

    def __init__(self, meter_id: str, kwh: float, voltage: float,
                 current: float, timestamp: datetime):
        self._meter_id = meter_id
        self._kwh = float(kwh)
        self._voltage = float(voltage)
        self._current = float(current)
        self._timestamp = timestamp

    @property
    def meter_id(self) -> str:
        return self._meter_id

    @property
    def kwh(self) -> float:
        return self._kwh

    @property
    def voltage(self) -> float:
        return self._voltage

    @property
    def current(self) -> float:
        return self._current

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    def __add__(self, other):
        if isinstance(other, PowerReading):
            return self._kwh + other._kwh
        if isinstance(other, (int, float)):
            return self._kwh + other
        return NotImplemented

    def __radd__(self, other):
        # Makes sum([reading1, reading2, ...]) work, since sum() starts
        # by computing 0 + reading1.
        return self.__add__(other)

    def __eq__(self, other):
        if not isinstance(other, PowerReading):
            return NotImplemented
        return (self._meter_id == other._meter_id and
                self._kwh == other._kwh and
                self._timestamp == other._timestamp)

    def __lt__(self, other):
        if not isinstance(other, PowerReading):
            return NotImplemented
        return self._timestamp < other._timestamp

    def __hash__(self):
        return hash((self._meter_id, self._kwh, self._timestamp))

    def __str__(self):
        return (f"PowerReading(meter={self._meter_id}, "
                f"kwh={self._kwh:.2f}, time={self._timestamp})")

    def __repr__(self):
        return (f"PowerReading(meter_id={self._meter_id!r}, "
                f"kwh={self._kwh!r}, voltage={self._voltage!r}, "
                f"current={self._current!r}, timestamp={self._timestamp!r})")
