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
    connection = sql.connect(
        server_hostname=os.getenv("DB_SERVER"),
        http_path=os.getenv("DB_PATH"),
        access_token=os.getenv("DB_TOKEN")
    )

    cursor = connection.cursor()

    # Query  Presentation Layer
    query = """
    SELECT 
        callsign, origin_country, velocity, predicted_velocity, efficiency_score,
        CASE 
            WHEN efficiency_score < 80 THEN 'Inefficient'
            ELSE 'Optimal'
        END as status
    FROM presentation.flight_predictions
    LIMIT 100
    """

    cursor.execute(query)


    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()
    return results