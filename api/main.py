from fastapi import FastAPI
from pydantic import BaseModel
import math
import statistics
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # New: For serving the test page
from pydantic import BaseModel
import math
import statistics
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. DATA CONTRACT: Matches what the JS Collector sends
class BehaviorData(BaseModel):
    user_id: str
    device_type: str
    avg_dwell: float
    avg_flight: float
    raw_timings: list  # This is the list of numbers for the bot check

# 2. BOT DETECTION: Checks for "too perfect" timing
def is_human(timings: list):
    if len(timings) < 3: return True 
    variance = statistics.stdev(timings)
    return variance > 2.0  # If variance is low, it's a Selenium script

# 3. BIOMETRIC MATH: Calculates the "Distance" from the Golden Baseline
def calculate_similarity(baseline, current):
    distance = math.sqrt(
        (baseline['avg_dwell'] - current.avg_dwell)**2 + 
        (baseline['avg_flight'] - current.avg_flight)**2
    )
    return distance

# 4. MAIN GATEKEEPER: The API Endpoint
@app.post("/verify")
async def verify_user(data: BehaviorData):
    # --- MOCK SQL DATA: In production, fetch this from Oracle ---
    # SELECT profile_id, avg_dwell, avg_flight, session_count FROM UserProfiles
    db_user = {
        "profile_id": 101,
        "avg_dwell": 85.0, 
        "avg_flight": 120.0, 
        "session_count": 3  # Change this to 6 to test the verification phase
    }

    # STEP A: Bot Check (Always do this first)
    if not is_human(data.raw_timings):
        return {"status": "REJECTED", "reason": "Automated traffic detected"}
    
    # STEP B: Enrollment Phase (The "Learning" sessions)
    if db_user["session_count"] < 5:
        # ACTION: In Oracle, use the 'Enrollment SQL' (Simple Average)
        # UPDATE UserProfiles SET session_count = session_count + 1...
        return {
            "status": "ENROLLING", 
            "progress": f"{db_user['session_count'] + 1}/5",
            "message": "Building behavioral profile. No verification yet."
        }
    
    # STEP C: Verification Phase (The "Judging" sessions)
    score = calculate_similarity(db_user, data)
    THRESHOLD = 20.0 
    
    if score <= THRESHOLD:
        # ACTION: In Oracle, use the 'Drift SQL' (Learning Rate 0.1)
        return {"status": "CERTIFIED", "score": round(score, 2)}
    else:
        # ACTION: Trigger MFA (OTP) because the rhythm changed
        return {"status": "SUSPICIOUS", "score": round(score, 2)}

# Tells FastAPI to serve files from your main folder
# This makes it 'Plug and Play' for anyone who clones your repo
app.mount("/", StaticFiles(directory=".", html=True), name="static")
