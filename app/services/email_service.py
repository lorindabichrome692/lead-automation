import logging
from pathlib import Path

import resend
from jinja2 import Environment, FileSystemLoader

from app.config import get_settings

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
_jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def _init_resend():
    resend.api_key = get_settings().resend_api_key


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an email via Resend. Returns True on success."""
    _init_resend()
    settings = get_settings()
    try:
        params = {
            "from": settings.resend_from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        email = resend.Emails.send(params)
        logger.info("Email sent | to=%s | subject=%s | id=%s", to_email, subject, email.get("id"))
        return True
    except Exception as e:
        logger.error("Email send failed | to=%s | error=%s", to_email, e)
        return False


def send_followup(lead_data: dict, template_name: str) -> bool:
    """Render a Jinja2 template with lead data and send via Resend."""
    try:
        template = _jinja_env.get_template(f"{template_name}.html")
        html_content = template.render(**lead_data)
    except Exception as e:
        logger.error("Template render failed | template=%s | error=%s", template_name, e)
        return False

    subject_map = {
        "hot_lead": f"Great to hear from you, {lead_data.get('name', '')}! Let's get started",
        "warm_lead": f"{lead_data.get('name', '')}, here's how we can help your {lead_data.get('sector', 'business')} business",
        "cold_lead": f"Helpful resources for {lead_data.get('sector', 'business')} professionals",
    }
    subject = subject_map.get(template_name, "Following up on your inquiry")
    return send_email(lead_data["email"], subject, html_content)
