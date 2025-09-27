from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional

from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse

from .config import get_twilio_settings
import os


router = APIRouter(prefix="/voice", tags=["voice"])


class OutboundCallRequest(BaseModel):
    to_number: str
    prompt: Optional[str] = None


def _create_twilio_client() -> TwilioClient:
    settings = get_twilio_settings()
    return TwilioClient(settings.account_sid, settings.auth_token)


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

        return {"sid": call.sid, "status": call.status}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/answer")
@router.get("/answer")
async def answer_call(request: Request, prompt: Optional[str] = None):
    """Basic TwiML that greets and hangs up.

    This is the minimal placeholder while we wire in OpenAI Realtime.
    """
    response = VoiceResponse()
    message = (
        prompt
        or "Hello from VT Hacks voice agent. This is a test call. Goodbye."
    )
    response.say(message, voice="Polly.Joanna")
    response.hangup()
    return Response(content=str(response), media_type="application/xml")


@router.get("/env-check")
def env_check():
    """Return presence (not values) of required Twilio env vars to aid debugging."""
    present = {
        "TWILIO_ACCOUNT_SID": bool(os.getenv("TWILIO_ACCOUNT_SID", "").strip()),
        "TWILIO_AUTH_TOKEN": bool(os.getenv("TWILIO_AUTH_TOKEN", "").strip()),
        "TWILIO_FROM_NUMBER": bool(os.getenv("TWILIO_FROM_NUMBER", "").strip()),
        "VOICE_WEBHOOK_URL": bool(os.getenv("VOICE_WEBHOOK_URL", "").strip()),
    }
    return {"present": present}

