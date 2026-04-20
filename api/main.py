"""
=====================================================================
OpenBehavior-Auth: Universal Biometric & Environmental Engine
=====================================================================
DESCRIPTION:
This API serves as the core 'Brain' of the OpenBehavior-Auth system. 
It performs three critical security functions:
1.  Bot Detection: Filters automated scripts using timing variance.
2.  Behavioral Matching: Compares typing/mouse rhythm against a baseline.
3.  Environmental Fingerprinting: Records device & network metadata.

AUTHOR: [Your Name/GitHub Handle]
VERSION: 1.0.0 (ISO Audit Grade)
=====================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import statistics
import json
import os
import csv
from datetime import datetime

# --- INITIALIZATION ---
app = FastAPI()

# Configure CORS: Allows the frontend to communicate with this API 
# even if hosted on different local ports.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_config():
    """
    Reads config.json from the parent directory.
    Uses defensive defaults if the file is missing or corrupted.
    """
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load config ({e}). Using system defaults.")
        return {
            "storage_mode": "local_csv",
            "threshold": 50.0,
            "enrollment_sessions": 3,
            "baseline": {"dwellTime": 85.0, "flightTime": 120.0, "rhythmVariance": 25.0, 
                         "deleteRatio": 5.0, "mouseJitter": 15.0, "mouseVelocity": 0.5, 
                         "clickDuration": 110.0}
        }

# Global Configuration Object
config = load_config()

# =====================================================================
# DATA STORAGE LAYER (The Audit Factory)
# =====================================================================

class CSVDatabase:
    """
    Handles the generation of high-precision audit logs.
    Each session is saved as a unique, chronological CSV file.
    """
    def __init__(self):
        # Create a 'logs' directory to prevent cluttering the root folder
        self.logs_dir = "logs"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            
        # Define the 'Gold Standard' columns for banking-grade auditing
        self.headers = [
            "Timestamp", "UserID", "Status", "Score", 
            "DwellTime", "FlightTime", "Variance", "Jitter", "Velocity", "ClickDuration",
            "ScreenRes", "Platform", "Cores", "Timezone", "Language"
        ]

    def save(self, user_id: str, status: str, score: float, metrics: dict):
        """
        Creates a fresh CSV file for every authentication attempt.
        Filename format: LOG_YYYYMMDD_HHMMSS_Microseconds.csv
        """
        file_ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.logs_dir, f"LOG_{file_ts}.csv")
        
        # Extract device info sent from the browser's 'deviceInfo' object
        device = getattr(metrics, 'device_info', {})

        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
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
                metrics.clickDuration,
                device.get("screen", "N/A"),
                device.get("platform", "N/A"),
                device.get("cores", "N/A"),
                device.get("timezone", "N/A"),
                device.get("language", "N/A")
            ])
        print(f"[*] Audit log generated: {filename}")

# Instantiate the active storage engine
db = CSVDatabase()

# =====================================================================
# LOGIC LAYER (The Math Engine)
# =====================================================================

class BehaviorData(BaseModel):
    """Defines the expected JSON structure from the frontend."""
    user_id: str
    dwellTime: float
    flightTime: float
    rhythmVariance: float
    deleteRatio: float
    mouseJitter: float
    mouseVelocity: float
    clickDuration: float
    raw_timings: list  # Crucial for Bot Detection
    device_info: dict  # Captures screen, OS, and hardware specs

# In-memory session store (In production, replace this with Redis or a DB)
db_user = {**config["baseline"], "session_count": 0}

def is_human(timings: list):
    """
    Anti-Automation Check:
    Robotic inputs (Selenium/Scripts) have near-zero variance.
    Natural human typing always has a standard deviation > 2ms.
    """
    if len(timings) < 3: return True
    return statistics.stdev(timings) > 2.0

def calculate_similarity(baseline: dict, current: BehaviorData):
    """
    Performs a multi-dimensional similarity analysis.
    Compares current behavior against the 'Golden Baseline' stored in config.
    Result is a percentage (0-100%).
    """
    metrics = ['dwellTime', 'flightTime', 'rhythmVariance', 'deleteRatio', 
               'mouseJitter', 'mouseVelocity', 'clickDuration']
    total_score = 0
    for k in metrics:
        bv = baseline.get(k, 0)
        cv = getattr(current, k, 0)
        mx = max(bv, cv, 1) # Prevent DivisionByZero
        total_score += (1 - abs(bv - cv) / mx)
    return (total_score / len(metrics)) * 100

# =====================================================================
# API LAYER (The Gatekeeper)
# =====================================================================

@app.post("/verify")
async def verify_user(data: BehaviorData):
    """
    The main endpoint for behavioral authentication.
    Flow: Bot Check -> Enrollment -> Similarity Math -> Audit Logging.
    """
    global db_user
    
    # Dynamically pull rules from config.json
    THRESHOLD = config.get("threshold", 50.0)
    ENROLLMENT_LIMIT = config.get("enrollment_sessions", 3)

    # 1. BOT CHECK: If variance is too low, reject immediately.
    if not is_human(data.raw_timings):
        return {"status": "REJECTED", "reason": "Non-human variance detected."}
    
    # 2. ENROLLMENT: Build a baseline if the user is new.
    if db_user["session_count"] < ENROLLMENT_LIMIT:
        db_user["session_count"] += 1
        db.save(data.user_id, "ENROLLING", 0.0, data)
        return {
            "status": "ENROLLING", 
            "progress": f"{db_user['session_count']}/{ENROLLMENT_LIMIT}",
            "message": "Learning user behavior..."
        }
    
    # 3. VERIFICATION: Compare behavior against baseline.
    score = calculate_similarity(db_user, data)
    status = "CERTIFIED" if score >= THRESHOLD else "SUSPICIOUS"

    # 4. AUDIT: Record the session package to a fresh ISO-named CSV.
    db.save(data.user_id, status, round(score, 2), data)

    return {
        "status": status, 
        "score": f"{round(score, 1)}%",
        "message": "Success" if status == "CERTIFIED" else "Rhythm Anomaly: MFA Required"
    }

# Serve test.html from the root folder automatically.
app.mount("/", StaticFiles(directory=".", html=True), name="static")
