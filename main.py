from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import time

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

class ValidationRequest(BaseModel):
    userId: str
    input: str
    category: str

# Simple in-memory rate limit store
rate_limit_store = {}

RATE_LIMIT = 10  # requests per minute


def check_rate_limit(user_id):
    current_time = time.time()
    user_data = rate_limit_store.get(user_id, [])

    # Keep only last 60 seconds
    user_data = [t for t in user_data if current_time - t < 60]

    if len(user_data) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    user_data.append(current_time)
    rate_limit_store[user_id] = user_data


def detect_prompt_injection(text):
    patterns = [
        r"ignore all safety rules",
        r"developer mode",
        r"system prompt",
        r"reveal.*prompt",
        r"you are now",
        r"act as system",
        r"override.*instructions",
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True, f"Blocked due to detected pattern: {pattern}"

    return False, "Input passed all security checks"


@app.post("/validate")
async def validate(request: ValidationRequest):
    try:
        check_rate_limit(request.userId)

        blocked, reason = detect_prompt_injection(request.input)

        if blocked:
            return {
                "blocked": True,
                "reason": "Potential prompt injection detected",
                "sanitizedOutput": None,
                "confidence": 0.98
            }

        return {
            "blocked": False,
            "reason": reason,
            "sanitizedOutput": request.input,
            "confidence": 0.95
        }

    except HTTPException as e:
        raise e

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request")
