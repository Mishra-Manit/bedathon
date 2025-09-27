## Voice Agent (Minimal Outbound Call)

This adds a minimal Twilio-powered outbound call to the FastAPI backend.

- `POST /voice/call`: initiate an outbound call to a phone number
- `GET|POST /voice/answer`: TwiML webhook that plays a greeting and hangs up

### Prerequisites

- Twilio account and a voice-enabled phone number
- Public URL for webhooks (e.g., using `ngrok`)
- Install backend deps:

```bash
cd /Users/manitmishra/Desktop/bedathon/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Environment variables

Create `backend/.env`:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1XXXXXXXXXX
# Public URL pointing to /voice/answer
VOICE_WEBHOOK_URL=https://your-public-domain.ngrok.io/voice/answer
```

If `VOICE_WEBHOOK_URL` is omitted, the request uses `/voice/answer` which is not reachable by Twilio unless tunneled.

### Run locally

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Expose locally with:

```bash
ngrok http 8000
```

Set the HTTPS URL from ngrok into `VOICE_WEBHOOK_URL` with `/voice/answer` appended.

### Trigger a call

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+1YOURMOBILE"}' \
  http://localhost:8000/voice/call
```

You should receive a call that speaks a short message and hangs up.

### Next steps

- Replace `/voice/answer` response with OpenAI Realtime voice loop.

