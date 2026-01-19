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
    allow_origins=[
        "http://localhost:5173", 
        "https://aero-stream-virid.vercel.app"
    ], 
    allow_methods=["*"],
    allow_headers=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AeroStream API is running. Access endpoints at /api/flights"}

@app.get("/api/flights")
def get_flights():
    server = os.getenv("DB_SERVER")
    path = os.getenv("DB_PATH")
    token = os.getenv("DB_TOKEN")

    if not all([server, path, token]):
        raise ValueError("Missing Databricks credentials in .env")

    connection = sql.connect(
        server_hostname=server,
        http_path=path,
        access_token=token
    )

    cursor = connection.cursor()

    # ---------------------------------------------------------
    # FIX 1: Use ROW_NUMBER() to get only the LATEST row per plane
    # ---------------------------------------------------------
    query_analyzed = """
    WITH LatestPositions AS (
        SELECT 
            t1.icao24, t1.callsign, t1.origin_country, t1.velocity, 
            t1.predicted_velocity, t1.efficiency_score, t1.request_time_utc,
            t2.latitude, t2.longitude, t2.baro_altitude,
            t2.temperature_c, t2.wind_speed_kmh, t2.wind_direction, 
            t2.plane_heading, t2.wind_offset_angle, t2.weather_code,
            -- Assign a rank: 1 = Latest, 2 = Previous, etc.
            ROW_NUMBER() OVER(PARTITION BY t1.icao24 ORDER BY t1.request_time_utc DESC) as rn
        FROM presentation.flight_predictions t1
        JOIN presentation.flight_weather_master t2 
          ON t1.icao24 = t2.icao24 AND t1.request_time_utc = t2.request_time_utc
    )
    SELECT 
        icao24, callsign, origin_country, velocity, predicted_velocity, efficiency_score,
        latitude, longitude, baro_altitude,
        temperature_c, wind_speed_kmh, wind_direction, plane_heading, wind_offset_angle, weather_code,
        CASE 
            WHEN efficiency_score < 80 THEN 'Inefficient'
            ELSE 'Optimal'
        END as status
    FROM LatestPositions
    WHERE rn = 1  -- Only keep the single latest ping per plane
    LIMIT 1000    -- Now this limit applies to UNIQUE planes, not rows
    """
    
    cursor.execute(query_analyzed)
    columns_analyzed = [desc[0] for desc in cursor.description]
    analyzed_results = [dict(zip(columns_analyzed, row)) for row in cursor.fetchall()]

    # ---------------------------------------------------------
    # FIX 2: Do the same for Silver (Raw) to find other planes
    # ---------------------------------------------------------
    query_raw = """
    WITH LatestRaw AS (
        SELECT 
            icao24, callsign, origin_country, velocity, 
            latitude, longitude, true_track as plane_heading,
            baro_altitude, geo_altitude,
            ROW_NUMBER() OVER(PARTITION BY icao24 ORDER BY request_time_utc DESC) as rn
        FROM silver.flights_parsed
    )
    SELECT 
        icao24, callsign, origin_country, velocity, 
        latitude, longitude, plane_heading,
        baro_altitude, geo_altitude
    FROM LatestRaw
    WHERE rn = 1
    LIMIT 1000
    """
    
    cursor.execute(query_raw)
    columns_raw = [desc[0] for desc in cursor.description]
    
    # ---------------------------------------------------------
    # Merge Logic (Preserves your existing logic)
    # ---------------------------------------------------------
    existing_icaos = {f['icao24'] for f in analyzed_results}
    final_results = analyzed_results[:] 

    for row in cursor.fetchall():
        flight = dict(zip(columns_raw, row))
        icao = flight['icao24']
        
        # Only add if we didn't already find it in the "Analyzed" set
        if icao not in existing_icaos:
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
            existing_icaos.add(icao) 

    cursor.close()
    connection.close()

    print(f"Returning {len(final_results)} unique flights to frontend.")
    return final_results