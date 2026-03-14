CREATE_TABLES_SCRIPT = """
    CREATE TABLE IF NOT EXISTS events (
        flight_id TEXT,
        date TEXT,
        time TEXT,
        equipment TEXT,
        flight_number TEXT,
        origin_iata TEXT,
        origin_icao TEXT,
        destination_iata TEXT,
        destination_icao TEXT,
        operator TEXT,
        registration TEXT
    );

    CREATE TABLE IF NOT EXISTS aircraft (
        code_icao TEXT PRIMARY KEY,
        code_iata TEXT NOT NULL,
        full_name TEXT NOT NULL,
        category TEXT NOT NULL,
        average_speed_mph REAL NOT NULL,
        volume REAL NOT NULL,
        payload REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS flights (
        flight_id TEXT PRIMARY KEY,
        flight_number TEXT,
        date TEXT NOT NULL,
        origin_iata TEXT,
        origin_icao TEXT,
        destination_iata TEXT,
        destination_icao TEXT,
        equipment TEXT,
        operator TEXT,
        registration TEXT
    );

    CREATE TABLE IF NOT EXISTS capacity (
        flight_id TEXT PRIMARY KEY,
        flight_number TEXT,
        date TEXT NOT NULL,
        origin_iata TEXT,
        origin_icao TEXT,
        destination_iata TEXT,
        destination_icao TEXT,
        equipment TEXT,
        aircraft_name TEXT,
        category TEXT,
        volume_m3 REAL,
        payload_kg REAL,
        operator TEXT,
        FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
        FOREIGN KEY (equipment) REFERENCES aircraft(code_icao)
    );

    CREATE INDEX IF NOT EXISTS idx_capacity_route
        ON capacity(origin_iata, destination_iata);
    CREATE INDEX IF NOT EXISTS idx_capacity_date
        ON capacity(date);
    CREATE INDEX IF NOT EXISTS idx_events_flight_id
        ON events(flight_id);
"""

CHECK_IS_EXISTS = "SELECT COUNT(*) FROM capacity"

AGGREGATE_FLIGHTS = """
    INSERT OR IGNORE INTO flights (
        flight_id, date, equipment, flight_number,
        origin_iata, origin_icao, destination_iata, destination_icao,
        operator, registration
    )
    SELECT
        flight_id,
        MAX(date) as date,
        MAX(equipment) as equipment,
        MAX(flight_number) as flight_number,
        MAX(origin_iata) as origin_iata,
        MAX(origin_icao) as origin_icao,
        MAX(destination_iata) as destination_iata,
        MAX(destination_icao) as destination_icao,
        MAX(operator) as operator,
        MAX(registration) as registration
    FROM events
    GROUP BY flight_id
    HAVING MAX(equipment) != '' AND MAX(equipment) IS NOT NULL;
"""

INSERT_EVENT = """
    INSERT INTO events (
        flight_id, date, time, equipment, flight_number,
        origin_iata, origin_icao, destination_iata, destination_icao,
        operator, registration
    ) VALUES (
        :flight_id, :date, :time, :equipment, :flight,
        :origin_iata, :origin_icao, :destination_iata, :destination_icao,
        :operator, :registration
    );
"""

INSERT_AIRCRAFT = """
    INSERT OR REPLACE INTO aircraft (
        code_icao, code_iata, full_name, category, 
        average_speed_mph, volume, payload
    ) VALUES (
        :code_icao, 
        :code_iata, 
        :full_name, 
        :category, 
        :average_speed_mph, 
        :volume, 
        :payload
    )
"""

INSERT_FLIGHT = """
    INSERT OR REPLACE INTO flights (
        flight_id, flight_number, date, origin_iata, origin_icao, 
        destination_iata, destination_icao, equipment, operator, registration
    ) VALUES (
        :flight_id, 
        :flight_number, 
        :date, 
        :origin_iata, 
        :origin_icao, 
        :destination_iata, 
        :destination_icao, 
        :equipment, 
        :operator, 
        :registration
    )
"""

INSERT_CAPACITY = """
    INSERT OR REPLACE INTO capacity (
        flight_id, flight_number, date, origin_iata, origin_icao, 
        destination_iata, destination_icao, equipment, aircraft_name, 
        category, volume_m3, payload_kg, operator
    ) VALUES (
        :flight_id, 
        :flight_number, 
        :date, 
        :origin_iata, 
        :origin_icao, 
        :destination_iata, 
        :destination_icao, 
        :equipment, 
        :aircraft_name, 
        :category, 
        :volume_m3, 
        :payload_kg, 
        :operator
    )
"""

SELECT_ALL_AIRCRAFT = "SELECT * FROM aircraft"

SELECT_CAPACITY_BASE = "SELECT * FROM capacity WHERE 1=1"

SELECT_CAPACITY_SUMMARY = """
    SELECT
        date,
        COUNT(*) as total_flights,
        ROUND(SUM(volume_m3), 2) as total_volume_m3,
        ROUND(SUM(payload_kg), 2) as total_payload_kg
    FROM capacity
    WHERE origin_iata = :origin AND destination_iata = :destination
"""
