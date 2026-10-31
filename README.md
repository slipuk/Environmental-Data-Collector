# Async Environmental Data Collector
## Problem
The problem of the modern world is that we have access to large amounts of data and materials but cannot use them properly because of a lack of organization. Today big data is being fed to machine learning models, but it is useless without structure.

Environmental data collector is the solution to this problem. It fetches the data the user needs and stores it in a predictable way, without surprises, unexpected data forms, or undefined behaviour.

## Architecture
All requests go through the client modules, which fetch data from the weather API. All fetched information goes through validation (checking data correctness), normalization (transforming raw response strings into objects), and record building (creating one object with all needed information). Clean data is serialized to JSON and CSV and written to disk. Every step of the program is logged with a unified log structure.

```log
[<time>][<type of information INFO | DEBUG | WARNING | ERROR>] message
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
│       └── file_writer.py
├── data
│   ├── environmental_data.csv
│   └── environmental_data.jsonl
├── logs
│   └── log.log
└── README.md
```

The main engine of the data collector is the clients folder; it fetches data in two ways: synchronous and asynchronous.

The models folder defines the structure of the data.
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
This is the main dataclass for structuring data.

Service folder:
```transform.py```: validates the data and constructs data models
```collect.py```: combines clients and transformation
```logger.py```: logging service
```wrappers.py```: decorators for timing functions

Storage folder saves transformed data in JSON and CSV formats.
Logs are created for debugging.

## Data Sources
[Open-Meteo](https://open-meteo.com)
## Installation

This project uses a virtual environment. Run these commands from the project root.

1. Clone the repository and enter its directory:

```bash
git clone https://github.com/slipuk/Environmental-Data-Collector.git
cd Environmental-Data-Collector
```

2. Create and activate a virtual environment.

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (cmd)

```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

Run the collector from the project root:

```bash
python -m app.main
```

This runs the asynchronous collection first, then the synchronous collection. Results are appended to `data/environmental_data.jsonl` and `data/environmental_data.csv`, and logs are written to `logs/log.log`.

Note: run it from the repository root, because `data/` and `logs/` paths are relative to the current directory.

## Output
Output goes to the log file, JSON and CSV files, and the terminal.
#### Terminal
```bash
INFO async_fetch finished: elapsed=0.807
INFO sync_fetch finished: elapsed=1.514
```
#### JSON output
Each line is one JSON object (NDJSON). The example below is formatted for readability:
```json
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
```csv
city,latitude,longitude,collected_at,weather_measured_at,air_quality_measured_at,temperature,humidity,wind_speed,pm25,pm10
Amsterdam,52.3676,4.9041,2026-10-31T11:17:01+00:00,2026-10-31T11:15:00+00:00,2026-10-31T11:00:00+00:00,8.9,89,9.4,10.0,12.6
```
## Error Handling
Error handling is implemented with `try...except`. When an error occurs, failed records are skipped and all relevant information is logged, including the error type and message.

```python
try:
    raw_cities = await acollect(cities)
except Exception as e:
    log.message("ERROR", f"async collection failed: {type(e).__name__}: {e}")
    return []
```

## Sync vs Async Experiment
Terminal output:
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

This project taught me:

- basic Python project structure and planning
- data modeling
- synchronous and asynchronous I/O
- debugging and optimization