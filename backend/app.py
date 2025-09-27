from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
from agent import ClaudeAgent, AgentRequest, AgentResponse
from supabase_utils import get_current_user

load_dotenv()

app = FastAPI(title="Claude Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
agent = ClaudeAgent(client)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 1000
    model: Optional[str] = "claude-3-sonnet-20240229"

class ChatResponse(BaseModel):
    response: str
    usage: Optional[dict] = None

@app.get("/")
async def root():
    return {"message": "Claude Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/auth/me")
async def auth_me(user=Depends(get_current_user)):
    # Return a subset of user info
    return {
        "id": getattr(user, "id", None),
        "email": getattr(getattr(user, "email", None), "__str__", lambda: user.email)() if hasattr(user, "email") else None,
        "app_metadata": getattr(user, "app_metadata", None),
        "user_metadata": getattr(user, "user_metadata", None),
        "aud": getattr(user, "aud", None),
        "role": getattr(user, "role", None),
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_claude(request: ChatRequest):
    try:
        response = client.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            messages=[{"role": msg.role, "content": msg.content} for msg in request.messages]
        )

        return ChatResponse(
            response=response.content[0].text,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Claude: {str(e)}")

@app.post("/agent", response_model=AgentResponse)
async def agent_request(request: AgentRequest):
    try:
        response = await agent.process_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/agent/history")
async def get_agent_history():
    return {"history": agent.get_history()}

@app.post("/agent/clear")
async def clear_agent_history():
    agent.clear_history()
    return {"message": "Agent history cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)