import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


# Load environment from backend/.env and backend/.env.local regardless of CWD
_voiceagent_dir = os.path.dirname(__file__)
_backend_dir = os.path.abspath(os.path.join(_voiceagent_dir, ".."))
_env_path = os.path.join(_backend_dir, ".env")
_env_local_path = os.path.join(_backend_dir, ".env.local")

# Load base .env first (no override), then .env.local with override=True
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=False)
if os.path.exists(_env_local_path):
    load_dotenv(_env_local_path, override=True)

# Also load from voiceagent/.env and voiceagent/.env.local
_va_env_path = os.path.join(_voiceagent_dir, ".env")
_va_env_local_path = os.path.join(_voiceagent_dir, ".env.local")
if os.path.exists(_va_env_path):
    load_dotenv(_va_env_path, override=False)
if os.path.exists(_va_env_local_path):
    load_dotenv(_va_env_local_path, override=True)

# Finally, fallback to current working directory `.env` search (does not override)
load_dotenv(override=False)


@dataclass
class TwilioSettings:
    account_sid: str
    auth_token: str
    from_number: str
    voice_webhook_url: Optional[str] = None


@dataclass
class OpenAISettings:
    api_key: str
    model: str = "gpt-4o-mini"


@dataclass
class EmailSettings:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_address: str = ""
    email_password: str = ""
    from_name: str = "VT Housing Assistant"


def get_twilio_settings() -> TwilioSettings:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_number = os.getenv("TWILIO_FROM_NUMBER", "").strip()
    voice_webhook_url = os.getenv("VOICE_WEBHOOK_URL", "").strip() or None

    if not account_sid or not auth_token or not from_number:
        missing = [
            name
            for name, value in (
                ("TWILIO_ACCOUNT_SID", account_sid),
                ("TWILIO_AUTH_TOKEN", auth_token),
                ("TWILIO_FROM_NUMBER", from_number),
            )
            if not value
        ]
        raise RuntimeError(
            f"Missing required Twilio environment variables: {', '.join(missing)}"
        )

    return TwilioSettings(
        account_sid=account_sid,
        auth_token=auth_token,
        from_number=from_number,
        voice_webhook_url=voice_webhook_url,
    )


def get_openai_settings() -> OpenAISettings:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        raise RuntimeError("Missing required OPENAI_API_KEY environment variable")

    return OpenAISettings(
        api_key=api_key,
        model=model,
    )


def get_email_settings() -> EmailSettings:
    email_address = os.getenv("EMAIL_ADDRESS", "").strip()
    email_password = os.getenv("EMAIL_PASSWORD", "").strip()
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    from_name = os.getenv("EMAIL_FROM_NAME", "VT Housing Assistant").strip()

    if not email_address or not email_password:
        raise RuntimeError("Missing required EMAIL_ADDRESS or EMAIL_PASSWORD environment variables")

    return EmailSettings(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        email_address=email_address,
        email_password=email_password,
        from_name=from_name,
    )


