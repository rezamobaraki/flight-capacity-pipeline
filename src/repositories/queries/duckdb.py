CREATE_TABLES_SCRIPT = """
    CREATE TABLE IF NOT EXISTS events (
        flight_id        VARCHAR,
        date             VARCHAR,
        time             VARCHAR,
        equipment        VARCHAR,
        flight_number    VARCHAR,
        origin_iata      VARCHAR,
        origin_icao      VARCHAR,
        destination_iata VARCHAR,
        destination_icao VARCHAR,
        operator         VARCHAR,
        registration     VARCHAR
    );

    CREATE TABLE IF NOT EXISTS aircraft (
        code_icao         VARCHAR PRIMARY KEY,
        code_iata         VARCHAR NOT NULL,
        full_name         VARCHAR NOT NULL,
        category          VARCHAR NOT NULL,
        average_speed_mph DOUBLE  NOT NULL,
        volume            DOUBLE  NOT NULL,
        payload           DOUBLE  NOT NULL
    );

    CREATE TABLE IF NOT EXISTS flights (
        flight_id        VARCHAR PRIMARY KEY,
        flight_number    VARCHAR,
        date             VARCHAR NOT NULL,
        origin_iata      VARCHAR,
        origin_icao      VARCHAR,
        destination_iata VARCHAR,
        destination_icao VARCHAR,
        equipment        VARCHAR,
        operator         VARCHAR,
        registration     VARCHAR
    );

    CREATE TABLE IF NOT EXISTS capacity (
        flight_id        VARCHAR PRIMARY KEY,
        flight_number    VARCHAR,
        date             VARCHAR NOT NULL,
        origin_iata      VARCHAR,
        origin_icao      VARCHAR,
        destination_iata VARCHAR,
        destination_icao VARCHAR,
        equipment        VARCHAR,
        aircraft_name    VARCHAR,
        category         VARCHAR,
        volume_m3        DOUBLE,
        payload_kg       DOUBLE,
        operator         VARCHAR
    );

    CREATE TABLE IF NOT EXISTS processed_files (
        filename     VARCHAR PRIMARY KEY,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_capacity_route
        ON capacity(origin_iata, destination_iata);
    CREATE INDEX IF NOT EXISTS idx_capacity_date
        ON capacity(date);
    CREATE INDEX IF NOT EXISTS idx_events_flight_id
        ON events(flight_id);
"""

CHECK_IS_EXISTS = "SELECT COUNT(*) FROM capacity"

CHECK_FILE_PROCESSED = "SELECT 1 FROM processed_files WHERE filename = $1"

MARK_FILE_PROCESSED = "INSERT OR IGNORE INTO processed_files (filename) VALUES ($1)"

# DuckDB window functions are fully vectorized — no behavioral difference
# from the SQLite version, just positional params instead of named params.
AGGREGATE_FLIGHTS = """
    INSERT OR REPLACE INTO flights (
        flight_id, flight_number, date,
        origin_iata, origin_icao,
        destination_iata, destination_icao,
        equipment, operator, registration
    )
    SELECT
        flight_id, flight_number, date,
        origin_iata, origin_icao,
        destination_iata, destination_icao,
        equipment, operator, registration
    FROM (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY flight_id
                ORDER BY date DESC, time DESC
            ) AS rn
        FROM events
    )
    WHERE rn = 1
"""

# LEFT JOIN identical to SQLite version — DuckDB uses hash joins by default
# which are faster than SQLite's nested-loop on large tables.
CALCULATE_CAPACITY = """
    INSERT OR REPLACE INTO capacity (
        flight_id, flight_number, date,
        origin_iata, origin_icao,
        destination_iata, destination_icao,
        equipment, aircraft_name, category,
        volume_m3, payload_kg, operator
    )
    SELECT
        f.flight_id,
        f.flight_number,
        f.date,
        f.origin_iata,
        f.origin_icao,
        f.destination_iata,
        f.destination_icao,
        f.equipment,
        COALESCE(a.full_name, 'Unknown Aircraft'),
        COALESCE(a.category,  'unknown_aircraft'),
        a.volume,
        a.payload,
        f.operator
    FROM flights f
    LEFT JOIN aircraft a ON f.equipment = a.code_icao
"""

INSERT_AIRCRAFT = """
    INSERT OR REPLACE INTO aircraft
        (code_icao, code_iata, full_name, category, average_speed_mph, volume, payload)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
"""

INSERT_EVENT = """
    INSERT INTO events (
        flight_id, date, time, equipment, flight_number,
        origin_iata, origin_icao, destination_iata, destination_icao,
        operator, registration
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
"""

INSERT_FLIGHT = """
    INSERT OR REPLACE INTO flights (
        flight_id, flight_number, date,
        origin_iata, origin_icao,
        destination_iata, destination_icao,
        equipment, operator, registration
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
"""

INSERT_CAPACITY = """
    INSERT OR REPLACE INTO capacity (
        flight_id, flight_number, date,
        origin_iata, origin_icao,
        destination_iata, destination_icao,
        equipment, aircraft_name, category,
        volume_m3, payload_kg, operator
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
"""

SELECT_ALL_FLIGHTS = "SELECT * FROM flights ORDER BY date"

SELECT_ALL_AIRCRAFT = "SELECT * FROM aircraft"

SELECT_CAPACITY_BASE = "SELECT * FROM capacity WHERE 1=1"

# Note: DuckDB does not need MAX(origin_iata) tricks here because we filter
# by exact match — origin and destination are always the same within a group.
SELECT_CAPACITY_SUMMARY_BASE = """
    SELECT
        date,
        $1                                        AS origin_iata,
        $2                                        AS destination_iata,
        COUNT(*)                                  AS total_flights,
        COALESCE(ROUND(SUM(volume_m3),  2), 0.0) AS total_volume_m3,
        COALESCE(ROUND(SUM(payload_kg), 2), 0.0) AS total_payload_kg
    FROM capacity
    WHERE 1=1
"""

# DuckDB-specific: bypass Python parsing entirely for trusted CSV sources.
# The DB engine reads the file in parallel using its multi-threaded scanner.
INGEST_CSV_DIRECT = """
    INSERT INTO events
    SELECT
        flight_id,
        date,
        time,
        equipment,
        flight      AS flight_number,
        origin_iata,
        origin_icao,
        destination_iata,
        destination_icao,
        operator,
        registration
    FROM read_csv_auto(
        $1,
        delim=';',
        header=true,
        ignore_errors=true
    )
    WHERE flight_id IS NOT NULL AND flight_id != ''
"""

# DuckDB-specific: write result set directly to disk without Python iteration.
EXPORT_CAPACITY_CSV = """
    COPY (
        SELECT * FROM capacity
        ORDER BY date, origin_iata, destination_iata
    )
    TO $1 (HEADER true, DELIMITER ',')
"""