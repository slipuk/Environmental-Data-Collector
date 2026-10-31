# Async Environmental Data Collector
## Problem
The problem of modern world is that we have access to large amounts of data and materials but cannot use them in proper way because of lack of organization. Today big data is being fed to machine learning models, but it is useless without structure.

Environmental data collector is the solution to this problem. It fetches data user needs and store it in predicted way, without suprises, unexpected data forms and without undefined behaviour.

## Architecture
All of the requests go through clients programs, they fetch all of the data from weather API. All of the fetched information goes through validation (checks the data correctness), normalization (transforms data from raw responses string responses to objects), building record (creating one object with all needed information). Clean information is parsed back to JSON and strings to be written to disk. Every step of the program is being logged with unified log structure

```log
[<time>][<type of information INFO | WARNING | ERROR>] message
[2026-10-30T13:45:12][INFO] async collection started: cities=15
[2026-10-30T13:45:17][WARNING] skipping 2 records with failed requests
```

## Project Structure
```bash
├── app
│   ├── clients
│   │   ├── weather_async.py
│   │   └── weather_sync.py
│   ├── main.py
│   ├── models
│   │   └── environmental.py
│   ├── service
│   │   ├── collect.py
│   │   ├── logger.py
│   │   ├── transform.py
│   │   └── wrappers.py
│   └── storage
│       └── json_writer.py
├── data
│   ├── environmental_data.csv
│   └── environmental_data.jsonl
├── logs
│   └── log.log
└── README.md
```

The main engine of data collector is clients folder, it fetches data in two ways: synchronious and asynchronious

Models folder define the structure of data.
```python 
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
```
The main dataclass for structuring data

Service folder:
```transform.py```: validates the data and constructs data models
```colect.py```: combines clients and transformation
```logger.py```: logging service
```wrappers.py```: wrapping functions

Storage folder saves transformed data to json and csv format
Logs: log created for debugging

## Data Sources
[Open-Meteo](https://open-meteo.com)
## Installation
It is better install to virtual environment
#### Linux / MacOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```
#### Windows
```bash
python -m venv c:\path\to\myenv
```
##### cmd
```bash
<venv>\Scripts\activate.bat
```
##### PowerShell
```bash
<venv>\Scripts\Activate.ps1
```

```bash
git clone https://github.com/slipuk/Environmental-Data-Collector.git
pip install -r requirements.txt
```
## Usage

```bash
python -m app.main
```
## Output
Output goes to many places like log file, json and csv file and terminal
#### Terminal
```bash
INFO async_fetch finished: elapsed=0.807
INFO sync_fetch finished: elapsed=1.514
```
#### JSON output
```
{
    "city": "Amsterdam", 
    "latitude": 52.3676, 
    "longitude": 4.9041, 
    "collected_at": "2026-10-30T07:41:18+00:00", 
    "weather_measured_at": "2026-10-30T07:30:00+00:00",
    "air_quality_measured_at": "2026-10-30T07:00:00+00:00", 
    "temperature": 9.4, 
    "humidity": 97, 
    "wind_speed": 5.8, 
    "pm25": 27.7, 
    "pm10": 30.9
}
```
#### CSV output
```bash
city,latitude,longitude,collected_at,weather_measured_at,air_quality_measured_at,temperature,humidity,wind_speed,pm25,pm10
Amsterdam,52.3676,4.9041,2026-10-30 10:54:30.790668+00:00,2026-10-30 10:45:00+00:00,2026-10-30 10:00:00+00:00,11.8,91,7.6,31.3,35.3
```
## Error Handling
Error handling is implemented in try...except structure and when errors occur functions return None and log all needed information, type of error and error message

```python
try:
    raw_cities = await acollect(cities)
except Exception as e:
    log.message("ERROR", f"async collection failed: {type(e).__name__}: {e}")
    return []
```

## Sync vs Async Experiment
```bash
run 1)
INFO async_fetch finished: elapsed=0.842
INFO sync_fetch finished: elapsed=1.844

run 2)
INFO async_fetch finished: elapsed=0.796
INFO sync_fetch finished: elapsed=1.747

run 3)
INFO async_fetch finished: elapsed=0.929
INFO sync_fetch finished: elapsed=1.859

run 4)
INFO async_fetch finished: elapsed=0.815
INFO sync_fetch finished: elapsed=1.679
```

## What I Learned

There have been learned:
basic python project structure and plan of actions
data modeling,
sync and async I/0
debugging and optimization