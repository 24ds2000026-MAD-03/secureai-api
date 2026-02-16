from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import time
import json

app = FastAPI()

@app.post("/stream")
async def stream_feedback(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    stream_flag = data.get("stream", False)
    
    if not stream_flag:
        return {"error": "stream must be true"}

    def event_generator():
        # Simulate streaming 6 chunks of feedback insights
        chunks = [
            "Insight 1: Customers desire faster delivery times.\n",
            "Insight 2: Users report confusion navigating the interface.\n",
            "Insight 3: Pricing structure is unclear and needs simplification.\n",
            "Insight 4: Mobile application occasionally crashes on login.\n",
            "Insight 5: Positive feedback about customer support responsiveness.\n",
            "Insight 6: Many users request dark mode and accessibility improvements.\n"
        ]
        for chunk in chunks:
            payload = json.dumps({"choices": [{"delta": {"content": chunk}}]})
            yield f"data: {payload}\n\n"
            time.sleep(0.3)  # simulate streaming delay
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
