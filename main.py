from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🌍 ALLOW CORS: This lets your frontend talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your Render frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Backend is running!"}

@app.post("/generate")
async def generate_text(data: dict):
    # This is where your AI logic will go later
    user_text = data.get("text", "")
    return {
        "status": "success",
        "generated_text": f"AI processed: {user_text}"
    }