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
    # MOCK SQL STEP: In a real app, you'd do: 
    # SELECT * FROM UserProfiles WHERE user_hash = data.user_id
    mock_baseline = {"avg_dwell": 85.0, "avg_flight": 120.0} 

    # Bot Check first!
    if not is_human(data.raw_timings):
        return {"status": "REJECTED", "reason": "Automated traffic detected"}
    
    # Run the match
    score = calculate_similarity(mock_baseline, data)
    
    # Threshold check (Lower is better)
    THRESHOLD = 20.0 
    
    if score <= THRESHOLD:
        return {"status": "CERTIFIED", "score": round(score, 2)}
    else:
        return {"status": "SUSPICIOUS", "score": round(score, 2)}

# 3. To run this: 'pip install fastapi uvicorn' then 'uvicorn main:app --reload'
