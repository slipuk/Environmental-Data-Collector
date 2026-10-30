import httpx
import asyncio
import time
from ..models.environmental import City, RawCityData
from ..service.logger import log

urls = {
    "weather": "https://api.open-meteo.com/v1/forecast",
    "air_quality": "https://air-quality-api.open-meteo.com/v1/air-quality"
}

timeout = 3
MAX_CONCURRENT_REQUESTS = 3

async def afetch_weather(
        aclient: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        lat: float,
        lon: float
    ):
    weather_url = urls.get("weather")
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"]
    }

    async with semaphore:
        start = time.perf_counter()
        response = await aclient.get(
            url = weather_url,
            params = params,
            timeout = timeout
        )
        response.raise_for_status()

    log.message(
        "DEBUG",
        f"GET weather lat={lat} lon={lon} status={response.status_code} "
        f"elapsed={time.perf_counter() - start:.2f}s"
    )

    data: dict = response.json()
    return data

async def afetch_air_quality(
        aclient: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        lat: float,
        lon: float
    ):
    air_quality_url = urls.get("air_quality")
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["pm2_5", "pm10"]
    }

    async with semaphore:
        start = time.perf_counter()
        response = await aclient.get(
            url = air_quality_url,
            params = params,
            timeout = timeout
        )
        response.raise_for_status()

    log.message(
        "DEBUG",
        f"GET air_quality lat={lat} lon={lon} status={response.status_code} "
        f"elapsed={time.perf_counter() - start:.2f}s"
    )

    data: dict = response.json()
    return data

async def afetch_city(
        aclient: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        city: City
    ) -> RawCityData:
    lat, lon = city.latitude, city.longitude
    weather_data, air_quality_data = await asyncio.gather(
        afetch_weather(aclient, semaphore, lat, lon),
        afetch_air_quality(aclient, semaphore, lat, lon),
        return_exceptions=True
    )

    if isinstance(weather_data, Exception):
        log.message(
            "WARNING",
            f"{city.name}: weather request failed: "
            f"{type(weather_data).__name__}: {weather_data}"
        )
        weather_data = None
    if isinstance(air_quality_data, Exception):
        log.message(
            "WARNING",
            f"{city.name}: air quality request failed: "
            f"{type(air_quality_data).__name__}: {air_quality_data}"
        )
        air_quality_data = None

    return RawCityData(
        city=city,
        weather_dict=weather_data,
        air_quality_dict=air_quality_data
    )

async def acollect(cities: list[City]) -> list[RawCityData]:
    start = time.perf_counter()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    async with httpx.AsyncClient() as aclient:
        results = list(await asyncio.gather(
            *(afetch_city(aclient, semaphore, city) for city in cities)
        ))

    log.message(
        "DEBUG",
        f"async fetch finished: cities={len(cities)} "
        f"elapsed={time.perf_counter() - start:.2f}s"
    )

    return results
