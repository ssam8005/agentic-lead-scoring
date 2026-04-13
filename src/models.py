"""Pydantic models for the lead scoring engine."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from enum import Enum


class LeadTier(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"


class LeadInput(BaseModel):
    lead_id: str = Field(..., description="Unique identifier from CRM")
    email: str = Field(..., description="Business email address")
    company: str = Field(..., description="Company name")
    title: Optional[str] = Field(None, description="Job title")
    company_size: Optional[int] = Field(None, description="Employee count")
    industry: Optional[str] = Field(None, description="Industry classification")
    lead_source: Optional[str] = Field(None, description="Inbound / outbound / referral")
    enrichment_provider: Optional[str] = Field(None, description="Clay provider that matched")
    funding_stage: Optional[str] = Field(None, description="Seed / Series A / etc.")
    tech_stack: Optional[list[str]] = Field(default_factory=list, description="Detected technologies")
    linkedin_url: Optional[str] = None
    company_linkedin: Optional[str] = None


class HistoricalLead(BaseModel):
    lead_id: str
    industry: str
    company_size: int
    title: str
    outcome: Literal["closed_won", "closed_lost", "ghosted", "timing_objection", "nurture"]
    days_to_close: Optional[int] = None
    deal_value: Optional[float] = None
    close_signals: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    similarity_score: float = Field(..., ge=0.0, le=1.0)


class ScoreResponse(BaseModel):
    lead_id: str
    score: int = Field(..., ge=0, le=100)
    tier: LeadTier
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Natural language scoring memo for rep")
    recommended_sequence: str
    suggested_angle: str
    rules_score: int = Field(..., description="Rules-based component score")
    ai_score: int = Field(..., description="AI reasoning component score")
    retrieved_context_count: int = Field(..., description="Number of similar leads retrieved")
    processing_time_ms: int


class PipelineState(BaseModel):
    """LangGraph state object passed between agents."""
    lead: LeadInput
    normalized_lead: Optional[dict] = None
    embedding: Optional[list[float]] = None
    retrieved_leads: list[HistoricalLead] = Field(default_factory=list)
    context_text: Optional[str] = None
    rules_score: Optional[int] = None
    ai_score: Optional[int] = None
    final_score: Optional[int] = None
    tier: Optional[LeadTier] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None
    recommended_sequence: Optional[str] = None
    suggested_angle: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
