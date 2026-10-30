from ..models.environmental import EnvironmentalModel, CityAirQuality, CityWeather, City
from .logger import log
from datetime import datetime, timezone


def _context(city_name: str | None) -> str:
    return f"{city_name}: " if city_name else ""


def validate_time(datetime_text: str | None, context: str = "") -> datetime | None:
    if not datetime_text:
        log.message("WARNING", f"{context}datetime missing")
        return None

    try:
        datetime_obj = datetime.fromisoformat(datetime_text)
    except (TypeError, ValueError) as e:
        log.message("WARNING", f"{context}invalid datetime {datetime_text!r}: {e}")
        return None

    if datetime_obj.tzinfo is None:
        datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)
    else:
        datetime_obj = datetime_obj.astimezone(timezone.utc)

    return datetime_obj

def validate_temperature(temperature: float | None, context: str = "") -> float | None:
    if temperature is None:
        log.message("DEBUG", f"{context}temperature missing")
        return None
    if temperature < -100 or temperature > 80:
        log.message("WARNING", f"{context}temperature out of range: {temperature}")
        return None
    return temperature

def validate_humidity(humidity: float | None, context: str = "") -> float | None:
    if humidity is None:
        log.message("DEBUG", f"{context}humidity missing")
        return None
    if humidity < 0 or humidity > 100:
        log.message("WARNING", f"{context}humidity out of range: {humidity}")
        return None
    return humidity

def validate_wind_speed(wind_speed: float | None, context: str = "") -> float | None:
    if wind_speed is None:
        log.message("DEBUG", f"{context}wind speed missing")
        return None
    if wind_speed < 0 or wind_speed > 410:
        log.message("WARNING", f"{context}wind speed out of range: {wind_speed}")
        return None
    return wind_speed

def validate_pm25(pm25: float | None, context: str = "") -> float | None:
    if pm25 is None:
        log.message("DEBUG", f"{context}pm25 missing")
        return None
    if pm25 < 0 or pm25 > 2000:
        log.message("WARNING", f"{context}pm25 out of range: {pm25}")
        return None
    return pm25

def validate_pm10(pm10: float | None, context: str = "") -> float | None:
    if pm10 is None:
        log.message("DEBUG", f"{context}pm10 missing")
        return None
    if pm10 < 0 or pm10 > 5000:
        log.message("WARNING", f"{context}pm10 out of range: {pm10}")
        return None
    return pm10

def validate_city_name(name: str | None = None, context: str = "") -> str | None:
    if name is None:
        log.message("WARNING", f"{context}city name missing")
        return None
    length = len(name)
    if length >= 256 or length == 0:
        log.message("WARNING", f"{context}invalid city name length: {length}")
        return None
    return name

def validate_city_coordinates(
    lat: float | None,
    lon: float | None,
    context: str = ""
) -> tuple[float | None, float | None]:
    none_set = (None, None)
    if lat is None or lon is None:
        log.message("WARNING", f"{context}coordinates missing: lat={lat} lon={lon}")
        return none_set
    if (lat < -90 or lat > 90) or (lon < -180 or lon > 180):
        log.message("WARNING", f"{context}coordinates out of range: lat={lat} lon={lon}")
        return none_set
    return lat, lon

def parse_weather(data: dict | None, city_name: str | None = None) -> CityWeather:
    context = _context(city_name)
    if not data:
        log.message("WARNING", f"{context}no weather data")
        return CityWeather()

    current = data.get("current") or {}
    if not current:
        log.message("WARNING", f"{context}weather payload missing 'current'")

    return CityWeather(
        measured_at=validate_time(current.get("time"), context),
        temperature=validate_temperature(current.get("temperature_2m"), context),
        humidity=validate_humidity(current.get("relative_humidity_2m"), context),
        wind_speed=validate_wind_speed(current.get("wind_speed_10m"), context)
    )

def parse_air_quality(data: dict | None, city_name: str | None = None) -> CityAirQuality:
    context = _context(city_name)
    if not data:
        log.message("WARNING", f"{context}no air quality data")
        return CityAirQuality()

    current = data.get("current") or {}
    if not current:
        log.message("WARNING", f"{context}air quality payload missing 'current'")

    return CityAirQuality(
        measured_at=validate_time(current.get("time"), context),
        pm25=validate_pm25(current.get("pm2_5"), context),
        pm10=validate_pm10(current.get("pm10"), context)
    )

def parse_city_data(data: dict | None) -> City | None:
    if not data:
        log.message("WARNING", "geocoding: no city data")
        return None

    name = validate_city_name(data.get("name"), "geocoding: ")
    lat, lon = validate_city_coordinates(
        data.get("latitude"),
        data.get("longitude"),
        "geocoding: "
    )

    if name is None or lat is None or lon is None:
        log.message("WARNING", "geocoding: invalid city record")
        return None

    return City(name=name, latitude=lat, longitude=lon)

def build_record(
        city: City,
        city_weather: CityWeather | None,
        city_air_quality: CityAirQuality | None
    ) -> EnvironmentalModel:

    if city_weather is None:
        log.message("WARNING", f"{city.name}: no weather data; using empty values")
        city_weather = CityWeather()
    if city_air_quality is None:
        log.message("WARNING", f"{city.name}: no air quality data; using empty values")
        city_air_quality = CityAirQuality()

    return EnvironmentalModel(
        city=city.name,
        latitude=city.latitude,
        longitude=city.longitude,
        weather_measured_at=city_weather.measured_at,
        air_quality_measured_at=city_air_quality.measured_at,
        temperature=city_weather.temperature,
        humidity=city_weather.humidity,
        wind_speed=city_weather.wind_speed,
        pm25=city_air_quality.pm25,
        pm10=city_air_quality.pm10
    )
