import time
from collections import defaultdict
from fastapi import HTTPException, status
from app.config import settings

class InMemoryRateLimiter:
    def __init__(self):
        # key -> list of timestamps
        self.requests = defaultdict(list)

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60):
        now = time.time()
        window_start = now - window_seconds
        
        # filter out old timestamps
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        if len(self.requests[key]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {int(window_seconds - (now - self.requests[key][0]))} seconds."
            )
        
        self.requests[key].append(now)

    def reset(self):
        self.requests.clear()

rate_limiter = InMemoryRateLimiter()
