"""Lead normalization and validation agent."""
from src.models import LeadInput, PipelineState

# ICP scoring weights for rules-based component
ICP_INDUSTRIES = {
    "B2B SaaS": 100, "SaaS": 100, "Software": 90,
    "E-commerce": 85, "Retail": 80, "HealthTech": 75,
    "FinTech": 75, "Professional Services": 70,
    "Digital Agency": 65, "Other": 40,
}

TARGET_TITLE_KEYWORDS = {
    "ceo": 100, "cto": 100, "coo": 95, "vp": 90,
    "head of": 85, "director": 80, "founder": 100,
    "principal": 85, "manager": 60, "lead": 55, "senior": 50,
}

COMPANY_SIZE_SCORES = [
    (1, 10, 40), (11, 50, 85), (51, 200, 90),
    (201, 500, 75), (501, 2000, 60), (2001, float("inf"), 40),
]

SOURCE_SCORES = {
    "inbound_demo_request": 100, "inbound_trial": 95,
    "inbound_contact_form": 80, "referral": 85,
    "outbound_cold": 40, "outbound_warm": 65,
    "event": 60, "content_download": 50,
}


def score_rules(lead: LeadInput) -> int:
    """Calculate rules-based firmographic score (0-100)."""
    scores = []

    # Industry fit (25% weight)
    industry_score = ICP_INDUSTRIES.get(lead.industry or "", 40)
    scores.append(("industry", industry_score, 0.25))

    # Company size (20% weight)
    size_score = 40
    for low, high, s in COMPANY_SIZE_SCORES:
        if lead.company_size and low <= lead.company_size <= high:
            size_score = s
            break
    scores.append(("size", size_score, 0.20))

    # Title seniority (25% weight)
    title_lower = (lead.title or "").lower()
    title_score = 40
    for keyword, score in TARGET_TITLE_KEYWORDS.items():
        if keyword in title_lower:
            title_score = score
            break
    scores.append(("title", title_score, 0.25))

    # Tech stack signals (15% weight)
    high_value_tech = {"hubspot", "salesforce", "clay", "apollo", "outreach", "salesloft"}
    tech_overlap = len(set(t.lower() for t in (lead.tech_stack or [])) & high_value_tech)
    tech_score = min(100, 40 + tech_overlap * 20)
    scores.append(("tech_stack", tech_score, 0.15))

    # Lead source (15% weight)
    source_score = SOURCE_SCORES.get(lead.lead_source or "", 40)
    scores.append(("source", source_score, 0.15))

    weighted = sum(s * w for _, s, w in scores)
    return round(weighted)


def normalize_lead(state: PipelineState) -> PipelineState:
    """Normalize lead fields and compute rules score."""
    lead = state.lead
    state.normalized_lead = {
        "lead_id": lead.lead_id,
        "company": lead.company,
        "title": lead.title or "Unknown",
        "company_size": lead.company_size or 0,
        "industry": lead.industry or "Unknown",
        "lead_source": lead.lead_source or "Unknown",
        "tech_stack": lead.tech_stack or [],
        "funding_stage": lead.funding_stage or "Unknown",
    }
    state.rules_score = score_rules(lead)
    return state
