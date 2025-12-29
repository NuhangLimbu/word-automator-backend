from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from typing import Optional, List
from datetime import datetime
import json

# Load environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PORT = int(os.getenv("PORT", 8000))

app = FastAPI(
    title="Word Automator AI Backend",
    description="AI-powered document automation backend",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessRequest(BaseModel):
    action: str
    text: str
    template_name: Optional[str] = None
    style: Optional[str] = "formal"

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Word Automator AI Backend",
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT
    }

@app.get("/config")
def get_config():
    """Endpoint to check configuration"""
    return {
        "environment": ENVIRONMENT,
        "allowed_origins": ALLOWED_ORIGINS,
        "openai_configured": bool(OPENAI_API_KEY),
        "port": PORT
    }

@app.post("/process")
async def process_text(request: ProcessRequest):
    """Main AI processing endpoint"""
    try:
        result = await process_with_ai(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_with_ai(request: ProcessRequest) -> dict:
    """Process text with AI capabilities"""
    
    if request.action == "autocorrect":
        return {
            "type": "text",
            "result": f"✅ Corrected ({request.style}): {autocorrect_text(request.text, request.style)}",
            "metadata": {
                "action": request.action,
                "style": request.style,
                "original_length": len(request.text)
            }
        }
    
    elif request.action == "template":
        template = get_template(request.template_name)
        return {
            "type": "template",
            "title": template["name"],
            "content": template["content"],
            "variables": template["variables"]
        }
    
    elif request.action == "summarize":
        summary = summarize_text(request.text)
        return {
            "type": "text",
            "result": f"📝 Summary: {summary}",
            "metadata": {
                "original_length": len(request.text),
                "summary_length": len(summary),
                "reduction": f"{round((1 - len(summary)/len(request.text))*100)}%"
            }
        }
    
    elif request.action == "analyze":
        return analyze_text(request.text)
    
    else:
        return {
            "type": "text",
            "result": f"🤖 Processed '{request.action}': {request.text[:100]}..."
        }

def autocorrect_text(text: str, style: str) -> str:
    """Auto-correct text"""
    # Basic corrections
    text = text.strip()
    if not text.endswith(('.', '!', '?')):
        text += '.'
    
    if style == "formal":
        # Capitalize first letter of each sentence
        sentences = text.split('. ')
        sentences = [s.capitalize() for s in sentences]
        text = '. '.join(sentences)
    
    return text

def summarize_text(text: str) -> str:
    """Summarize text (basic implementation)"""
    words = text.split()
    if len(words) <= 30:
        return text
    
    # Take first 30 words as summary
    summary = " ".join(words[:30])
    if len(words) > 30:
        summary += "..."
    
    return summary

def analyze_text(text: str) -> dict:
    """Analyze text metrics"""
    words = text.split()
    sentences = [s for s in text.split('.') if s.strip()]
    
    return {
        "type": "analysis",
        "word_count": len(words),
        "sentence_count": len(sentences),
        "character_count": len(text),
        "average_word_length": round(len(text.replace(' ', '')) / max(len(words), 1), 1),
        "reading_time_minutes": round(len(words) / 200, 1),  # 200 wpm
        "complexity": "Easy" if len(words) < 100 else "Moderate" if len(words) < 300 else "Complex"
    }

def get_template(template_name: Optional[str] = None) -> dict:
    """Get template by name"""
    templates = {
        "business_report": {
            "name": "Business Report",
            "content": """# {title}

## Executive Summary
{summary}

## Key Findings
{findings}

## Recommendations
{recommendations}

## Next Steps
{next_steps}

**Date:** {date}
**Prepared by:** {author}""",
            "variables": ["title", "summary", "findings", "recommendations", "next_steps", "date", "author"]
        },
        "email": {
            "name": "Professional Email",
            "content": """Subject: {subject}

Dear {recipient},

{body}

Best regards,
{sender}
{position}
{company}""",
            "variables": ["subject", "recipient", "body", "sender", "position", "company"]
        }
    }
    
    return templates.get(template_name or "business_report", templates["business_report"])

if __name__ == "__main__":
    print(f"Starting server in {ENVIRONMENT} environment on port {PORT}")
    print(f"Allowed origins: {ALLOWED_ORIGINS}")
    print(f"OpenAI configured: {bool(OPENAI_API_KEY)}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )