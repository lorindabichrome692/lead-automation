from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class LeadInput(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
    company: Optional[str] = None
    sector: Optional[str] = None
    source: str = "web_form"


class LeadScore(BaseModel):
    score: int = Field(..., ge=1, le=100)
    label: Literal["hot", "warm", "cold"]
    reason: str
    suggested_response: str


class LeadResponse(BaseModel):
    id: str
    status: str
    score: LeadScore


class WhatsAppPayload(BaseModel):
    # "from" is a reserved keyword in Python, so we use an alias
    phone: str = Field(..., alias="from")
    name: str
    message: str
    timestamp: str

    model_config = {"populate_by_name": True}
