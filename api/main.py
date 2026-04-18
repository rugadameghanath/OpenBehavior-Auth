from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math

app = FastAPI()

# 1. Define what the incoming data looks like (from your JS)
class BehaviorData(BaseModel):
    user_id: str
    device_type: str
    avg_dwell: float
    avg_flight: float

# 2. The Logic: Threshold Matching
def calculate_similarity(baseline, current):
    # Simple Euclidean Distance logic
    # We compare Dwell and Flight rhythms
    distance = math.sqrt(
        (baseline['avg_dwell'] - current.avg_dwell)**2 + 
        (baseline['avg_flight'] - current.avg_flight)**2
    )
    return distance

@app.post("/verify")
async def verify_user(data: BehaviorData):
    # MOCK SQL STEP: In a real app, you'd do: 
    # SELECT * FROM UserProfiles WHERE user_hash = data.user_id
    mock_baseline = {"avg_dwell": 85.0, "avg_flight": 120.0} 
    
    # Run the match
    score = calculate_similarity(mock_baseline, data)
    
    # Threshold check (Lower is better)
    THRESHOLD = 20.0 
    
    if score <= THRESHOLD:
        return {"status": "CERTIFIED", "score": round(score, 2)}
    else:
        return {"status": "SUSPICIOUS", "score": round(score, 2)}

# 3. To run this: 'pip install fastapi uvicorn' then 'uvicorn main:app --reload'
