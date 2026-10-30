from app.models.environmental import City, EnvironmentalModel
import time
import asyncio

cities = [
    City(name="Kyiv", latitude=50.4501, longitude=30.5234),
    City(name="Lviv", latitude=49.8397, longitude=24.0297),
    City(name="London", latitude=51.5074, longitude=-0.1278),
    City(name="Tokyo", latitude=35.6762, longitude=139.6503),
    City(name="New York", latitude=40.7128, longitude=-74.0060),
    City(name="Berlin", latitude=52.5200, longitude=13.4050),
    City(name="Paris", latitude=48.8566, longitude=2.3522),
    City(name="Warsaw", latitude=52.2297, longitude=21.0122),
    City(name="Madrid", latitude=40.4168, longitude=-3.7038),
    City(name="Rome", latitude=41.9028, longitude=12.4964),
    City(name="Toronto", latitude=43.6532, longitude=-79.3832),
    City(name="Sydney", latitude=-33.8688, longitude=151.2093),
    City(name="Singapore", latitude=1.3521, longitude=103.8198),
    City(name="Dubai", latitude=25.2048, longitude=55.2708),
    City(name="Sao Paulo", latitude=-23.5505, longitude=-46.6333)
]

cities_async = [
    City(name="Amsterdam", latitude=52.3676, longitude=4.9041),
    City(name="Vienna", latitude=48.2082, longitude=16.3738),
    City(name="Prague", latitude=50.0755, longitude=14.4378),
    City(name="Budapest", latitude=47.4979, longitude=19.0402),
    City(name="Stockholm", latitude=59.3293, longitude=18.0686),
    City(name="Oslo", latitude=59.9139, longitude=10.7522),
    City(name="Copenhagen", latitude=55.6761, longitude=12.5683),
    City(name="Helsinki", latitude=60.1699, longitude=24.9384),
    City(name="Dublin", latitude=53.3498, longitude=-6.2603),
    City(name="Lisbon", latitude=38.7223, longitude=-9.1393),
    City(name="Athens", latitude=37.9838, longitude=23.7275),
    City(name="Istanbul", latitude=41.0082, longitude=28.9784),
    City(name="Seoul", latitude=37.5665, longitude=126.9780),
    City(name="Bangkok", latitude=13.7563, longitude=100.5018),
    City(name="Mexico City", latitude=19.4326, longitude=-99.1332)
]

from app.service.collect import collect_city_data, async_collect_city_data
from app.storage.json_writer import json_writer, csv_writer
from app.service.logger import log

def sync_fetch():
    log.message("INFO", f"sync collection started: cities={len(cities)}")
    
    start = time.perf_counter()

    for city in cities:
        city_data = collect_city_data(city)
        if city_data is None:
            log.message("WARNING", f"{city.name}: skipping write due to collection error")
            continue
        json_writer.write_to_json(city_data)
        csv_writer.write_to_csv(city_data)
        print(f"Fetch data for {city_data.city}")
    
    ttx = time.perf_counter() - start
    
    log.message("INFO", f"sync collection finished: elapsed={ttx:.2f}s")
    print(f"Fetched data for {ttx}")

async def async_fetch():
    log.message("INFO", f"async collection started: cities={len(cities_async)}")
    
    start = time.perf_counter()
    
    env_data = await async_collect_city_data(cities=cities_async)
    
    ttx = time.perf_counter() - start
    
    try:
        json_writer.write_to_json(env_data)
        csv_writer.write_to_csv(env_data)
    except TypeError as e:
        log.message("ERROR", f"writing to file failed {type(e).__name__}: {e}")
        raise 

    log.message("INFO", f"async collection finished: elapsed={ttx:.2f}s")
    print("Execution time:", ttx)
    
if __name__ == "__main__":
    try:
        asyncio.run(async_fetch())
        sync_fetch()
    except Exception as e:
        log.message("ERROR", f"run failed: {type(e).__name__}: {e}")
        raise