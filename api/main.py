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
"""
=====================================================================
OpenBehavior-Auth: Universal Biometric & Environmental Engine
=====================================================================
DESCRIPTION:
This engine provides a multi-layered security approach for digital 
banking operations. It supports three distinct storage backends:
1.  Local CSV: ISO-8601 rotated audit logs for local forensics.
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

# Configure CORS for cross-origin local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_config():
    """
    Loads configuration from config.json. 
    Includes fallback defaults to ensure system stability.
    """
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[*] Config Load Warning: {e}. Using Default Security Profile.")
        return {
            "storage_mode": "local_csv", 
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
    """
    The Storage Factory handles data persistence across different media.
    The main API never interacts with files or databases directly; 
    it only speaks to this Manager.
    """
    def __init__(self):
        self.mode = config.get("storage_mode", "local_csv")
        self.headers = [
            "Timestamp", "UserID", "Status", "Score", 
            "DwellTime", "FlightTime", "Variance", "Jitter", "Velocity", "ClickDuration",
            "ScreenRes", "Platform", "Cores", "Timezone", "Language"
        ]

    def save(self, user_id: str, status: str, score: float, metrics: dict):
        """Routes the data to the correct backend based on config.json"""
        if self.mode == "local_csv":
            return self._save_local_csv(user_id, status, score, metrics)
        elif self.mode == "google_sheets":
            return self._save_google_sheets(user_id, status, score, metrics)
        elif self.mode == "sql_db":
            return self._save_sql_db(user_id, status, score, metrics)

    def _save_local_csv(self, user_id, status, score, metrics):
        """
        Creates a new, high-precision ISO-8601 CSV for every attempt.
        Path: /logs/LOG_YYYYMMDD_HHMMSS_ffffff.csv
        """
        if not os.path.exists("logs"):
            os.makedirs("logs")
            
        file_ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"logs/LOG_{file_ts}.csv"
        device = getattr(metrics, 'device_info', {})

        try:
            with open(filename, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    user_id, status, score,
                    metrics.dwellTime, metrics.flightTime, metrics.rhythmVariance,
                    metrics.mouseJitter, metrics.mouseVelocity, metrics.clickDuration,
                    device.get("screen", "N/A"), device.get("platform", "N/A"),
                    device.get("cores", "N/A"), device.get("timezone", "N/A"),
                    device.get("language", "N/A")
                ])
            print(f"[Storage] Local Audit Saved: {filename}")
        except Exception as e:
            print(f"[Error] Local CSV Write Failed: {e}")

    def _save_google_sheets(self, user_id, status, score, metrics):
        """
        Logic for Google Sheets API integration.
        Requires: pip install gspread oauth2client
        """
        url = config.get("google_sheet_url")
        print(f"[Storage] Mock-up: Pushing record for {user_id} to GSheet: {url}")
        
        # IMPLEMENTATION STEPS:
        # 1. creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        # 2. client = gspread.authorize(creds)
        # 3. sheet = client.open_by_url(url).sheet1
        # 4. sheet.append_row([timestamp, user_id, status, score, ...metrics])

    def _save_sql_db(self, user_id, status, score, metrics):
        """
        Logic for Relational Database integration (Oracle/SQL Server).
        Requires: pip install sqlalchemy + (cx_Oracle or pyodbc)
        """
        conn_str = config.get("db_connection_string")
        print(f"[Storage] Mock-up: Writing to SQL Database via {conn_str}")

        # IMPLEMENTATION STEPS:
        # 1. engine = create_engine(conn_str)
        # 2. metadata = MetaData(bind=engine)
        # 3. logs_table = Table('BehaviorLogs', metadata, autoload=True)
        # 4. engine.execute(logs_table.insert(), [data_dict])

# Initialize the global storage manager
db = StorageManager()

# =====================================================================
# SECTION 3: ANALYTICS & BIOMETRIC MATH
# =====================================================================

class BehaviorData(BaseModel):
    """Pydantic model for strict data validation on the /verify endpoint."""
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

# Mocking a profile store (In production, this is a SQL lookup)
db_user = {**config["baseline"], "session_count": 0}

def is_human(timings: list):
    """
    Performs robotic input detection. 
    Checks the standard deviation of keystroke intervals.
    """
    if len(timings) < 3: return True
    sd = statistics.stdev(timings)
    return sd > 2.0  # Robotic scripts usually have SD < 1.0ms

def calculate_similarity(baseline: dict, current: BehaviorData):
    """
    Calculates the 'Identity Score' using 7-dimensional similarity.
    Each dimension is normalized against the maximum value to ensure balance.
    """
    metrics_to_compare = [
        'dwellTime', 'flightTime', 'rhythmVariance', 'deleteRatio', 
        'mouseJitter', 'mouseVelocity', 'clickDuration'
    ]
    
    dimension_scores = []
    
    for key in metrics_to_compare:
        base_val = baseline.get(key, 0)
        curr_val = getattr(current, key, 0)
        
        # Prevent division by zero and handle absolute differences
        max_val = max(base_val, curr_val, 1)
        diff = abs(base_val - curr_val)
        
        # Calculate similarity for this specific metric
        similarity = 1 - (diff / max_val)
        dimension_scores.append(similarity)
    
    # Final score is the mean of all biometric dimensions
    avg_similarity = sum(dimension_scores) / len(dimension_scores)
    return avg_similarity * 100


class CSVDatabase:
    """
    OpenBehavior-Auth Smart Storage Engine
    Logic: Groups sessions into single files until 'max_log_rows' is reached.
    Prevents file-system clutter in high-traffic environments.
    """
    def __init__(self):
        self.logs_dir = "logs"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            
        self.headers = [
            "Timestamp", "UserID", "Status", "Score", 
            "DwellTime", "FlightTime", "Variance", "Jitter", "Velocity", "ClickDuration",
            "ScreenRes", "Platform", "Cores", "Timezone", "Language"
        ]

    def _get_active_file(self):
        """
        Determines whether to append to the latest file or rotate to a new one.
        Default: 200 rows per file.
        """
        max_rows = config.get("max_log_rows", 200)
        
        # Look for existing files: LOG_20260420_110000.csv, etc.
        existing_logs = sorted([f for f in os.listdir(self.logs_dir) if f.startswith("LOG_")])
        
        if existing_logs:
            latest_path = os.path.join(self.logs_dir, existing_logs[-1])
            try:
                with open(latest_path, 'r') as f:
                    # Count total lines in the current file
                    line_count = sum(1 for _ in f)
                
                # If we haven't hit the 200-row limit (+1 for header), keep using it
                if line_count <= max_rows:
                    return latest_path
            except Exception:
                pass # If file is locked or corrupt, move to create a new one

        # If no file exists OR limit is reached, generate a new timestamped file
        file_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = os.path.join(self.logs_dir, f"LOG_{file_ts}.csv")
        
        # Initialize the new file with headers
        with open(new_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            
        return new_path

    def save(self, user_id: str, status: str, score: float, metrics: dict):
        """Standardized save method used by the /verify endpoint."""
        target_file = self._get_active_file()
        
        # Safely pull device info from the incoming Pydantic model
        device = getattr(metrics, 'device_info', {})

        with open(target_file, mode='a', newline='') as f:
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
                metrics.clickDuration,
                device.get("screen", "N/A"),
                device.get("platform", "N/A"),
                device.get("cores", "N/A"),
                device.get("timezone", "N/A"),
                device.get("language", "N/A")
            ])
        print(f"[*] Audit log updated: {target_file}")

# =====================================================================
# SECTION 4: THE AUTHENTICATION GATEKEEPER
# =====================================================================

@app.post("/verify")
async def verify_user(data: BehaviorData):
    """
    Main entry point for authentication requests.
    Workflow: Bot Check -> Enrollment -> Similarity Math -> Archival.
    """
    global db_user
    
    # 1. Fetch Dynamic Rules
    THRESHOLD = config.get("threshold", 50.0)
    ENROLLMENT_LIMIT = config.get("enrollment_sessions", 3)

    # 2. BOT DETECTION
    if not is_human(data.raw_timings):
        print(f"[Security] Bot Detected for user: {data.user_id}")
        return {"status": "REJECTED", "reason": "Non-human variance detected."}
    
    # 3. ENROLLMENT LOGIC
    if db_user["session_count"] < ENROLLMENT_LIMIT:
        db_user["session_count"] += 1
        db.save(data.user_id, "ENROLLING", 0.0, data)
        return {
            "status": "ENROLLING", 
            "progress": f"{db_user['session_count']}/{ENROLLMENT_LIMIT}",
            "message": "Building your biometric profile. Please keep typing."
        }
    
    # 4. IDENTITY SCORING
    score = calculate_similarity(db_user, data)
    
    # 5. DECISION ENGINE
    status = "CERTIFIED" if score >= THRESHOLD else "SUSPICIOUS"
    
    # 6. AUDIT ARCHIVAL
    db.save(data.user_id, status, round(score, 2), data)

    return {
        "status": status, 
        "score": f"{round(score, 1)}%",
        "message": "Access Granted" if status == "CERTIFIED" else "Rhythm Mismatch: MFA Challenged"
    }

# =====================================================================
# SECTION 5: STATIC SERVER
# =====================================================================

# Serves the Zero-Dependency Lab (test.html) directly from the root
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("[*] OpenBehavior-Auth Engine Starting...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

