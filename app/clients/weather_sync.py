import requests
import time
from ..models.environmental import City
from ..service.logger import log

cities = [
    City(name="Kyiv", latitude=50.4501, longitude=30.5234),
    City(name="Lviv", latitude=49.8397, longitude=24.0297),
    City(name="London", latitude=51.5074, longitude=-0.1278),
    City(name="Tokyo", latitude=35.6762, longitude=139.6503),
    City(name="New York", latitude=40.7128, longitude=-74.0060)
]

urls = {
    "geocoding": "https://geocoding-api.open-meteo.com/v1/search",
    "weather": "https://api.open-meteo.com/v1/forecast",
    "air_quality": "https://air-quality-api.open-meteo.com/v1/air-quality"
}

session = requests.Session()
timeout = 10

def fetch_weather(lat: float, lon: float):
    weather_url = urls["weather"]
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"]
    }
    response = session.get(url=weather_url, params=params, timeout=timeout)

    response.raise_for_status()

    log.message(
        "DEBUG",
        f"GET weather lat={lat} lon={lon} status={response.status_code}"
    )

    data = response.json()
    return data

def fetch_air_quality(lat: float, lon: float):
    air_url = urls["air_quality"]
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["pm2_5", "pm10"]
    }
    start = time.perf_counter()
    response = session.get(url=air_url, params=params, timeout=timeout)

    response.raise_for_status()

    log.message(
        "DEBUG",
        f"GET air_quality lat={lat} lon={lon} status={response.status_code}"
    )

    data = response.json()
    return data