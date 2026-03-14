import csv
import glob
import json
import os
import sqlite3

# Configuration
DB_PATH = "data/capacity.db"
AIRCRAFT_FILE = "data/airplane_details.json"
EVENTS_DIR = "data/flight_events/*.csv"

def init_db():
    """Initialize the SQLite database schema."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH) # Start fresh for this run
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Aircraft table (for reference)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aircraft (
            code_icao TEXT PRIMARY KEY,
            volume REAL,
            payload REAL
        )
    ''')
    
    # Flights table (The Capacity Table)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            flight_id TEXT PRIMARY KEY,
            date TEXT,
            origin TEXT,
            destination TEXT,
            equipment TEXT,
            capacity_volume REAL,
            capacity_weight REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized.")

def load_aircraft_data() -> dict[str, dict[str, float]]:
    """
    Load aircraft details into a dictionary for fast lookup.
    Returns: {code_icao: {'volume': float, 'payload': float}}
    """
    aircraft_map = {}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if not os.path.exists(AIRCRAFT_FILE):
        print(f"Warning: {AIRCRAFT_FILE} not found.")
        return {}

    with open(AIRCRAFT_FILE) as f:
        for line in f:
            try:
                data = json.loads(line)
                code_icao = data.get('code_icao')
                if code_icao:
                    details = {
                        'volume': data.get('volume', 0.0),
                        'payload': data.get('payload', 0.0)
                    }
                    aircraft_map[code_icao] = details
                    
                    # Store in DB as well for completeness
                    cursor.execute(
                        "INSERT OR IGNORE INTO aircraft (code_icao, volume, payload) VALUES (?, ?, ?)",
                        (code_icao, details['volume'], details['payload'])
                    )
            except json.JSONDecodeError:
                continue
                
    conn.commit()
    conn.close()
    print(f"Loaded {len(aircraft_map)} aircraft types.")
    return aircraft_map

def process_flight_events(aircraft_map: dict[str, dict[str, float]]):
    """
    Process all flight event CSV files and populate the flights table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    csv_files = glob.glob(EVENTS_DIR)
    print(f"Found {len(csv_files)} event files.")
    
    total_records = 0
    
    # To handle multiple events per flight, we use INSERT OR IGNORE
    # and then potentially UPDATE if we find better data (e.g. Origin is present)
    # But for a simple solution, we'll assume the *first* valid entry we see is good enough,
    # or better: we assume the 'equipment' is constant. 
    # The trickiest part is Origin/Dest might be missing in some events.
    
    for file_path in sorted(csv_files):
        print(f"Processing {file_path}...")
        with open(file_path) as f:
            # Check delimiter using sniffer or just assume semicolon based on earlier `head`
            # The `head` output showed semicolons.
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                total_records += 1
                flight_id = row.get('flight_id')
                if not flight_id:
                    continue
                
                equipment = row.get('equipment')
                origin = row.get('origin_iata')
                destination = row.get('destination_iata')
                date = row.get('date')
                
                # Check capacity
                capacity = aircraft_map.get(equipment)
                if capacity:
                    cap_vol = capacity['volume']
                    cap_weight = capacity['payload']
                else:
                    cap_vol = 0.0
                    cap_weight = 0.0
                
                # Insert or Ignore
                # This ensures we have the flight.
                # If we want to enrich missing origin/dest later, we'd need an UPDATE logic.
                # For simplicity, let's try to capture the info if we have it.
                
                # We'll use a transaction per batch or just one per file for speed.
                
                cursor.execute('''
                    INSERT OR IGNORE INTO flights 
                    (flight_id, date, origin, destination, equipment, capacity_volume, capacity_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (flight_id, date, origin, destination, equipment, cap_vol, cap_weight))
                
                # If the insert was ignored (flight exists), we might want to update fields if they were null
                if cursor.rowcount == 0:
                     # Flight exists. Check if we can improve data.
                     # Only update if current stored value is null/empty and new value is present.
                     if origin:
                         cursor.execute("UPDATE flights SET origin = ? WHERE flight_id = ? AND (origin IS NULL OR origin = '')", (origin, flight_id))
                     if destination:
                         cursor.execute("UPDATE flights SET destination = ? WHERE flight_id = ? AND (destination IS NULL OR destination = '')", (destination, flight_id))
                     if equipment and capacity: # Update capacity if we found equipment later
                         cursor.execute('''
                            UPDATE flights 
                            SET equipment = ?, capacity_volume = ?, capacity_weight = ? 
                            WHERE flight_id = ? AND (equipment IS NULL OR equipment = '')
                         ''', (equipment, cap_vol, cap_weight, flight_id))

        conn.commit()
    
    conn.close()
    print(f"Processed {total_records} records.")

def generate_report():
    """Generate a simple CLI report (Question 3 - Option 2 style)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n--- Capacity Report ---")
    
    # Total Capacity
    cursor.execute("SELECT SUM(capacity_volume), SUM(capacity_weight), COUNT(*) FROM flights")
    row = cursor.fetchone()
    print(f"Total Flights Processed: {row[2]}")
    print(f"Total Volume Capacity: {row[0]:,.2f} m3")
    print(f"Total Weight Capacity: {row[1]:,.2f} kg")
    
    # Missing Capacity Stats
    cursor.execute("SELECT COUNT(*) FROM flights WHERE capacity_volume = 0")
    row_missing = cursor.fetchone()
    missing_count = row_missing[0] if row_missing else 0
    print(f"Flights with unknown aircraft capacity: {missing_count}")
    
    # Analyze missing equipment
    print("\nTop 10 Missing Equipment Codes:")
    cursor.execute('''
        SELECT equipment, COUNT(*) as c
        FROM flights
        WHERE capacity_volume = 0 OR capacity_volume IS NULL
        GROUP BY equipment
        ORDER BY c DESC
        LIMIT 10
    ''')
    for r in cursor.fetchall():
        print(f"Code: '{r[0]}' - Count: {r[1]}")

    # Top 5 Routes by Capacity
    print("\nTop 5 Routes by Daily Volume:")
    cursor.execute('''
        SELECT date, origin, destination, SUM(capacity_volume) as daily_vol
        FROM flights
        WHERE origin != '' AND destination != ''
        GROUP BY date, origin, destination
        ORDER BY daily_vol DESC
        LIMIT 5
    ''')
    for r in cursor.fetchall():
        print(f"{r[0]} | {r[1]} -> {r[2]} : {r[3]:,.2f} m3")

    conn.close()

def export_results_csv():
    """Export the processed capacity table to CSV (Question 2 Deliverable)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\nExporting capacity table to 'capacity_table.csv'...")
    cursor.execute("SELECT * FROM flights")
    rows = cursor.fetchall()
    
    # Get column names
    headers = [description[0] for description in cursor.description]
    
    with open('capacity_table.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    conn.close()
    print("Export complete.")

if __name__ == "__main__":
    init_db()
    aircraft_map = load_aircraft_data()
    process_flight_events(aircraft_map)
    generate_report()
    export_results_csv()
