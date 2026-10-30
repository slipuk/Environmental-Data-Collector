from dataclasses import dataclass, field
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

#supporting dataclass for async functions output
@dataclass
class City:
    name: str
    latitude: float
    longitude: float

@dataclass
class RawCityData:
    city: City
    weather_dict: dict | None = None
    air_quality_dict: dict | None = None

@dataclass
class CityWeather:
    measured_at: datetime | None = None
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None

@dataclass
class CityAirQuality:
    measured_at: datetime | None = None
    pm25: float | None = None
    pm10: float | None = None

@dataclass
class EnvironmentalModel:
    city: str
    latitude: float
    longitude: float
    collected_at: datetime = field(default_factory=utc_now)
    weather_measured_at: datetime | None = None
    air_quality_measured_at: datetime | None = None
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    pm25: float | None = None
    pm10: float | None = None