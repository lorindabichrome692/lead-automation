import logging
from datetime import datetime, timezone

from app.models.schemas import LeadScore
from app.services.crm import update_lead
from app.services.email_service import send_followup

logger = logging.getLogger(__name__)


def _build_lead_data(lead_fields: dict, score: LeadScore) -> dict:
    """Merge lead fields with score data for template rendering."""
    return {
        "name": lead_fields.get("name", ""),
        "email": lead_fields.get("email", ""),
        "company": lead_fields.get("company", ""),
        "sector": lead_fields.get("sector", ""),
        "message": lead_fields.get("message", ""),
        "score": score.score,
        "label": score.label,
        "reason": score.reason,
        "suggested_response": score.suggested_response,
    }


def _send_and_update(record_id: str, lead_data: dict, template: str):
    """Send follow-up email and update Airtable record."""
    success = send_followup(lead_data, template)
    if success:
        update_lead(record_id, {
            "Status": "contacted",
            "FollowUpCount": 1,
            "LastContactedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        })
        logger.info("Follow-up complete | record=%s | template=%s", record_id, template)
    else:
        logger.warning("Follow-up email failed | record=%s | template=%s", record_id, template)


def process_followup(lead_fields: dict, score: LeadScore, record_id: str, scheduler=None):
    """
    Determine follow-up strategy based on score and trigger email.

    - hot  (>=70): send immediately
    - warm (40-69): schedule for 24 hours later
    - cold (<40):  schedule for 7 days later
    """
    lead_data = _build_lead_data(lead_fields, score)

    if score.label == "hot":
        logger.info("Hot lead — sending email immediately | record=%s", record_id)
        _send_and_update(record_id, lead_data, "hot_lead")

    elif score.label == "warm":
        if scheduler:
            from datetime import timedelta
            run_time = datetime.now(timezone.utc) + timedelta(hours=24)
            scheduler.add_job(
                _send_and_update,
                "date",
                run_date=run_time,
                args=[record_id, lead_data, "warm_lead"],
                id=f"warm_{record_id}",
                replace_existing=True,
            )
            update_lead(record_id, {"Status": "follow_up_scheduled"})
            logger.info("Warm lead — email scheduled for %s | record=%s", run_time.isoformat(), record_id)
        else:
            # Fallback: send immediately if no scheduler available
            _send_and_update(record_id, lead_data, "warm_lead")

    else:  # cold
        if scheduler:
            from datetime import timedelta
            run_time = datetime.now(timezone.utc) + timedelta(days=7)
            scheduler.add_job(
                _send_and_update,
                "date",
                run_date=run_time,
                args=[record_id, lead_data, "cold_lead"],
                id=f"cold_{record_id}",
                replace_existing=True,
            )
            update_lead(record_id, {"Status": "follow_up_scheduled"})
            logger.info("Cold lead — email scheduled for %s | record=%s", run_time.isoformat(), record_id)
        else:
            _send_and_update(record_id, lead_data, "cold_lead")
