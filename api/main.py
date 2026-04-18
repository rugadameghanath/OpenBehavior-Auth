from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math
import statistics

app = FastAPI()

# 1. Define what the incoming data looks like (from your JS)
class BehaviorData(BaseModel):
    user_id: str
    device_type: str
    avg_dwell: float
    avg_flight: float

def is_human(timings: list):
    # If the bot is sending the same timing for every keypress
    if len(timings) < 3: return True # Not enough data to judge
    
    variance = statistics.stdev(timings)
    
    # Bots often have 0 variance (100ms, 100ms, 100ms)
    # Even a 'fast' human has a jitter of at least 5-10ms
    if variance < 2.0:
        return False # Likely a Bot
    return True

# 2. The Logic: Threshold Matching
def calculate_similarity(baseline, current):
    # Simple Euclidean Distance logic
    # We compare Dwell and Flight rhythms
    distance = math.sqrt(
        (baseline['avg_dwell'] - current.avg_dwell)**2 + 
        (baseline['avg_flight'] - current.avg_flight)**2
    )
    return distance
def update_baseline(old_avg, new_value, session_count):
    """
    Moves the baseline toward the new behavior using a 'Learning Rate'.
    The more sessions we have, the more 'stable' the baseline becomes.
    """
    # Learning Rate: 0.1 means we change the baseline by 10% each time
    LEARNING_RATE = 0.1 
    
    updated_val = (old_avg * (1 - LEARNING_RATE)) + (new_value * LEARNING_RATE)
    return round(updated_val, 2)

# Example usage during a successful login:
# new_dwell = update_baseline(db_dwell, current_dwell, db_sessions)

@app.post("/verify")
async def verify_user(data: BehaviorData):
    # 1. MOCK SQL STEP: In Oracle, you'd fetch the row for this user_id
    # We added 'session_count' to our mock data
    mock_user_profile = {
        "avg_dwell": 85.0, 
        "avg_flight": 120.0, 
        "session_count": 3  # Current number of successful logins stored in Oracle
    }

    # 2. Bot Check first! (Always kill automation before processing logic)
    if not is_human(data.raw_timings):
        return {"status": "REJECTED", "reason": "Automated traffic detected"}
    
    # 3. ENROLLMENT LOGIC (The "Step 2" we discussed)
    # If the user is new (less than 5 sessions), we don't verify score yet.
    if mock_user_profile["session_count"] < 5:
        # Here, you would UPDATE Oracle: 
        # SET avg_dwell = new_calc, avg_flight = new_calc, session_count = count + 1
        return {
            "status": "ENROLLING", 
            "progress": f"{mock_user_profile['session_count'] + 1}/5",
            "message": "Building behavioral profile. No verification performed."
        }
    
    # 4. VERIFICATION LOGIC (Only runs if session_count >= 5)
    score = calculate_similarity(mock_user_profile, data)
    
    # Threshold check (Lower is better)
    THRESHOLD = 20.0 
    
    if score <= THRESHOLD:
        # Match! Here you'd also run your 'update_baseline' logic to follow the drift
        return {"status": "CERTIFIED", "score": round(score, 2)}
    else:
        # Mismatch or major drift
        return {"status": "SUSPICIOUS", "score": round(score, 2)}

# 3. To run this: 'pip install fastapi uvicorn' then 'uvicorn main:app --reload'
