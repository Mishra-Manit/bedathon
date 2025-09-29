from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import asyncio
from datetime import datetime

from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .config import get_twilio_settings, get_openai_settings, get_email_settings
import os


# Define data models first
class UserPreferences(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
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


async def _send_summary_email(recipient_email: str, recipient_name: str, summary: str, property_info: str = "") -> bool:
    """Send the conversation summary via email"""
    try:
        email_settings = get_email_settings()

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Apartment Inquiry Summary - {property_info}"
        message["From"] = f"{email_settings.from_name} <{email_settings.email_address}>"
        message["To"] = recipient_email

        # Create email body
        email_body = f"""
Dear {recipient_name},

Your VT Housing Assistant has completed an inquiry call on your behalf. Here's the summary of the information gathered:

{summary}

This information was collected during a phone call to help you make an informed decision about your housing options.

If you have any questions or need to schedule additional inquiries, please let us know.

Best regards,
VT Housing Assistant
Virginia Tech Student Housing Platform

---
This is an automated message from the VT Housing Assistant platform.
        """.strip()

        # Create plain text part
        text_part = MIMEText(email_body, "plain")
        message.attach(text_part)

        # Create HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #8B1538; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .summary {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #8B1538; margin: 20px 0; }}
        .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
        pre {{ white-space: pre-wrap; font-family: Arial, sans-serif; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 VT Housing Assistant</h1>
        <p>Apartment Inquiry Summary - {property_info}</p>
    </div>

    <div class="content">
        <p>Dear {recipient_name},</p>

        <p>Your VT Housing Assistant has completed an inquiry call on your behalf. Here's the summary of the information gathered:</p>

        <div class="summary">
            <pre>{summary}</pre>
        </div>

        <p>This information was collected during a phone call to help you make an informed decision about your housing options.</p>

        <p>If you have any questions or need to schedule additional inquiries, please let us know.</p>

        <p>Best regards,<br>
        <strong>VT Housing Assistant</strong><br>
        Virginia Tech Student Housing Platform</p>
    </div>

    <div class="footer">
        This is an automated message from the VT Housing Assistant platform.
    </div>
</body>
</html>
        """.strip()

        html_part = MIMEText(html_body, "html")
        message.attach(html_part)

        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(email_settings.smtp_server, email_settings.smtp_port) as server:
            server.starttls(context=context)
            server.login(email_settings.email_address, email_settings.email_password)
            server.sendmail(email_settings.email_address, recipient_email, message.as_string())

        print(f"Summary email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


async def _generate_conversation_summary(call_sid: str) -> str:
    """Generate a summary of the conversation for the student"""
    try:
        client = _create_openai_client()
        settings = get_openai_settings()

        conversation = conversation_sessions.get(call_sid)
        if not conversation:
            return "No conversation found to summarize."

        # Extract just the conversation messages (excluding system message)
        conversation_messages = conversation["messages"][1:]  # Skip system message

        # Create conversation transcript
        transcript = ""
        for msg in conversation_messages:
            role = "Assistant" if msg["role"] == "assistant" else "Leasing Office"
            transcript += f"{role}: {msg['content']}\n"

        # Generate summary
        summary_prompt = f"""Please create a comprehensive summary of this phone conversation between a housing assistant and a leasing office.

The assistant was calling on behalf of a Virginia Tech student to gather apartment information.

Conversation transcript:
{transcript}

Please provide a summary that includes:
1. Key information gathered about the property (availability, pricing, amenities, etc.)
2. Any special offers or student discounts mentioned
3. Application requirements and processes
4. Contact information or next steps mentioned
5. Any important details the student should know

Format the summary in a clear, organized way that would be helpful for the student to review."""

        response = client.chat.completions.create(
            model=settings.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates clear, organized summaries of housing-related phone conversations."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=500,
            temperature=0.3,
        )

        summary = response.choices[0].message.content

        # Store summary in conversation session
        conversation["summary"] = summary

        # Send email if user email is available
        user_context = conversation.get("user_context")
        if user_context and user_context.user_preferences:
            user_prefs = user_context.user_preferences
            if user_prefs.email and user_prefs.name:
                property_info = ""
                if user_context.apartment_info and user_context.apartment_info.name:
                    property_info = user_context.apartment_info.name

                # Send email asynchronously
                await _send_summary_email(
                    recipient_email=user_prefs.email,
                    recipient_name=user_prefs.name,
                    summary=summary,
                    property_info=property_info
                )

        return summary

    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Error generating conversation summary."


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
                context_info += f"You are calling on behalf of: {prefs.name or 'Unknown'}, {prefs.year or 'Unknown year'} {prefs.major or 'Unknown major'} student\n"
                context_info += f"Student's Budget: ${prefs.budget or 'Unknown'}/month\n"
                context_info += f"Student Preferences - Cleanliness: {prefs.cleanliness or 'Unknown'}/5, Noise: {prefs.noise_level or 'Unknown'}/5, Study time: {prefs.study_time or 'Unknown'}/5\n"

            if user_context.apartment_info:
                apt = user_context.apartment_info
                context_info += f"Property of Interest: {apt.name or 'Unknown'}\n"
                context_info += f"Address: {apt.address or 'Unknown'}\n"
                context_info += f"Listed Price: {apt.price or 'Unknown'}\n"
                context_info += f"Bedrooms: {apt.bedrooms or 'Unknown'}\n"
                context_info += f"Distance to VT: {apt.distance or 'Unknown'}\n"
                context_info += f"Listed Amenities: {apt.amenities or 'Unknown'}\n"

            context_info += "\nINFORMATION TO GATHER:\n"
            context_info += "- Current availability and move-in dates\n"
            context_info += "- Current pricing and any student specials\n"
            context_info += "- Lease terms and requirements\n"
            context_info += "- Pet policies and parking availability\n"
            context_info += "- Utilities included and additional fees\n"
            context_info += "- Application process and requirements\n"
            context_info += "- Tour scheduling availability\n"
            context_info += "\nRemember to ask one question at a time and track what information you've already gathered.\n"

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

    # Create concise initial message based on user context
    if user_context and user_context.user_preferences:
        user_name = user_context.user_preferences.name or 'a Virginia Tech student'
        if user_context.apartment_info and user_context.apartment_info.name:
            property_name = user_context.apartment_info.name
            initial_message = f"Hi, I'm calling for {user_name}, a VT student interested in {property_name}. Do you have any current availability?"
        else:
            initial_message = f"Hi, I'm calling for {user_name}, a VT student. Do you have any current availability?"
    else:
        initial_message = "Hi, I'm calling for a VT student about rental availability. Do you have anything open?"

    response.say(initial_message, voice="Polly.Joanna")

    # Set up to gather speech input without additional prompting
    gather = Gather(
        input="speech",
        action="/voice/process-speech",
        speech_timeout="auto",
        language="en-US",
        enhanced=True
    )
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

        # Check if conversation should end based on AI response
        should_end_conversation = any(keyword in ai_response.lower() for keyword in [
            "thank you for your time", "i'll relay this information", "that's all the information i needed",
            "goodbye", "thank you for calling", "have a great day", "i have all the information i need"
        ])

        if should_end_conversation:
            # Generate and store summary before ending
            await _generate_conversation_summary(call_sid)
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
        "EMAIL_ADDRESS": bool(os.getenv("EMAIL_ADDRESS", "").strip()),
        "EMAIL_PASSWORD": bool(os.getenv("EMAIL_PASSWORD", "").strip()),
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


@router.get("/conversations/{call_sid}/summary")
def get_conversation_summary(call_sid: str):
    """Get the summary of a completed conversation"""
    if call_sid in conversation_sessions:
        conversation = conversation_sessions[call_sid]
        summary = conversation.get("summary", "No summary available yet.")
        return {
            "call_sid": call_sid,
            "summary": summary,
            "last_activity": conversation["last_activity"].isoformat(),
            "message_count": len(conversation["messages"])
        }
    return {"message": "Conversation not found"}


@router.get("/conversations/{call_sid}/summary/print")
def print_conversation_summary(call_sid: str):
    """Get a nicely formatted summary for printing"""
    if call_sid in conversation_sessions:
        conversation = conversation_sessions[call_sid]
        summary = conversation.get("summary", "No summary available yet.")

        # Get user context if available
        user_info = ""
        if conversation.get("user_context") and conversation["user_context"].user_preferences:
            user_prefs = conversation["user_context"].user_preferences
            user_info = f"Student: {user_prefs.name or 'Unknown'}\n"
            user_info += f"Budget: ${user_prefs.budget or 'Unknown'}/month\n"
            user_info += f"Year: {user_prefs.year or 'Unknown'}\n"
            user_info += f"Major: {user_prefs.major or 'Unknown'}\n\n"

        formatted_output = f"""
=== APARTMENT INQUIRY SUMMARY ===
Call ID: {call_sid}
Date: {conversation['last_activity'].strftime('%Y-%m-%d %H:%M:%S')}

{user_info}{summary}

=== END OF SUMMARY ===
        """.strip()

        return {"formatted_summary": formatted_output}
    return {"message": "Conversation not found"}


@router.delete("/conversations/{call_sid}")
def clear_conversation(call_sid: str):
    """Clear a specific conversation session"""
    if call_sid in conversation_sessions:
        del conversation_sessions[call_sid]
        return {"message": f"Conversation {call_sid} cleared"}
    return {"message": "Conversation not found"}

