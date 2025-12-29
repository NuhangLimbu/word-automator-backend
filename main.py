from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from typing import Dict, List, Optional
import json
from datetime import datetime

app = FastAPI(title="Word Automator AI Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for demo, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ProcessRequest(BaseModel):
    action: str
    text: str
    template_name: Optional[str] = None
    style: Optional[str] = "professional"

class Template(BaseModel):
    name: str
    content: str
    variables: Dict[str, str]

class UsageLog(BaseModel):
    action: str
    timestamp: str
    text_length: int
    result_length: int

# In-memory storage (use database in production)
templates_db = {
    "business_report": {
        "name": "Business Report",
        "content": """# {company_name} - {report_type} Report

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
        "variables": ["company_name", "report_type", "summary", "findings", "recommendations", "next_steps", "date", "author"]
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
    }
}

correction_rules = {
    "formal": {
        "replacements": {
            "hi ": "Hello ",
            "hey ": "Dear ",
            "thanks": "Thank you",
            "pls": "please",
            "btw": "however",
            "asap": "at your earliest convenience"
        }
    },
    "casual": {
        "replacements": {
            "Dear ": "Hi ",
            "Sincerely": "Cheers",
            "Thank you": "Thanks"
        }
    }
}

usage_logs: List[UsageLog] = []

# Initialize OpenAI (optional)
openai.api_key = os.getenv("OPENAI_API_KEY", "your-openai-key-here")

@app.get("/")
def read_root():
    return {"status": "Word Automator AI Backend is running"}

@app.post("/process")
async def process_text(request: ProcessRequest):
    """Process text based on action"""
    try:
        result = ""
        
        if request.action == "autocorrect":
            result = await autocorrect_text(request.text, request.style)
        
        elif request.action == "autofill":
            result = await autofill_template(request.template_name, request.text)
        
        elif request.action == "summarize":
            result = await summarize_text(request.text)
        
        elif request.action == "template":
            template_data = templates_db.get(request.template_name or "business_report")
            result = {
                "type": "template",
                "title": template_data["name"],
                "content": template_data["content"],
                "variables": template_data["variables"]
            }
        
        elif request.action == "analyze":
            result = await analyze_text(request.text)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
        
        # Log usage
        log_entry = UsageLog(
            action=request.action,
            timestamp=datetime.now().isoformat(),
            text_length=len(request.text),
            result_length=len(str(result))
        )
        usage_logs.append(log_entry)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/templates")
def get_templates():
    """Get all available templates"""
    return templates_db

@app.post("/templates")
def create_template(template: Template):
    """Create a new template"""
    templates_db[template.name.lower().replace(" ", "_")] = {
        "name": template.name,
        "content": template.content,
        "variables": template.variables
    }
    return {"message": "Template created", "template": template.name}

@app.get("/logs")
def get_logs(limit: int = 50):
    """Get usage logs"""
    return usage_logs[-limit:]

@app.get("/rules")
def get_correction_rules():
    """Get available correction rules"""
    return correction_rules

# AI Processing Functions
async def autocorrect_text(text: str, style: str = "formal") -> str:
    """Auto-correct text with AI"""
    if openai.api_key.startswith("your-"):
        # Mock AI response
        corrections = correction_rules.get(style, correction_rules["formal"])
        for wrong, correct in corrections["replacements"].items():
            text = text.replace(wrong, correct)
        
        # Basic grammar fixes
        text = text.capitalize()
        if not text.endswith((".", "!", "?")):
            text += "."
        
        return f"🤖 AI Corrected ({style}):\n{text}"
    
    # Real OpenAI API call
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a professional editor. Correct the text in {style} style."},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except:
        return f"Manual correction ({style}): {text}"

async def summarize_text(text: str) -> str:
    """Summarize text with AI"""
    if openai.api_key.startswith("your-"):
        # Mock summary
        words = text.split()
        if len(words) > 30:
            summary = " ".join(words[:30]) + "..."
        else:
            summary = text
        return f"📝 Summary ({len(words)} words → {len(summary.split())} words):\n{summary}"
    
    # Real OpenAI API call
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the text concisely."},
                {"role": "user", "content": text}
            ],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message.content
    except:
        return f"Mock summary: {text[:100]}..."

async def analyze_text(text: str) -> Dict:
    """Analyze text metrics"""
    words = text.split()
    sentences = text.split('.')
    
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
        "readability": "Easy" if len(words) < 15 else "Moderate" if len(words) < 30 else "Complex",
        "key_phrases": list(set([word.lower() for word in words if len(word) > 4]))[:5]
    }

async def autofill_template(template_name: str, context: str) -> Dict:
    """Autofill template with context"""
    template = templates_db.get(template_name or "business_report")
    if not template:
        return {"error": "Template not found"}
    
    # In production, use AI to extract variables from context
    variables = {}
    for var in template["variables"]:
        variables[var] = f"[{var.upper()}]"  # Placeholders
    
    filled_content = template["content"]
    for var, value in variables.items():
        filled_content = filled_content.replace(f"{{{var}}}", value)
    
    return {
        "type": "filled_template",
        "template": template["name"],
        "content": filled_content,
        "variables": variables
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)