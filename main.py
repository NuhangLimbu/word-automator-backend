from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
from datetime import datetime

PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

# Simple CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "online", "service": "Word Automator AI"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/process")
async def process(request: Request):
    data = await request.json()
    action = data.get("action", "unknown")
    text = data.get("text", "")
    
    # Mock responses
    if action == "autocorrect":
        result = f"Corrected: {text.capitalize()}"
    elif action == "template":
        result = {"type": "template", "content": "# Template\n\nFill me"}
    elif action == "summarize":
        result = f"Summary: {text[:50]}..."
    else:
        result = f"Processed {action}: {text}"
    
    return {"result": result, "success": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)