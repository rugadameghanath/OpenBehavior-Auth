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
    "dwellTime": config["baseline"]["dwellTime"], 
    "flightTime": config["baseline"]["flightTime"], 
    "session_count": config["starting_session_count"] 
}

# ==========================================
# 2. MODELS & LOGIC
# ==========================================
class BehaviorData(BaseModel):
    user_id: str
    dwellTime: float
    flightTime: float
    rhythmVariance: float
    deleteRatio: float
    mouseJitter: float
    mouseVelocity: float
    clickDuration: float
    raw_timings: list  # Still needed for the Bot Check

def is_human(timings: list):
    """Bot Check: High variance = Human, Low variance = Bot."""
    if len(timings) < 3: return True 
    variance = statistics.stdev(timings)
    return variance > 2.0 

def calculate_similarity(baseline, current):
    """
    Calculates a percentage match across 7 biometric factors.
    100% = Perfect Match, 0% = Total Mismatch
    """
    metrics = [
        'dwellTime', 'flightTime', 'rhythmVariance', 
        'deleteRatio', 'mouseJitter', 'mouseVelocity', 'clickDuration'
    ]
    
    total_score = 0
    
    for k in metrics:
        # Get values, ensuring we don't divide by zero
        bv = baseline.get(k, 0)
        # We use getattr because 'current' is a Pydantic object
        cv = getattr(current, k, 0)
        
        mx = max(bv, cv, 1)
        # Calculate how close the two numbers are (0.0 to 1.0)
        total_score += (1 - abs(bv - cv) / mx)
    
    # Return as a percentage (0-100)
    return (total_score / len(metrics)) * 100

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
