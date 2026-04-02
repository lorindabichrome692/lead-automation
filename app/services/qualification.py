import json
import logging

import anthropic

from app.config import get_settings
from app.models.schemas import LeadInput, LeadScore

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert lead qualification analyst. Analyze the incoming lead data and return a JSON response with exactly these fields:

{
  "score": <integer 1-100>,
  "label": "<hot|warm|cold>",
  "reason": "<brief explanation in English, max 2 sentences>",
  "suggested_response": "<personalized first response message to send to this lead, in English, max 3 sentences>"
}

Scoring criteria:
- Budget mentioned or implied: +20 points
- Urgent need expressed: +20 points
- Decision maker indicators: +15 points
- Clear/specific request: +15 points
- Company name provided: +10 points
- Relevant sector: +10 points
- Professional tone: +10 points

Labels:
- hot: score >= 70
- warm: score 40-69
- cold: score < 40

IMPORTANT: Return ONLY valid JSON. No markdown, no code fences, no extra text."""


def qualify_lead(lead: LeadInput) -> LeadScore:
    """Call Claude API to score and qualify an incoming lead."""
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    user_message = (
        f"Lead Data:\n"
        f"Name: {lead.name}\n"
        f"Email: {lead.email}\n"
        f"Company: {lead.company or 'Not provided'}\n"
        f"Sector: {lead.sector or 'Not provided'}\n"
        f"Phone: {lead.phone or 'Not provided'}\n"
        f"Message: {lead.message}"
    )

    def _call_claude() -> dict:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = message.content[0].text.strip()
        logger.debug("Claude raw response: %s", raw)
        return json.loads(raw)

    try:
        data = _call_claude()
    except json.JSONDecodeError as e:
        logger.warning("JSON parse failed on first attempt (%s), retrying...", e)
        try:
            data = _call_claude()
        except json.JSONDecodeError as e2:
            logger.error("JSON parse failed on retry: %s", e2)
            raise ValueError(f"Claude returned invalid JSON after retry: {e2}") from e2
    except anthropic.APIError as e:
        logger.error("Claude API error: %s", e)
        raise

    # Clamp score to 1-100 just in case
    score = max(1, min(100, int(data["score"])))

    # Derive label from score if Claude returns an inconsistent value
    if score >= 70:
        label = "hot"
    elif score >= 40:
        label = "warm"
    else:
        label = "cold"

    result = LeadScore(
        score=score,
        label=label,
        reason=data["reason"],
        suggested_response=data["suggested_response"],
    )

    logger.info(
        "Lead qualified | name=%s | score=%d | label=%s",
        lead.name,
        result.score,
        result.label,
    )
    return result
