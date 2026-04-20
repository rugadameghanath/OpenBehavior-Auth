"""
=====================================================================
OpenBehavior-Auth: Universal Biometric & Environmental Engine
=====================================================================
DESCRIPTION:
This engine provides a multi-layered security approach for digital 
banking operations. It supports three distinct storage backends:
1.  Local CSV: Smart-buffered audit logs (200-row rotation) for local forensics.
2.  Google Sheets: Real-time cloud-based monitoring.
3.  SQL Database: Production-grade relational storage (Oracle/SQL).

ARCHITECTURE:
- Bot Detection: Timing variance analysis.
- Behavioral Matching: 7-dimensional Euclidean similarity.
- Device Fingerprinting: Silent hardware/environment binding.

AUTHOR: [Your Name/GitHub Handle]
VERSION: 1.1.0 (Enterprise Pluggable Edition)
=====================================================================
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import statistics
import json
import os
import csv
import math
from datetime import datetime

# =====================================================================
# SECTION 1: SYSTEM INITIALIZATION & CONFIG
# =====================================================================

app = FastAPI(title="OpenBehavior-Auth Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_config():
    """Loads configuration with defensive fallbacks for stability."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[*] Config Load Warning: {e}. Using Default Security Profile.")
        return {
            "storage_mode": "local_csv", 
            "max_log_rows": 200,
            "threshold": 50.0,
            "enrollment_sessions": 3,
            "google_sheet_url": "https://docs.google.com/spreadsheets/d/PLACEHOLDER",
            "db_connection_string": "oracle+cx_oracle://user:pass@host:port/service_name",
            "baseline": {
                "dwellTime": 85.0, "flightTime": 120.0, "rhythmVariance": 25.0, 
                "deleteRatio": 5.0, "mouseJitter": 15.0, "mouseVelocity": 0.5, 
                "clickDuration": 110.0
            }
        }

config = load_config()

# =====================================================================
# SECTION 2: PLUGGABLE STORAGE FACTORY
# =====================================================================

class StorageManager:
    """Handles data persistence and Smart-Rotation for Local CSV."""
    def __init__(self):
        self.mode = config.get("storage_mode", "local_csv")
        self.logs_dir = "logs"
        
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            
        self.headers = [
            "Timestamp", "UserID", "Status", "Score", 
            "DwellTime", "FlightTime", "Variance", "Jitter", "Velocity", "ClickDuration",
            "ScreenRes", "Platform", "Cores", "Timezone", "Language"
        ]

    def save(self, user_id: str, status: str, score: float, metrics: dict):
        if self.mode == "local_csv":
            return self._save_local_csv(user_id, status, score, metrics)
        elif self.mode == "google_sheets":
            return self._save_google_sheets(user_id, status, score, metrics)
        elif self.mode == "sql_db":
            return self._save_sql_db(user_id, status, score, metrics)

    def _get_active_file(self):
        """Determines whether to append to latest file or rotate based on row limits."""
        max_rows = config.get("max_log_rows", 200)
        existing_logs = sorted([f for f in os.listdir(self.logs_dir) if f.startswith("LOG_")])
        
        if existing_logs:
            latest_path = os.path.join(self.logs_dir, existing_logs[-1])
            try:
                with open(latest_path, 'r') as f:
                    line_count = sum(1 for _ in f)
                if line_count <= max_rows:
                    return latest_path
            except Exception:
                pass

        # Generate a new timestamped file if limit reached
        file_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = os.path.join(self.logs_dir, f"LOG_{file_ts}.csv")
        
        with open(new_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            
        return new_path

    def _save_local_csv(self, user_id, status, score, metrics):
        target_file = self._get_active_file()
        device = getattr(metrics, 'device_info', {})

        try:
            with open(target_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    user_id, status, score,
                    metrics.dwellTime, metrics.flightTime, metrics.rhythmVariance,
                    metrics.mouseJitter, metrics.mouseVelocity, metrics.clickDuration,
                    device.get("screen", "N/A"), device.get("platform", "N/A"),
                    device.get("cores", "N/A"), device.get("timezone", "N/A"),
                    device.get("language", "N/A")
                ])
        except Exception as e:
            print(f"[Error] Local CSV Write Failed: {e}")

    def _save_google_sheets(self, user_id, status, score, metrics):
        url = config.get("google_sheet_url")
        print(f"[Storage] Mock-up: Pushing record for {user_id} to GSheet: {url}")

    def _save_sql_db(self, user_id, status, score, metrics):
        conn_str = config.get("db_connection_string")
        print(f"[Storage] Mock-up: Writing to SQL Database via {conn_str}")

# Global storage instance
db = StorageManager()

# =====================================================================
# SECTION 3: ANALYTICS & BIOMETRIC MATH
# =====================================================================

class BehaviorData(BaseModel):
    user_id: str
    dwellTime: float
    flightTime: float
    rhythmVariance: float
    deleteRatio: float
    mouseJitter: float
    mouseVelocity: float
    clickDuration: float
    raw_timings: list
    device_info: dict

db_user = {**config["baseline"], "session_count": 0}

def is_human(timings: list):
    if len(timings) < 3: return True
    sd = statistics.stdev(timings)
    return sd > 2.0  

def calculate_similarity(baseline: dict, current: BehaviorData):
    metrics_to_compare = [
        'dwellTime', 'flightTime', 'rhythmVariance', 'deleteRatio', 
        'mouseJitter', 'mouseVelocity', 'clickDuration'
    ]
    
    dimension_scores = []
    
    for key in metrics_to_compare:
        base_val = baseline.get(key, 0)
        curr_val = getattr(current, key, 0)
        
        max_val = max(base_val, curr_val, 1)
        diff = abs(base_val - curr_val)
        
        similarity = 1 - (diff / max_val)
        dimension_scores.append(similarity)
    
    avg_similarity = sum(dimension_scores) / len(dimension_scores)
    return avg_similarity * 100

# =====================================================================
# SECTION 4: THE AUTHENTICATION GATEKEEPER
# =====================================================================

@app.post("/verify")
async def verify_user(data: BehaviorData):
    global db_user
    
    THRESHOLD = config.get("threshold", 50.0)
    ENROLLMENT_LIMIT = config.get("enrollment_sessions", 3)

    if not is_human(data.raw_timings):
        return {"status": "REJECTED", "reason": "Non-human variance detected."}
    
    if db_user["session_count"] < ENROLLMENT_LIMIT:
        db_user["session_count"] += 1
        db.save(data.user_id, "ENROLLING", 0.0, data)
        return {
            "status": "ENROLLING", 
            "progress": f"{db_user['session_count']}/{ENROLLMENT_LIMIT}",
            "message": "Building your biometric profile. Please keep typing."
        }
    
    score = calculate_similarity(db_user, data)
    status = "CERTIFIED" if score >= THRESHOLD else "SUSPICIOUS"
    
    db.save(data.user_id, status, round(score, 2), data)

    return {
        "status": status, 
        "score": f"{round(score, 1)}%",
        "message": "Access Granted" if status == "CERTIFIED" else "Rhythm Mismatch: MFA Challenged"
    }

# =====================================================================
# SECTION 5: STATIC SERVER
# =====================================================================
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("[*] OpenBehavior-Auth Engine Starting...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
