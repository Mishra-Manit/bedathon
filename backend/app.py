from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
<<<<<<< Updated upstream
from agent import ClaudeAgent, AgentRequest, AgentResponse
from supabase_utils import get_current_user
from sqlmodel import Session, create_engine, select
from models import ApartmentComplex, ApartmentComplexRead, ApartmentComplexCreate
=======
from .agent import ClaudeAgent, AgentRequest, AgentResponse
from .voiceagent.router import router as voice_router
from .supabase_utils import get_current_user
>>>>>>> Stashed changes

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

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bedathon.db")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

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

<<<<<<< Updated upstream
# Apartment API endpoints
@app.get("/apartments", response_model=List[ApartmentComplexRead])
async def get_apartments(
    session: Session = Depends(get_session),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    min_bedrooms: Optional[int] = Query(None, ge=0),
    max_bedrooms: Optional[int] = Query(None, ge=0),
    max_distance: Optional[float] = Query(None, ge=0),
    pets_allowed: Optional[bool] = Query(None),
    parking_included: Optional[bool] = Query(None),
    furniture_included: Optional[bool] = Query(None)
):
    """Get apartment complexes with optional filtering."""
    query = select(ApartmentComplex)
    
    # Apply filters
    if search:
        query = query.where(ApartmentComplex.name.contains(search))
    
    if min_bedrooms is not None:
        # This is a simplified filter - in a real app you'd want more sophisticated logic
        pass
    
    if max_bedrooms is not None:
        # This is a simplified filter - in a real app you'd want more sophisticated logic
        pass
    
    if max_distance is not None:
        query = query.where(ApartmentComplex.distance_to_burruss <= max_distance)
    
    if pets_allowed is not None:
        query = query.where(ApartmentComplex.pets_allowed == pets_allowed)
    
    if parking_included is not None:
        query = query.where(ApartmentComplex.parking_included == parking_included)
    
    if furniture_included is not None:
        query = query.where(ApartmentComplex.furniture_included == furniture_included)
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    apartments = session.exec(query).all()
    return apartments

@app.get("/apartments/{apartment_id}", response_model=ApartmentComplexRead)
async def get_apartment(
    apartment_id: str,
    session: Session = Depends(get_session)
):
    """Get a specific apartment complex by ID."""
    apartment = session.get(ApartmentComplex, apartment_id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment

@app.post("/apartments", response_model=ApartmentComplexRead)
async def create_apartment(
    apartment: ApartmentComplexCreate,
    session: Session = Depends(get_session)
):
    """Create a new apartment complex."""
    db_apartment = ApartmentComplex(**apartment.model_dump())
    session.add(db_apartment)
    session.commit()
    session.refresh(db_apartment)
    return db_apartment

@app.put("/apartments/{apartment_id}", response_model=ApartmentComplexRead)
async def update_apartment(
    apartment_id: str,
    apartment_update: ApartmentComplexCreate,
    session: Session = Depends(get_session)
):
    """Update an existing apartment complex."""
    apartment = session.get(ApartmentComplex, apartment_id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    for key, value in apartment_update.model_dump().items():
        setattr(apartment, key, value)
    
    session.add(apartment)
    session.commit()
    session.refresh(apartment)
    return apartment

@app.delete("/apartments/{apartment_id}")
async def delete_apartment(
    apartment_id: str,
    session: Session = Depends(get_session)
):
    """Delete an apartment complex."""
    apartment = session.get(ApartmentComplex, apartment_id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    session.delete(apartment)
    session.commit()
    return {"message": "Apartment deleted successfully"}

@app.post("/apartments/import")
async def import_apartments_data(session: Session = Depends(get_session)):
    """Import apartment data from the Google Sheets."""
    try:
        from import_apartments import import_apartments
        import_apartments()
        return {"message": "Apartment data imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing apartment data: {str(e)}")
=======
# Mount voice agent routes
app.include_router(voice_router)
>>>>>>> Stashed changes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)