import logging

from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import LeadInput, LeadResponse, LeadScore, WhatsAppPayload
from app.services.crm import create_lead
from app.services.followup import process_followup
from app.services.qualification import qualify_lead

logger = logging.getLogger(__name__)

router = APIRouter()


def _process_lead(lead: LeadInput, scheduler=None) -> LeadResponse:
    """Qualify → save to Airtable → trigger follow-up email."""
    # Step 1: Qualify with Claude
    try:
        score: LeadScore = qualify_lead(lead)
    except Exception as e:
        logger.error("Qualification failed for %s: %s", lead.email, e)
        raise HTTPException(status_code=500, detail=f"Lead qualification failed: {e}")

    # Step 2: Save to Airtable
    try:
        record_id = create_lead(lead, score)
    except Exception as e:
        logger.error("CRM save failed for %s: %s", lead.email, e)
        raise HTTPException(status_code=500, detail=f"CRM save failed: {e}")

    # Step 3: Trigger follow-up email
    try:
        lead_fields = {
            "name": lead.name,
            "email": lead.email,
            "company": lead.company or "",
            "sector": lead.sector or "",
            "message": lead.message,
        }
        process_followup(lead_fields, score, record_id, scheduler=scheduler)
    except Exception as e:
        # Non-fatal: log but don't fail the request
        logger.error("Follow-up failed for %s: %s", record_id, e)

    logger.info(
        "Lead pipeline complete | id=%s | name=%s | source=%s | score=%d | label=%s",
        record_id, lead.name, lead.source, score.score, score.label,
    )

    return LeadResponse(id=record_id, status="received", score=score)


@router.post("/api/lead", response_model=LeadResponse)
async def submit_lead(lead: LeadInput, request: Request):
    """Accept a lead from the web form, qualify it, save to Airtable, trigger follow-up."""
    scheduler = getattr(request.app.state, "scheduler", None)
    return _process_lead(lead, scheduler=scheduler)


@router.post("/api/whatsapp-webhook", response_model=LeadResponse)
async def whatsapp_webhook(payload: WhatsAppPayload, request: Request):
    """Simulate an incoming WhatsApp message and run it through the lead pipeline."""
    lead = LeadInput(
        name=payload.name,
        email="pending@whatsapp.placeholder",
        phone=payload.phone,
        message=payload.message,
        source="whatsapp",
    )
    scheduler = getattr(request.app.state, "scheduler", None)
    return _process_lead(lead, scheduler=scheduler)
