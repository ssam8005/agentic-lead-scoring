"""Output validation and final score assembly."""
from src.models import PipelineState, LeadTier
from src.config import get_settings


SEQUENCE_MAP = {
    "B2B SaaS": {"HOT": "saas-hot-6step", "WARM": "saas-warm-8step", "COLD": "nurture-quarterly"},
    "E-commerce": {"HOT": "ecom-hot-5step", "WARM": "ecom-warm-7step", "COLD": "nurture-quarterly"},
}
DEFAULT_SEQUENCES = {"HOT": "general-hot-6step", "WARM": "general-warm-7step", "COLD": "nurture-quarterly"}


def validate_and_finalize(state: PipelineState) -> PipelineState:
    """Validate AI output, compute final blended score, assign tier."""
    settings = get_settings()

    # Validate score range
    if not (0 <= (state.ai_score or 0) <= 100):
        state.error = f"AI score out of range: {state.ai_score}"
        state.retry_count += 1
        return state

    # Blend scores
    ai_w = settings.ai_weight
    rules_w = settings.rules_weight
    blended = round(ai_w * (state.ai_score or 0) + rules_w * (state.rules_score or 0))
    state.final_score = max(0, min(100, blended))

    # Assign tier
    if state.final_score >= settings.hot_threshold:
        state.tier = LeadTier.HOT
    elif state.final_score >= settings.warm_threshold:
        state.tier = LeadTier.WARM
    else:
        state.tier = LeadTier.COLD

    # Ensure sequence is set
    if not state.recommended_sequence:
        industry = state.normalized_lead.get("industry", "")
        seqs = SEQUENCE_MAP.get(industry, DEFAULT_SEQUENCES)
        state.recommended_sequence = seqs[state.tier.value]

    state.error = None
    return state
