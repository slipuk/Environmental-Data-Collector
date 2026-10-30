from ..models.environmental import City, EnvironmentalModel, RawCityData
from ..clients.weather_sync import fetch_air_quality, fetch_weather
from ..clients.weather_async import acollect
from .transform import parse_weather, parse_air_quality, build_record
from .logger import log

import requests
import time

def collect_city_data(city: City) -> EnvironmentalModel | None:
    weather = None
    air_quality = None

    lat, lon = city.latitude, city.longitude

    try:
        data = fetch_weather(lat, lon)
        weather = parse_weather(data, city.name)
    except requests.RequestException as e:
        log.message("WARNING", f"{city.name}: weather request failed: {e}")
        return None

    try:
        data = fetch_air_quality(lat, lon)
        air_quality = parse_air_quality(data, city.name)
    except requests.RequestException as e:
        log.message("WARNING", f"{city.name}: air quality request failed: {e}")
        return None

    log.message("DEBUG", f"{city.name}: record collected")
    return build_record(city, weather, air_quality)

# helping function to transform list of cities
def transform_city(city: RawCityData) -> EnvironmentalModel:
    city_obj = city.city
    city_weather = parse_weather(city.weather_dict, city_obj.name)
    city_air_quality = parse_air_quality(city.air_quality_dict, city_obj.name)

    return build_record(
        city=city_obj,
        city_weather=city_weather,
        city_air_quality=city_air_quality
    )

async def async_collect_city_data(cities: list[City]) -> list[EnvironmentalModel]:
    start = time.perf_counter()

    try:
        raw_cities = await acollect(cities)
    except Exception as e:
        log.message("ERROR", f"async collection failed: {type(e).__name__}: {e}")
        return []

    successful = [
        city for city in raw_cities
        if city.weather_dict is not None and city.air_quality_dict is not None
    ]
    skipped = len(raw_cities) - len(successful)
    if skipped:
        log.message(
            "WARNING",
            f"skipping {skipped} records with failed requests"
        )

    records = [transform_city(city) for city in successful]
    elapsed = time.perf_counter() - start

    missing_weather = sum(1 for city in raw_cities if city.weather_dict is None)
    missing_air = sum(1 for city in raw_cities if city.air_quality_dict is None)

    log.message(
        "INFO",
        f"async collection finished: cities={len(cities)} written={len(records)} "
        f"skipped={skipped} missing_weather={missing_weather} missing_air={missing_air} "
        f"elapsed={elapsed:.2f}s"
    )

    return records
