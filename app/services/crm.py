import logging
from datetime import datetime, timezone
from typing import Optional

from pyairtable import Api

from app.config import get_settings
from app.models.schemas import LeadInput, LeadScore

logger = logging.getLogger(__name__)


def _get_table():
    settings = get_settings()
    api = Api(settings.airtable_api_key)
    return api.table(settings.airtable_base_id, settings.airtable_table_name)


def create_lead(lead: LeadInput, score: LeadScore) -> str:
    """Create a new record in Airtable. Returns the record ID."""
    table = _get_table()
    fields = {
        "Name": lead.name,
        "Email": lead.email,
        "Message": lead.message,
        "Score": score.score,
        "Label": score.label,
        "Reason": score.reason,
        "SuggestedResponse": score.suggested_response,
        "Source": lead.source,
        "Status": "new",
        "FollowUpCount": 0,
    }
    if lead.phone:
        fields["Phone"] = lead.phone
    if lead.company:
        fields["Company"] = lead.company
    if lead.sector:
        fields["Sector"] = lead.sector

    try:
        record = table.create(fields)
        record_id = record["id"]
        logger.info("Airtable record created | id=%s | name=%s", record_id, lead.name)
        return record_id
    except Exception as e:
        logger.error("Airtable create_lead failed: %s", e)
        raise


def update_lead(record_id: str, fields: dict) -> None:
    """Update specific fields on an existing Airtable record."""
    table = _get_table()
    try:
        table.update(record_id, fields)
        logger.info("Airtable record updated | id=%s | fields=%s", record_id, list(fields.keys()))
    except Exception as e:
        logger.error("Airtable update_lead failed | id=%s | error=%s", record_id, e)
        raise


def get_leads(label: Optional[str] = None, status: Optional[str] = None) -> list:
    """Fetch leads from Airtable with optional filters."""
    table = _get_table()
    formula_parts = []
    if label:
        formula_parts.append(f"{{Label}}='{label}'")
    if status:
        formula_parts.append(f"{{Status}}='{status}'")

    formula = None
    if len(formula_parts) == 1:
        formula = formula_parts[0]
    elif len(formula_parts) > 1:
        formula = "AND(" + ", ".join(formula_parts) + ")"

    try:
        records = table.all(formula=formula) if formula else table.all()
        logger.info("Airtable get_leads | count=%d | label=%s | status=%s", len(records), label, status)
        return records
    except Exception as e:
        logger.error("Airtable get_leads failed: %s", e)
        raise


def get_lead_stats() -> dict:
    """Return counts by label, by status, and total."""
    records = get_leads()
    stats = {
        "total": len(records),
        "by_label": {"hot": 0, "warm": 0, "cold": 0},
        "by_status": {
            "new": 0,
            "contacted": 0,
            "follow_up_scheduled": 0,
            "converted": 0,
            "lost": 0,
        },
    }
    for r in records:
        f = r.get("fields", {})
        label = f.get("Label", "").lower()
        status = f.get("Status", "").lower()
        if label in stats["by_label"]:
            stats["by_label"][label] += 1
        if status in stats["by_status"]:
            stats["by_status"][status] += 1
    return stats
