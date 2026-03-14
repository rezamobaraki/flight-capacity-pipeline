CREATE_TABLES_SCRIPT = """
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
"""

CHECK_IS_EMPTY = "SELECT COUNT(*) FROM capacity"

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

