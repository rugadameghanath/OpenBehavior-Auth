from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import math
import statistics
import json
import os

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_config():
    """Reads the threshold and baseline from config.json."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

# Global variables to act as our 'In-Memory' Database
config = load_config()
db_user = {
    "avg_dwell": config["baseline"]["avg_dwell"], 
    "avg_flight": config["baseline"]["avg_flight"], 
    "session_count": config["starting_session_count"] 
}

# ==========================================
# 2. MODELS & LOGIC
# ==========================================
class BehaviorData(BaseModel):
    user_id: str
    device_type: str
    avg_dwell: float
    avg_flight: float
    raw_timings: list

def is_human(timings: list):
    """Bot Check: High variance = Human, Low variance = Bot."""
    if len(timings) < 3: return True 
    variance = statistics.stdev(timings)
    return variance > 2.0 

def calculate_similarity(baseline, current):
    """Euclidean Distance between profile and current session."""
    distance = math.sqrt(
        (baseline['avg_dwell'] - current.avg_dwell)**2 + 
        (baseline['avg_flight'] - current.avg_flight)**2
    )
    return distance

# ==========================================
# 3. THE CORE SECURITY GATEKEEPER
# ==========================================
@app.post("/verify")
async def verify_user(data: BehaviorData):
    # This keyword is critical to ensure the session_count persists
    global db_user
    
    # Load strictness from config
    THRESHOLD = config["threshold"]

    # STEP A: Bot Check
    if not is_human(data.raw_timings):
        return {"status": "REJECTED", "reason": "Automated traffic detected"}
    
    # STEP B: Enrollment Phase (Building the Baseline)
    if db_user["session_count"] < 5:
        db_user["session_count"] += 1 
        return {
            "status": "ENROLLING", 
            "progress": f"{db_user['session_count']}/5",
            "message": "Learning your typing rhythm..."
        }
    
    # STEP C: Verification Phase (The Judging Phase)
    score = calculate_similarity(db_user, data)
    
    if score <= THRESHOLD:
        return {
            "status": "CERTIFIED", 
            "score": round(score, 2),
            "message": "Authentication Successful"
        }
    else:
        return {
            "status": "SUSPICIOUS", 
            "score": round(score, 2),
            "message": "Rhythm mismatch. MFA required."
        }

# ==========================================
# 4. PLUG & PLAY MOUNTING
# ==========================================
app.mount("/", StaticFiles(directory=".", html=True), name="static")
