"""Claude scoring agent with LangChain."""
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.models import PipelineState, LeadTier
from src.config import get_settings
import json, re


SYSTEM_PROMPT = """You are a senior B2B sales analyst scoring leads for a revenue team.
You receive an enriched lead record and context from historically similar leads with their outcomes.
Your job is to score the lead 0-100 and explain your reasoning concisely.

Scoring guidelines:
- 70-100 (HOT): Strong ICP match, high-seniority title, signals similar to closed-won deals
- 40-69 (WARM): Decent ICP fit, some positive signals, worth nurturing with sequence
- 0-39 (COLD): Poor ICP fit, weak signals, or patterns similar to ghosted/lost deals

Return ONLY valid JSON with these exact fields:
{
  "score": <integer 0-100>,
  "reasoning": "<2-3 sentence memo for the sales rep>",
  "recommended_sequence": "<sequence name>",
  "suggested_angle": "<opening angle for outreach>",
  "confidence": <float 0.0-1.0>
}"""


def score_lead(state: PipelineState) -> PipelineState:
    """Use Claude to score the lead with RAG context."""
    settings = get_settings()

    llm = ChatAnthropic(
        model=settings.anthropic_model,
        api_key=settings.anthropic_api_key,
        temperature=0.1,
    )

    lead = state.normalized_lead
    user_message = f"""Lead to score:
- Company: {lead['company']}
- Industry: {lead['industry']}
- Title: {lead['title']}
- Company size: {lead['company_size']} employees
- Lead source: {lead['lead_source']}
- Tech stack: {', '.join(lead['tech_stack']) or 'unknown'}
- Funding stage: {lead['funding_stage']}
- Rules-based score: {state.rules_score}/100

{state.context_text}

Score this lead."""

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    # Parse JSON response
    content = response.content.strip()
    # Extract JSON if wrapped in code block
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", content, re.DOTALL)
    if match:
        content = match.group(1)

    result = json.loads(content)

    state.ai_score = result["score"]
    state.reasoning = result["reasoning"]
    state.recommended_sequence = result["recommended_sequence"]
    state.suggested_angle = result["suggested_angle"]
    state.confidence = result["confidence"]
    return state
