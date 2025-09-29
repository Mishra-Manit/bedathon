from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
from dotenv import load_dotenv
from typing import List, Optional
import logging

from agent import ClaudeAgent, AgentRequest, AgentResponse
from models import ProfileCreate, ProfileRead
from supabase_utils import (
    get_current_user,
    profiles_select_by_user_id,
    profiles_insert,
    profiles_update_by_user_id,
)
from supabase_matching_fastapi import matching_router
from voiceagent.router import router as voice_router

load_dotenv()

app = FastAPI(title="Claude Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include matching router
app.include_router(matching_router)
app.include_router(voice_router)

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
            messages=[{"role": msg.role, "content": msg.content} for msg in request.messages],
        )
        return ChatResponse(
            response=response.content[0].text,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
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


# Profiles endpoints used by the frontend to determine onboarding vs dashboard
@app.post("/profiles", response_model=ProfileRead)
async def create_profile(profile_data: ProfileCreate, user=Depends(get_current_user)):
    try:
        existing = profiles_select_by_user_id(user.id, token=getattr(user, "token", None))
        if existing:
            return ProfileRead(**existing[0])

        profile_dict = profile_data.dict()
        if profile_dict.get("move_in") is not None:
            profile_dict["move_in"] = profile_dict["move_in"].isoformat()
        profile_dict["user_id"] = user.id
        
        # Remove fields that don't exist in Supabase schema
        profile_dict.pop("max_distance_to_vt", None)
        profile_dict.pop("preferred_amenities", None)

        created = profiles_insert(profile_dict, token=getattr(user, "token", None))
        if created:
            return ProfileRead(**created[0])
        raise HTTPException(status_code=400, detail="Insert returned no data")
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Unexpected error creating profile for user_id=%s", getattr(user, "id", None))
        raise HTTPException(status_code=500, detail=f"Unexpected error creating profile: {str(e)}")


@app.get("/profiles/me", response_model=Optional[ProfileRead])
async def get_my_profile(user=Depends(get_current_user)):
    try:
        existing = profiles_select_by_user_id(user.id, token=getattr(user, "token", None))
        return ProfileRead(**existing[0]) if existing else None
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error fetching profile for user_id=%s", getattr(user, "id", None))
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")


@app.put("/profiles/me", response_model=ProfileRead)
async def update_my_profile(profile_data: ProfileCreate, user=Depends(get_current_user)):
    try:
        profile_dict = profile_data.dict()
        if profile_dict.get("move_in") is not None:
            profile_dict["move_in"] = profile_dict["move_in"].isoformat()
        updated = profiles_update_by_user_id(user.id, profile_dict, token=getattr(user, "token", None))
        if updated:
            return ProfileRead(**updated[0])
        existing = profiles_select_by_user_id(user.id)
        if existing:
            return ProfileRead(**existing[0])
        raise HTTPException(status_code=404, detail="Profile not found")
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error updating profile for user_id=%s", getattr(user, "id", None))
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
