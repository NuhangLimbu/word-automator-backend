import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# ========== CONFIGURATION ==========
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

print("=" * 60)
print("WORD AUTOMATOR AI BACKEND")
print(f"Environment: {ENVIRONMENT}")
print(f"Port: {PORT}")
print(f"Allowed Origins: {ALLOWED_ORIGINS}")
print("=" * 60)

# ========== FASTAPI APP ==========
app = FastAPI(
    title="Word Automator AI Backend",
    description="AI-powered document automation backend",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url=None
)

# ========== CORS MIDDLEWARE ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.office.com",
        "https://*.officeapps.live.com",
        "https://*.sharepoint.com",
        "https://word-automator-frontend.onrender.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "https://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-Office-Version",
        "X-Office-SessionId",
        "Access-Control-Allow-Origin"
    ],
    expose_headers=["*"],
    max_age=600
)

# ========== SECURITY MIDDLEWARE ==========
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Office-compatible CSP
    csp_directives = [
        "default-src 'self'",
        "connect-src 'self' https://*.office.com https://*.officeapps.live.com https://*.sharepoint.com https://word-automator-backend.onrender.com",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://appsforoffice.microsoft.com",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "frame-ancestors 'self' https://*.office.com https://*.officeapps.live.com",
        "form-action 'self'"
    ]
    
    response.headers.update({
        "Content-Security-Policy": "; ".join(csp_directives),
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Office-Version",
        "Access-Control-Expose-Headers": "*",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "ALLOW-FROM https://office.com",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    })
    
    return response

# ========== DATA MODELS ==========
class ProcessRequest(BaseModel):
    action: str
    text: str
    template_name: Optional[str] = None
    style: Optional[str] = "formal"
    variables: Optional[Dict[str, Any]] = None

# ========== TEMPLATES DATABASE ==========
TEMPLATES = {
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
    "email_template": {
        "name": "Professional Email",
        "content": """Subject: {subject}

Dear {recipient_name},

{email_body}

Best regards,
{sender_name}
{position}
{company}""",
        "variables": ["subject", "recipient_name", "email_body", "sender_name", "position", "company"]
    },
    "meeting_minutes": {
        "name": "Meeting Minutes",
        "content": """# Meeting Minutes: {meeting_title}

**Date:** {date}
**Time:** {time}
**Location:** {location}
**Attendees:** {attendees}

## Agenda
{agenda}

## Discussion Points
{discussion}

## Action Items
{action_items}

## Next Meeting
{next_meeting}""",
        "variables": ["meeting_title", "date", "time", "location", "attendees", "agenda", "discussion", "action_items", "next_meeting"]
    }
}

# ========== ROUTES ==========
@app.get("/")
async def root():
    return {
        "service": "Word Automator AI Backend",
        "status": "online",
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "config": "/config",
            "templates": "/templates",
            "process": "/process (POST)",
            "logs": "/logs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Word Automator AI"
    }

@app.get("/config")
async def get_config():
    return {
        "environment": ENVIRONMENT,
        "port": PORT,
        "cors_enabled": True,
        "office_compatible": True,
        "templates_count": len(TEMPLATES),
        "api_version": "1.0.0"
    }

@app.get("/templates")
async def get_templates():
    return {
        "templates": TEMPLATES,
        "count": len(TEMPLATES),
        "timestamp": datetime.now().isoformat()
    }

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight"""
    return JSONResponse(
        content={"message": "CORS preflight successful"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Office-Version"
        }
    )

@app.post("/process")
async def process_text(request: ProcessRequest):
    """Main AI processing endpoint"""
    try:
        print(f"Processing action: {request.action}")
        
        result = {
            "success": True,
            "action": request.action,
            "timestamp": datetime.now().isoformat(),
            "original_text_length": len(request.text)
        }
        
        # Process based on action
        if request.action == "autocorrect":
            corrected = autocorrect_text(request.text, request.style)
            result.update({
                "type": "text",
                "result": corrected,
                "style": request.style,
                "improvement": f"Fixed grammar and {request.style} style applied"
            })
            
        elif request.action == "template":
            template = TEMPLATES.get(request.template_name or "business_report")
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            result.update({
                "type": "template",
                "template_name": template["name"],
                "content": template["content"],
                "variables": template["variables"],
                "instructions": "Fill the {variables} with your content"
            })
            
        elif request.action == "summarize":
            summary = summarize_text(request.text)
            result.update({
                "type": "text",
                "result": summary,
                "reduction_percentage": round((1 - len(summary)/len(request.text)) * 100, 1),
                "original_words": len(request.text.split()),
                "summary_words": len(summary.split())
            })
            
        elif request.action == "analyze":
            analysis = analyze_text(request.text)
            result.update({
                "type": "analysis",
                **analysis
            })
            
        elif request.action == "autofill":
            filled = autofill_template(request.template_name, request.text, request.variables or {})
            result.update({
                "type": "filled_template",
                "result": filled,
                "template_used": request.template_name
            })
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ========== AI PROCESSING FUNCTIONS ==========
def autocorrect_text(text: str, style: str = "formal") -> str:
    """Auto-correct text with style adjustments"""
    if not text:
        return text
    
    # Basic corrections
    text = text.strip()
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    if style == "formal":
        sentences = [s.capitalize() for s in sentences]
        corrected = '. '.join(sentences)
        if not corrected.endswith('.'):
            corrected += '.'
    elif style == "casual":
        corrected = text.lower()
        corrected = corrected[0].upper() + corrected[1:] if corrected else corrected
    else:
        corrected = text.capitalize()
    
    return f"🤖 AI Corrected ({style}):\n{corrected}"

def summarize_text(text: str) -> str:
    """Summarize text"""
    words = text.split()
    if len(words) <= 30:
        return text
    
    # Simple summary: take first 30 words
    summary = " ".join(words[:30])
    if len(words) > 30:
        summary += "..."
    
    return f"📝 Summary ({len(words)} words → {len(summary.split())} words):\n{summary}"

def analyze_text(text: str) -> dict:
    """Analyze text metrics"""
    words = text.split()
    sentences = [s for s in text.split('.') if s.strip()]
    characters = len(text.replace(' ', ''))
    
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "character_count": len(text),
        "characters_no_spaces": characters,
        "average_word_length": round(characters / max(len(words), 1), 2),
        "average_sentence_length": round(len(words) / max(len(sentences), 1), 2),
        "reading_time_minutes": round(len(words) / 200, 1),  # 200 wpm
        "complexity": "Easy" if len(words) < 100 else "Moderate" if len(words) < 300 else "Complex",
        "key_metrics": {
            "has_punctuation": any(p in text for p in ['.', '!', '?']),
            "has_capitals": any(c.isupper() for c in text),
            "has_numbers": any(c.isdigit() for c in text)
        }
    }

def autofill_template(template_name: str, context: str, variables: dict) -> str:
    """Autofill template with variables"""
    template = TEMPLATES.get(template_name or "business_report")
    if not template:
        return "Template not found"
    
    # Use provided variables or extract from context
    filled = template["content"]
    for var in template["variables"]:
        value = variables.get(var, f"[{var.upper()}_HERE]")
        filled = filled.replace(f"{{{var}}}", value)
    
    return filled

# ========== ERROR HANDLERS ==========
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if ENVIRONMENT == "development" else "Contact administrator",
            "timestamp": datetime.now().isoformat()
        }
    )

# ========== START SERVER ==========
if __name__ == "__main__":
    print(f"\n🚀 Starting Word Automator AI Backend...")
    print(f"📡 Listening on: http://0.0.0.0:{PORT}")
    print(f"🌍 Environment: {ENVIRONMENT}")
    print(f"🔗 CORS Enabled for Office domains")
    print(f"📊 Templates loaded: {len(TEMPLATES)}")
    print("\n✅ Endpoints:")
    print(f"   • Health: http://localhost:{PORT}/health")
    print(f"   • API Root: http://localhost:{PORT}/")
    print(f"   • Documentation: http://localhost:{PORT}/docs")
    print(f"   • Templates: http://localhost:{PORT}/templates")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info" if ENVIRONMENT == "production" else "debug",
        access_log=True
    )