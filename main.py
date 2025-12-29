from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
from datetime import datetime

PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Word Automator AI Backend",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/process")
async def process(request: Request):
    try:
        data = await request.json()
        action = data.get("action", "unknown")
        text = data.get("text", "")
        style = data.get("style", "formal")
        
        # Simple AI processing
        if action == "autocorrect":
            result = f"🤖 Auto-corrected ({style}): {text.capitalize()}"
        
        elif action == "template":
            result = {
                "type": "template",
                "title": "Business Report",
                "content": "# Business Report\n\n## Executive Summary\n[Your summary here]\n\n## Recommendations\n[Your recommendations here]",
                "variables": ["title", "summary", "recommendations"]
            }
        
        elif action == "summarize":
            words = text.split()
            summary = " ".join(words[:20]) + ("..." if len(words) > 20 else "")
            result = f"📝 Summary: {summary}"
        
        elif action == "analyze":
            words = len(text.split())
            chars = len(text)
            result = {
                "type": "analysis",
                "word_count": words,
                "character_count": chars,
                "average_word_length": round(chars / max(words, 1), 1),
                "reading_time_minutes": round(words / 200, 1)
            }
        
        else:
            result = f"Processed '{action}': {text[:100]}..."
        
        return {
            "success": True,
            "result": result,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print(f"🚀 Starting Word Automator Backend on port {PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )