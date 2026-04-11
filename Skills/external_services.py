from .registry import registry
import smtplib
from email.message import EmailMessage

@registry.register(
    name="send_email",
    description="Sends an email using standard SMTP. Requires configuration in system context.",
    parameters={
        "to_email": {"type": "string", "description": "Target email address"},
        "subject": {"type": "string", "description": "Email subject"},
        "body": {"type": "string", "description": "Email body content"}
    }
)
def external_services(to_email: str, subject: str, body: str) -> str:
    # Requires an active SMTP server configured natively. Stub implementation.
    return f"Request to send email to {to_email} with subject '{subject}' queued (SMTP server not natively configured)."
