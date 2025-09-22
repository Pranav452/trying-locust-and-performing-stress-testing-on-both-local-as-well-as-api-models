import time 
from typing import Dict, List
from fastapi import FastAPI, HTTPException

from metrics import RATE_LIMIT_EXCEEDED, USER_REQUEST_COUNT

user_rate_limits: Dict[str, int] = {}
user_requests: Dict[str, List[float]] = {}
RATE_LIMIT = {
    "anonymous": 100,
    "user": 1000,
    "default": 5
}
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

def get_user_limit(user: str) -> int:
    return user_rate_limits.get(user, RATE_LIMIT.get(user, RATE_LIMIT["default"]))

def check_rate_limit(user: str) -> bool:
    current_time = time.time()
    limit = get_user_limit(user)
    
    if user not in user_requests:
        user_requests[user] = []
    
    # Remove old requests outside the time window
    cutoff_time = current_time - RATE_LIMIT_WINDOW
    user_requests[user] = [
        req_time for req_time in user_requests[user] 
        if req_time > cutoff_time
    ]
    
    # Check if user has exceeded rate limit
    if len(user_requests[user]) >= limit:
        RATE_LIMIT_EXCEEDED.labels(user=user).inc()
        return False
    
    # Add current request
    user_requests[user].append(current_time)
    return True
