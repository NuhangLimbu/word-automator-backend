from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Enable CORS so your Frontend can talk to this Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://word-automator-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def status():
    return {"status": "Backend is active and responsive"}

@app.post("/process")
async def process_request(request: Request):
    data = await request.json()
    action = data.get("action")
    text = data.get("text", "")

    if action == "template":
        return {
            "type": "template",
            "title": "AI GENERATED DOCUMENT",
            "content": "This document was structured via JSON automation logic."
        }
    
    # Logic for text transformations
    if action == "summarize":
        result = f"Summary: {text[:50]}... [Processed by AI]"
    elif action == "autocorrect":
        result = text.strip().capitalize() + " (Grammar Corrected)"
    else:
        result = f"AI Output for {action}: {text[::-1]}" # Example logic

    return {"type": "text", "result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)