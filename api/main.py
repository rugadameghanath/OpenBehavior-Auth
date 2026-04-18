"""
OpenBehavior-Auth: Core API & Router
--------------------------------------------------
This module serves as the primary backend for the behavioral biometrics engine.
It handles incoming biometric payloads, performs variance and similarity checks,
and routes the resulting data to the configured storage backend dynamically.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import math
import statistics
import json
import os
import csv
from datetime import datetime

# =====================================================================
# SECTION 1: SYSTEM INITIALIZATION & CONFIGURATION
# =====================================================================

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_config():
    """Loads the master configuration file to determine system behavior."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

# Load config globally so all components can access it on startup
config = load_config()

# =====================================================================
# SECTION 2: DATABASE ADAPTERS (The Storage Engines)
# =====================================================================

class CSVDatabase:
    """
    Mode: 'local_csv'
    A flat-file database adapter perfect for local testing and open-source users.
    Generates a CSV that can be opened natively in Excel.
    """
    def __init__(self):
        self.filepath = "biometrics_db.csv"
        # If the file doesn't exist, create it and write the column headers
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "UserID", "Status", "Score", 
                    "DwellTime", "FlightTime", "Variance", 
                    "Jitter", "Velocity", "ClickDuration"
                ])

    def save(self, user_id: str, status: str, score: float, metrics: dict):
        """Appends a new session record to the CSV."""
        with open(self.filepath, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_id,
                status,
                score,
                metrics.dwellTime,
                metrics.flightTime,
                metrics.rhythmVariance,
                metrics.mouseJitter,
                metrics.mouseVelocity,
                metrics.clickDuration
            ])

class SQLDatabase:
    """
    Mode: 'sql_db'
    Adapter for Enterprise / VPS Hosting environments (Oracle, SQLite, Postgres).
    """
    def save(self, user_id: str, status: str, score: float, metrics: dict):
        # NOTE: Implement actual SQLAlchemy or standard SQL INSERT logic here
        print(f"[SQL Router] INSERT INTO UserSessions VALUES ('{user_id}', '{status}', {score})")

class WebhookDatabase:
    """
    Mode: 'cloud_api'
    Adapter for Serverless deployments. Sends data via HTTP POST to external services.
    """
    def save(self, user_id: str, status: str, score: float, metrics: dict):
        # NOTE: Implement standard requests.post() logic to external endpoints here
        print(f"[Cloud Router] HTTP POST payload dispatched for {user_id}")

# =====================================================================
# SECTION 3: THE UNIVERSAL ROUTER
# =====================================================================
# This block reads the config and automatically spins up the correct database
# adapter. The rest of the application will just call `db.save()`.

storage_mode = config.get("storage_mode", "local_csv")

if storage_mode == "sql_db":
    db = SQLDatabase()
elif storage_mode == "cloud_api":
    db = WebhookDatabase()
else:
    # Default fallback to ensure the app always runs out of the box
    db = CSVDatabase() 

# =====================================================================
# SECTION 4: DATA MODELS & BASELINE STATE
# =====================================================================

# Mock User Profile acting as our active comparison baseline
db_user = {
    "dwellTime": config["baseline"]["dwellTime"], 
    "flightTime": config["baseline"]["flightTime"],
    "rhythmVariance": config["baseline"]["rhythmVariance"],
    "deleteRatio": config["baseline"]["deleteRatio"],
    "mouseJitter": config["baseline"]["mouseJitter"],
    "mouseVelocity": config["baseline"]["mouseVelocity"],
    "clickDuration": config["baseline"]["clickDuration"],
    "session_count": config["starting_session_count"] 
}

class BehaviorData(BaseModel):
    """The strict data contract required from the frontend client."""
    user_id: str
    dwellTime: float
    flightTime: float
    rhythmVariance: float
    deleteRatio: float
    mouseJitter: float
    mouseVelocity: float
    clickDuration: float
    raw_timings: list

# =====================================================================
# SECTION 5: BIOMETRIC MATH ENGINE
# =====================================================================

def is_human(timings: list):
    """Variance check to filter out zero-variance automation (Selenium/Bots)."""
    if len(timings) < 3: 
        return True 
    variance = statistics.stdev(timings)
    return variance > 2.0 

def calculate_similarity(baseline: dict, current: BehaviorData):
    """Calculates a weighted percentage match across all 7 biometric factors."""
    metrics = [
        'dwellTime', 'flightTime', 'rhythmVariance', 
        'deleteRatio', 'mouseJitter', 'mouseVelocity', 'clickDuration'
    ]
    
    total_score = 0
    for k in metrics:
        bv = baseline.get(k, 0)
        cv = getattr(current, k, 0)
        mx = max(bv, cv, 1) # Prevent division by zero
        total_score += (1 - abs(bv - cv) / mx)
    
    return (total_score / len(metrics)) * 100

# =====================================================================
# SECTION 6: THE CORE API GATEKEEPER
# =====================================================================

@app.post("/verify")
async def verify_user(data: BehaviorData):
    global db_user
    THRESHOLD = config["threshold"]

    # STEP A: Bot Detection Check
    if not is_human(data.raw_timings):
        return {"status": "REJECTED", "reason": "Automated traffic detected"}
    
    # STEP B: Enrollment Phase Tracking
    if db_user["session_count"] < 5:
        db_user["session_count"] += 1
        
        # Log the enrollment attempt to the configured database
        db.save(data.user_id, "ENROLLING", 0.0, data)
        
        return {
            "status": "ENROLLING", 
            "progress": f"{db_user['session_count']}/5",
            "message": "Learning behavioral patterns..."
        }
    
    # STEP C: Active Verification Math
    score = calculate_similarity(db_user, data)
    
    if score >= THRESHOLD:
        result_status = "CERTIFIED"
        message = "Authentication Successful"
    else:
        result_status = "SUSPICIOUS"
        message = "Rhythm mismatch. MFA required."

    # Send the final result to the Universal Router to be saved
    db.save(data.user_id, result_status, round(score, 2), data)

    # Return decision to the frontend
    return {
        "status": result_status, 
        "score": f"{round(score, 1)}%",
        "message": message
    }

# =====================================================================
# SECTION 7: STATIC FILE MOUNTING
# =====================================================================
# Exposes the root directory so test.html can be served directly via FastAPI.
app.mount("/", StaticFiles(directory=".", html=True), name="static")
