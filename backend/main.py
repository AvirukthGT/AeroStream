from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from databricks import sql
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS (Allows your Vue app on port 5173 to talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/flights")
def get_flights():
    server = os.getenv("DB_SERVER")
    path = os.getenv("DB_PATH")
    token = os.getenv("DB_TOKEN")

    if not all([server, path, token]):
        print("MISSING CREDENTIALS:", server, path, "TOKEN_LEN:", len(token) if token else 0)
        raise ValueError("Missing Databricks credentials in .env")

    print(f"Connecting to Databricks: {server}")

    connection = sql.connect(
        server_hostname=server,
        http_path=path,
        access_token=token
    )

    cursor = connection.cursor()

    # 1. Query Presentation Layer (Analyzed Flights)
    # Filter for Australia and ordered by latest time
    query_analyzed = """
    SELECT 
        t1.icao24, t1.callsign, t1.origin_country, t1.velocity, t1.predicted_velocity, t1.efficiency_score,
        t2.latitude, t2.longitude, t2.baro_altitude,
        t2.temperature_c, t2.wind_speed_kmh, t2.wind_direction, t2.plane_heading, t2.wind_offset_angle, t2.weather_code,
        CASE 
            WHEN t1.efficiency_score < 80 THEN 'Inefficient'
            ELSE 'Optimal'
        END as status
    FROM presentation.flight_predictions t1
    JOIN presentation.flight_weather_master t2 
      ON t1.icao24 = t2.icao24 AND t1.request_time_utc = t2.request_time_utc
    ORDER BY t1.request_time_utc DESC
    LIMIT 200
    """
    cursor.execute(query_analyzed)
    columns_analyzed = [desc[0] for desc in cursor.description]
    analyzed_raw = [dict(zip(columns_analyzed, row)) for row in cursor.fetchall()]

    # Deduplicate Analyzed (Keep most recent if SQL returned multiple)
    analyzed_unique = {}
    for f in analyzed_raw:
        if f['icao24'] not in analyzed_unique:
            analyzed_unique[f['icao24']] = f
    
    analyzed_results = list(analyzed_unique.values())

    # 2. Query Silver Layer (Raw Global Flights)
    # Filter for Australia
    query_raw = """
    SELECT 
        icao24, callsign, origin_country, velocity, 
        latitude, longitude, true_track as plane_heading,
        baro_altitude, geo_altitude
    FROM silver.flights_parsed
    LIMIT 200
    """
    cursor.execute(query_raw)
    columns_raw = [desc[0] for desc in cursor.description]
    
    # Merge / Dedupe Raw against Analyzed
    # If a flight is already in analyzed_results, skip it in raw (to prefer the enriched version)
    existing_icaos = set(analyzed_unique.keys())
    final_results = analyzed_results[:] # Start with enriched

    for row in cursor.fetchall():
        flight = dict(zip(columns_raw, row))
        icao = flight['icao24']
        
        if icao not in existing_icaos:
            # Add defaults for missing analytics data
            flight.update({
                "predicted_velocity": None,
                "efficiency_score": None,
                "temperature_c": None,
                "wind_speed_kmh": None,
                "wind_direction": None,
                "wind_offset_angle": None,
                "weather_code": None,
                "status": "Raw" 
            })
            final_results.append(flight)
            existing_icaos.add(icao) # Prevent dupes within raw list too?

    cursor.close()
    connection.close()

    return final_results