from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import asyncio
from datetime import datetime

from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai

from .config import get_twilio_settings, get_openai_settings
import os


# Define data models first
class UserPreferences(BaseModel):
    name: Optional[str] = None
    budget: Optional[int] = None
    year: Optional[str] = None
    major: Optional[str] = None
    cleanliness: Optional[int] = None
    noise_level: Optional[int] = None
    study_time: Optional[int] = None
    social_level: Optional[int] = None
    sleep_schedule: Optional[int] = None

class ApartmentInfo(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    price: Optional[str] = None
    bedrooms: Optional[str] = None
    distance: Optional[str] = None
    lease_type: Optional[str] = None
    pets: Optional[str] = None
    parking: Optional[str] = None
    amenities: Optional[str] = None

class UserContext(BaseModel):
    user_preferences: Optional[UserPreferences] = None
    apartment_info: Optional[ApartmentInfo] = None

router = APIRouter(prefix="/voice", tags=["voice"])

# In-memory conversation state storage (in production, use Redis or database)
conversation_sessions: Dict[str, Dict] = {}

# Store user context temporarily by call SID for new calls
pending_call_contexts: Dict[str, UserContext] = {}

class OutboundCallRequest(BaseModel):
    to_number: str
    prompt: Optional[str] = None
    user_context: Optional[UserContext] = None


class ConversationState(BaseModel):
    call_sid: str
    messages: List[Dict[str, str]]
    context: str
    last_activity: datetime
    user_context: Optional[UserContext] = None


def _create_twilio_client() -> TwilioClient:
    settings = get_twilio_settings()
    return TwilioClient(settings.account_sid, settings.auth_token)


def _create_openai_client():
    settings = get_openai_settings()
    return openai.OpenAI(api_key=settings.api_key)


def _get_conversation_context() -> str:
    """Load the housing agent context from prompt.md"""
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful voice assistant for Virginia Tech students looking for housing."


def _get_or_create_conversation(call_sid: str, user_context: Optional[UserContext] = None) -> Dict:
    """Get existing conversation or create a new one"""
    if call_sid not in conversation_sessions:
        conversation_sessions[call_sid] = {
            "messages": [
                {
                    "role": "system",
                    "content": _get_conversation_context() + "\n\nYou are speaking over the phone, so keep responses concise and conversational. Ask one question at a time."
                }
            ],
            "context": _get_conversation_context(),
            "last_activity": datetime.now(),
            "user_context": user_context
        }
    else:
        conversation_sessions[call_sid]["last_activity"] = datetime.now()

    return conversation_sessions[call_sid]


async def _get_ai_response(call_sid: str, user_input: str) -> str:
    """Get AI response using OpenAI"""
    try:
        client = _create_openai_client()
        settings = get_openai_settings()

        conversation = _get_or_create_conversation(call_sid)

        # Add user message to conversation
        conversation["messages"].append({
            "role": "user",
            "content": user_input
        })

        # Enhance system message with user context if available
        messages_for_ai = conversation["messages"].copy()
        if conversation.get("user_context"):
            user_context = conversation["user_context"]
            context_info = "\n\nCONTEXT FOR THIS CALL:\n"

            if user_context.user_preferences:
                prefs = user_context.user_preferences
                context_info += f"User: {prefs.name or 'Unknown'}, {prefs.year or 'Unknown year'} {prefs.major or 'Unknown major'} student\n"
                context_info += f"Budget: ${prefs.budget or 'Unknown'}/month\n"
                context_info += f"Preferences - Cleanliness: {prefs.cleanliness or 'Unknown'}/5, Noise: {prefs.noise_level or 'Unknown'}/5, Study time: {prefs.study_time or 'Unknown'}/5\n"

            if user_context.apartment_info:
                apt = user_context.apartment_info
                context_info += f"Interested Property: {apt.name or 'Unknown'}\n"
                context_info += f"Address: {apt.address or 'Unknown'}\n"
                context_info += f"Listed Price: {apt.price or 'Unknown'}\n"
                context_info += f"Bedrooms: {apt.bedrooms or 'Unknown'}\n"
                context_info += f"Distance to VT: {apt.distance or 'Unknown'}\n"
                context_info += f"Amenities: {apt.amenities or 'Unknown'}\n"

            # Update the system message to include context
            messages_for_ai[0]["content"] += context_info

        # Get AI response
        response = client.chat.completions.create(
            model=settings.model,
            messages=messages_for_ai,
            max_tokens=150,  # Keep responses short for phone calls
            temperature=0.7,
        )

        ai_response = response.choices[0].message.content

        # Add AI response to conversation
        conversation["messages"].append({
            "role": "assistant",
            "content": ai_response
        })

        return ai_response

    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "I'm having trouble processing that. Could you please repeat what you said?"


@router.post("/call")
def start_outbound_call(req: OutboundCallRequest):
    """Initiate an outbound call to the given number.

    For now, this will simply play a brief message using a TwiML Bin endpoint
    hosted by our own webhook handler at `/voice/answer`.
    """
    try:
        settings = get_twilio_settings()
        twilio_client = _create_twilio_client()

        # Determine the webhook URL that Twilio should request when the call is answered
        # If VOICE_WEBHOOK_URL is provided, use it (e.g., your public ngrok/production URL)
        # otherwise default to relative path (useful for local docs, but Twilio needs public URL)
        webhook_url = settings.voice_webhook_url or "/voice/answer"

        call = twilio_client.calls.create(
            to=req.to_number,
            from_=settings.from_number,
            url=webhook_url,
        )

        # Store user context for this call SID to use when call is answered
        if req.user_context:
            pending_call_contexts[call.sid] = req.user_context

        return {"sid": call.sid, "status": call.status}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/answer")
@router.get("/answer")
async def answer_call(request: Request):
    """Initial call answer - starts the conversation"""
    form = await request.form()
    call_sid = form.get("CallSid", "unknown")

    # Get user context for this call if available
    user_context = pending_call_contexts.pop(call_sid, None)

    # Initialize conversation with user context
    _get_or_create_conversation(call_sid, user_context)

    response = VoiceResponse()

    # Create personalized initial message based on user context
    if user_context and user_context.user_preferences and user_context.apartment_info:
        user_prefs = user_context.user_preferences
        apartment = user_context.apartment_info

        initial_message = f"Hello {user_prefs.name or 'there'}! I'm your housing assistant for Virginia Tech students. "
        initial_message += f"I can see you're interested in {apartment.name} at {apartment.address}. "
        initial_message += f"Based on your profile, you're a {user_prefs.year or 'student'} majoring in {user_prefs.major or 'your field'} "
        initial_message += f"with a budget of around ${user_prefs.budget or 'your specified amount'} per month. "
        initial_message += f"The property shows {apartment.bedrooms} and is priced at {apartment.price}. "
        initial_message += f"I'm calling to get the latest availability and pricing information for you. How can I help you with this property today?"
    elif user_context and user_context.apartment_info:
        apartment = user_context.apartment_info
        initial_message = f"Hello! I'm your housing assistant for Virginia Tech students. "
        initial_message += f"I can see you're interested in {apartment.name} at {apartment.address}. "
        initial_message += f"The property shows {apartment.bedrooms} and is priced at {apartment.price}. "
        initial_message += f"I'm calling to get the latest availability and pricing information for you. How can I help you today?"
    else:
        initial_message = "Hello! I'm your housing assistant for Virginia Tech students. I can help you find apartments, negotiate prices, and schedule tours. How can I help you today?"

    response.say(initial_message, voice="Polly.Joanna")

    # Set up to gather speech input
    gather = Gather(
        input="speech",
        action="/voice/process-speech",
        speech_timeout="auto",
        language="en-US",
        enhanced=True
    )
    gather.say("Please tell me what you're looking for.", voice="Polly.Joanna")
    response.append(gather)

    # Fallback if no input detected
    response.say("I didn't hear anything. Please call back when you're ready to chat!", voice="Polly.Joanna")
    response.hangup()

    return Response(content=str(response), media_type="application/xml")


@router.post("/process-speech")
async def process_speech(request: Request):
    """Process user speech input and continue conversation"""
    form = await request.form()
    call_sid = form.get("CallSid", "unknown")
    speech_result = form.get("SpeechResult", "")
    confidence = form.get("Confidence", "0.0")

    response = VoiceResponse()

    # Check if speech was understood
    if not speech_result or float(confidence) < 0.5:
        response.say("I didn't quite catch that. Could you please repeat?", voice="Polly.Joanna")
        gather = Gather(
            input="speech",
            action="/voice/process-speech",
            speech_timeout="auto",
            language="en-US",
            enhanced=True
        )
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    try:
        # Get AI response
        ai_response = await _get_ai_response(call_sid, speech_result)

        # Speak the AI response
        response.say(ai_response, voice="Polly.Joanna")

        # Continue conversation or end based on response
        if any(keyword in ai_response.lower() for keyword in ["goodbye", "thank you for calling", "have a great day"]):
            response.hangup()
        else:
            # Continue gathering input
            gather = Gather(
                input="speech",
                action="/voice/process-speech",
                speech_timeout="auto",
                language="en-US",
                enhanced=True
            )
            response.append(gather)

            # Fallback after timeout
            response.say("I didn't hear a response. Feel free to call back anytime!", voice="Polly.Joanna")
            response.hangup()

    except Exception as e:
        print(f"Error processing speech: {e}")
        response.say("I'm experiencing technical difficulties. Please try calling back in a moment.", voice="Polly.Joanna")
        response.hangup()

    return Response(content=str(response), media_type="application/xml")


@router.get("/env-check")
def env_check():
    """Return presence (not values) of required env vars to aid debugging."""
    present = {
        "TWILIO_ACCOUNT_SID": bool(os.getenv("TWILIO_ACCOUNT_SID", "").strip()),
        "TWILIO_AUTH_TOKEN": bool(os.getenv("TWILIO_AUTH_TOKEN", "").strip()),
        "TWILIO_FROM_NUMBER": bool(os.getenv("TWILIO_FROM_NUMBER", "").strip()),
        "VOICE_WEBHOOK_URL": bool(os.getenv("VOICE_WEBHOOK_URL", "").strip()),
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY", "").strip()),
    }
    return {"present": present}


@router.get("/conversations")
def get_conversations():
    """Debug endpoint to view active conversations"""
    return {
        "active_conversations": len(conversation_sessions),
        "sessions": {
            call_sid: {
                "message_count": len(session["messages"]),
                "last_activity": session["last_activity"].isoformat(),
            }
            for call_sid, session in conversation_sessions.items()
        }
    }


@router.delete("/conversations/{call_sid}")
def clear_conversation(call_sid: str):
    """Clear a specific conversation session"""
    if call_sid in conversation_sessions:
        del conversation_sessions[call_sid]
        return {"message": f"Conversation {call_sid} cleared"}
    return {"message": "Conversation not found"}

