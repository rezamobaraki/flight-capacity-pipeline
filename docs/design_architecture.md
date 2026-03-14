# Rotate Cargo Capacity — Design & Architecture

> **Design Flow:**
> 0.Understanding → 1.Requirements → 2.Core Entity → 3.API/Interface → 4.Data Flow → 5.High-level Design → 6.Deep Dive / Low-level Design
>
> - High-level Design → Requirements **[Primary Goal: Satisfy Functional Requirements]**
> - Deep Dive / Low-level Design → Requirements **[Primary Goal: Satisfy Non-Functional Requirements]**

---

## 0. Understanding

### Problem Statement

**Rotate** helps airlines make data-driven commercial decisions. A core metric is **available cargo capacity** — how much weight (kg) and volume (m³) can be shipped between airports given current flights and aircraft.

### Input Data

| Dataset | Format | Size | Description |
|---|---|---|---|
| `flight_events/*.csv` | Semicolon-delimited CSV, 7 files (Oct 3–9, 2022) | **700K rows, 76 MB** | Real-time ADS-B events from Flightradar24 |
| `airplane_details_original.json` | JSONL (one JSON object per line) | **100 rows, 16 KB** | Aircraft specs: payload (kg) + volume (m³) |

### Key Data Characteristics

- **Delimiter is `;`** — not comma, despite the `.csv` extension
- **Multiple events per flight** — a single `flight_id` emits 2–6 events (gate_departure, takeoff, cruising, descent, landed, gate_arrival)
- **Missing fields** — ~19% of rows have empty `flight`, `origin_iata`, or `origin_icao`
- **Unmatched equipment** — only 100 aircraft types provided; 612 unique equipment codes in events have no match
- **Join key** — `flight_events.equipment` → `airplane_details.code_icao`

---

## 1. Requirements

### Functional Requirements (FR)

| ID | Requirement | Maps to |
|----|-------------|---------|
| FR-1 | Load and model flight event CSVs + aircraft JSONL so data is queryable and reusable | Challenge Q1 |
| FR-2 | Deduplicate events → one row per `flight_id`, then join with aircraft details to produce a capacity table (payload_kg, volume_m3 per flight) | Challenge Q2 |
| FR-3 | Expose an API endpoint accepting two airports → returns total capacity per day | Challenge Q3 |
| FR-4 | Handle missing/dirty data gracefully (empty fields, unmatched equipment codes) | Challenge Q2 hint |

### Non-Functional Requirements (NFR)

| ID | Requirement | Decision |
|----|-------------|----------|
| NFR-1 | Process 700K rows in reasonable time (<30s pipeline, <100ms queries) | Streaming loaders → SQLite with indexes |
| NFR-2 | Simple, readable, no over-engineering | Pure Python + Pydantic + stdlib `csv` + `sqlite3` |
| NFR-3 | Testable at every layer independently | Layered architecture with dependency injection |
| NFR-4 | Minimal external dependencies | Only `fastapi`, `uvicorn`, `pydantic`, `httpx`(dev) |

---

## 2. Core Entities

Four Pydantic domain models represent the data at each stage of the pipeline:

```
FlightEvent          Aircraft            Flight              Capacity
─────────────       ─────────────       ──────────────      ──────────────
address              code_iata           flight_id           flight_id
altitude             code_icao ←──┐     flight_number       flight_number
callsign             full_name    │     date                date
date                 category     │     origin_iata         origin_iata
destination_iata     avg_speed    │     origin_icao         origin_icao
destination_icao     volume ──────┼──→  destination_iata    destination_iata
equipment ───────────payload ─────┘     destination_icao    destination_icao
event                                   equipment           equipment
flight                                  operator            aircraft_name
flight_id                               registration        category
latitude                                                    volume_m3  ← from Aircraft
longitude                                                   payload_kg ← from Aircraft
operator                                                    operator
origin_iata
origin_icao
registration
time
```

### Why Pydantic for domains (not dataclasses)?

- **Validation on parse** — CSV rows are raw strings; `field_validator` coerces altitude `str→int`, coordinates `str→float`, empty strings → defaults
- **Schema consistency** — same model validates input AND serializes to API responses
- **One model per stage** — `FlightEvent` (raw) → `Flight` (deduplicated) → `Capacity` (joined)

---

## 3. API / Interface

### CLI Entry Point

```
python -m src.main
```
Runs the full pipeline: load → aggregate → calculate → persist to SQLite.

### REST API (FastAPI)

```
uvicorn src.handlers:create_app --factory --port 8000
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/capacity?origin=X&destination=Y&date=Z` | Per-flight capacity list, all filters optional |
| `GET` | `/api/v1/capacity/summary?origin=X&destination=Y` | Daily aggregated summary for a route (Q3 answer) |

### Response Schemas

```
CapacityListResponse          DailySummaryListResponse
├── count: int                ├── count: int
└── capacities: [             └── summaries: [
      CapacityResponse              DailySummaryResponse
      ├── flight_id                 ├── date
      ├── flight_number             ├── origin_iata
      ├── date                      ├── destination_iata
      ├── origin_iata               ├── total_flights
      ├── destination_iata          ├── total_volume_m3
      ├── equipment                 └── total_payload_kg
      ├── aircraft_name          ]
      ├── volume_m3
      ├── payload_kg
      └── operator
    ]
```

---

## 4. Data Flow

```
                          ┌─────────────────────────────────────┐
                          │           DATA SOURCES               │
                          │                                     │
                          │  flight_events/*.csv   aircraft.json │
                          └─────────┬───────────────────┬───────┘
                                    │                   │
                              ┌─────▼─────┐       ┌────▼────────┐
                              │EventLoader│       │AircraftLoader│
                              │ (stream)  │       │  (stream)   │
                              └─────┬─────┘       └────┬────────┘
                                    │                   │
                             Iterator[FlightEvent]   list[Aircraft]
                                    │                   │
                              ┌─────▼──────────┐        │
                              │FlightAggregator│        │
                              │  (deduplicate) │        │
                              └─────┬──────────┘        │
                                    │                   │
                              list[Flight]              │
                                    │                   │
                              ┌─────▼───────────────────▼──┐
                              │     CapacityService         │
                              │  (join flight + aircraft)   │
                              └─────┬──────────────────────┘
                                    │
                              list[Capacity]
                                    │
                              ┌─────▼──────────┐
                              │SQLiteRepository│
                              │   (persist)    │
                              └─────┬──────────┘
                                    │
                              ┌─────▼──────────┐
                              │  FastAPI API    │
                              │  (query + serve)│
                              └────────────────┘
```

### Key Design: Streaming Loaders → Batch Services

- **EventLoader.stream()** yields `FlightEvent` one at a time (generator) — never loads all 700K rows into memory at once
- **FlightAggregator.aggregate()** collects events into a `dict[flight_id → list[events]]` — this is the materialization point, unavoidable for dedup
- **CapacityService.calculate()** iterates flights once, looks up aircraft via `dict[code_icao → Aircraft]` — O(1) per flight
- **SQLiteRepository** persists results — so queries are instant after pipeline completes

---

## 5. High-level Design (Satisfies Functional Requirements)

### Project Structure

```
rotate/
├── src/
│   ├── core/                          # Configuration & wiring
│   │   ├── settings.py                #   Paths, log config
│   │   └── app_container.py           #   Dependency injection (manual)
│   │
│   ├── domains/                       # Pydantic domain models
│   │   ├── flight_event.py            #   Raw CSV row (with field validators)
│   │   ├── aircraft.py                #   Aircraft specs (JSONL row)
│   │   ├── flight.py                  #   Deduplicated flight (1 per flight_id)
│   │   └── capacity.py                #   Final output (flight + aircraft joined)
│   │
│   ├── errors/                        # Exception hierarchy
│   │   ├── app.py                     #   AppError base (with status_code)
│   │   ├── database.py                #   DatabaseNotInitializedError
│   │   ├── domain.py                  #   DomainError base
│   │   └── file.py                    #   DataFileNotFoundError, NoFlightDataError
│   │
│   ├── services/                      # Business logic (pure Python)
│   │   ├── event_loader.py            #   CSV → Iterator[FlightEvent] (streaming)
│   │   ├── aircraft_loader.py         #   JSONL → Iterator[Aircraft] (streaming)
│   │   ├── flight_aggregator.py       #   Events → deduplicated Flights
│   │   ├── capacity_service.py        #   Flights + Aircraft → Capacity list
│   │   └── pipeline_service.py        #   Orchestrates: load → aggregate → calculate → save
│   │
│   ├── repositories/                  # Data persistence
│   │   ├── interfaces/                #   AbstractRepository (contract)
│   │   └── sqlite_repository.py       #   SQLite implementation
│   │
│   ├── schemas/                       # API serialization (Pydantic)
│   │   ├── requests/                  #   (reserved for future POST endpoints)
│   │   └── responses/                 #   CapacityResponse, DailySummaryResponse, etc.
│   │
│   ├── handlers/                      # FastAPI delivery layer
│   │   ├── __init__.py                #   create_app(), lifespan, error handler
│   │   ├── health.py                  #   GET /health
│   │   └── capacity.py                #   GET /api/v1/capacity, /capacity/summary
│   │
│   └── main.py                        # CLI entry: runs pipeline then exits
│
├── tests/                             # pytest suite
│   ├── conftest.py                    #   Fixtures: tmp data, container, sample objects
│   ├── test_loaders.py                #   EventLoader + AircraftLoader
│   ├── test_aggregator.py             #   FlightAggregatorService
│   ├── test_capacity.py               #   CapacityService
│   ├── test_repository.py             #   SQLiteRepository
│   └── test_api.py                    #   FastAPI endpoints (async)
│
└── data/
    ├── flight_events/*.csv            # 7 daily CSV files (input)
    ├── airplane_details_original.json # Aircraft specs (input)
    └── rotate.db                      # SQLite database (output, gitignored)
```

### Layer Responsibilities

| Layer | Knows About | Depends On | Never Touches |
|-------|-------------|------------|---------------|
| **domains/** | Only itself (data shape) | `pydantic` | DB, files, HTTP |
| **errors/** | Only itself (exception hierarchy) | Python `Exception` | Anything else |
| **services/** | Domains, errors | `csv`, `json`, domain models | DB, HTTP |
| **repositories/** | Domains, errors | `sqlite3`, domain models | File parsing, HTTP |
| **handlers/** | Schemas, repositories | `fastapi`, repository interface | File parsing, services |
| **core/** | Everything (wiring) | All layers | Business logic |

### Why Services (not Use Cases)?

The project has 4 operations total. A use-case pattern (1 class per operation) would create 4 files with 4 classes each containing a single `execute()` method — indirection for no gain. Services group related operations into cohesive units:

- `EventLoader` — one responsibility: parse CSV files
- `AircraftLoader` — one responsibility: parse JSONL file
- `FlightAggregator` — one responsibility: deduplicate events into flights
- `CapacityService` — one responsibility: join flights with aircraft
- `PipelineService` — orchestrate the above in sequence

---

## 6. Deep Dive / Low-level Design (Satisfies Non-Functional Requirements)

### 6.1 Streaming Loaders (NFR-1: Performance)

**Problem:** 700K rows × Pydantic validation = potentially slow if loaded all at once.

**Solution:** Both loaders use Python generators:

```python
# event_loader.py — yields one FlightEvent at a time
def stream(self) -> Iterator[FlightEvent]:
    for csv_file in sorted(self._data_dir.glob("*.csv")):
        with open(csv_file) as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                yield FlightEvent.model_validate(row)
```

**Effect:** At any point, only one CSV file's file handle is open, and only one row is in memory. The downstream `FlightAggregator` materializes into a dict (unavoidable for grouping), but the I/O is lazy.

### 6.2 Flight Deduplication Strategy (FR-2)

**Problem:** A flight_id has 2–6 event rows. We need exactly one row per flight.

**Solution:** `FlightAggregator` groups events by `flight_id`, then consolidates fields using **first-non-empty** strategy:

```python
def _build_flight(self, flight_id, events):
    # Some events have origin_iata, others don't.
    # Take the first non-empty value across all events for each field.
    return Flight(
        origin_iata=self._first_nonempty(e.origin_iata for e in events),
        ...
    )
```

Flights with **no equipment code** are skipped entirely — they cannot contribute to capacity calculation.

### 6.3 SQLite as Persistence Layer (NFR-1: Query Speed)

**Why SQLite instead of in-memory only?**

| Concern | Decision |
|---------|----------|
| Pipeline runs once (~15s), queries should be instant | SQLite persists results; API reads from DB with no re-processing |
| Route + date filtering on 106K capacity records | Indexes on `(origin_iata, destination_iata)` and `(date)` |
| API restarts shouldn't re-process 700K events | `is_empty()` check at startup — skip pipeline if data exists |
| No extra dependencies | `sqlite3` is Python stdlib |

**Schema design:**

```sql
-- Three tables mirror the three pipeline stages
aircraft   (code_icao PK)           -- 100 rows, lookup table
flights    (flight_id PK)           -- 198K rows, deduplicated
capacity   (flight_id PK, FK→flights, FK→aircraft)  -- 106K rows, joined

-- Indexes for API query patterns
idx_capacity_route  ON capacity(origin_iata, destination_iata)
idx_capacity_date   ON capacity(date)
```

### 6.4 Dependency Injection via AppContainer (NFR-3: Testability)

**No DI framework.** A simple `AppContainer` class wires everything:

```python
class AppContainer:
    def __init__(self, settings=None):
        self.settings = settings or Settings()
        self.repository = SQLiteRepository(self.settings.DATABASE_PATH)
        self.aircraft_loader = AircraftLoader(self.settings.AIRCRAFT_FILE)
        self.event_loader = EventLoader(self.settings.FLIGHT_EVENTS_DIR)
        self.aggregator = FlightAggregatorService()
        self.capacity_service = CapacityService()
        self.pipeline = PipelineService(...)
```

Tests inject a custom `Settings` pointing to temp directories:

```python
@pytest.fixture
def settings(tmp_data_dir):
    s = Settings()
    s.DATABASE_PATH = tmp_data_dir / "test.db"  # isolated test DB
    ...
```

### 6.5 Error Hierarchy (NFR-2: Simplicity)

```
Exception
└── AppError (status_code=500)
    ├── NotFoundError (404)
    │   ├── DataFileNotFoundError
    │   └── AircraftNotFoundError
    ├── AppValidationError (422)
    │   └── NoFlightDataError
    └── DatabaseError (500)
        └── DatabaseNotInitializedError
```

The `status_code` attribute lets the FastAPI error handler map any `AppError` subclass to the correct HTTP response without if/elif chains.

### 6.6 API Startup Lifecycle (NFR-1)

```python
@asynccontextmanager
async def lifespan(app):
    container.repository.initialize()
    if container.repository.is_empty():
        container.pipeline.run()     # Only runs on first start
    yield
    container.repository.close()
```

First launch: pipeline processes all data (~15s), persists to SQLite.
Subsequent launches: data already in DB, starts in <1s.

---

## Data Observations (Challenge Q2 Hint)

| Observation | Impact | How We Handle It |
|---|---|---|
| CSV delimiter is `;` not `,` | Would parse as 1 column if using default comma | `csv.DictReader(delimiter=";")` |
| ~19% rows have empty `flight`, `origin_iata` | Flights without origin/dest can't form a route | `_first_nonempty` across events; still stored if at least one event has the field |
| 612 equipment codes not in aircraft details | Can't calculate capacity for ~93K flights | Logged as warning; flights skipped in capacity table |
| `flight_id` can be empty | Some rows are ground movements or test signals | Filtered out in `FlightAggregator` |
| Some `flight_id`s have no equipment across all events | No aircraft to join | Filtered out in `_build_flight()` |

### Pipeline Statistics (Real Data)

```
Aircraft loaded:        100
Events loaded:      700,000  (100K × 7 files)
Events grouped:     202,407  (unique flight_ids)
Flights built:      198,821  (after filtering no-equipment)
Capacity computed:  106,086  (after joining with 100 aircraft types)
Unmatched equip:        612  (codes with no aircraft details)
```

---

## Technology Choices Summary

| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| Processing model | **Batch pipeline** | Streaming (Kafka/Flink) | Historical data, 76 MB, no real-time need |
| Data parsing | **Pure Python** (`csv`, `json`) | Polars/Pandas | Simpler; Pydantic validation per row; no extra deps |
| Domain models | **Pydantic BaseModel** | dataclasses | Need validation on CSV parse + API serialization |
| Persistence | **SQLite** | In-memory only / PostgreSQL | Survives restarts; stdlib; indexes for fast queries |
| Architecture | **Services** | Use-case classes | 4 operations don't need 4 classes with 1 method each |
| DI | **Manual AppContainer** | dependency-injector lib | One file, zero magic, easy to test |
| API | **FastAPI** | Flask/Django | Async, auto-docs, Pydantic-native |
| Testing | **pytest** | unittest | Fixtures, parametrize, cleaner syntax |

