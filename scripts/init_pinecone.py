"""Initialize Pinecone index with sample historical lead data."""
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from src.config import get_settings
import json

SAMPLE_HISTORICAL_LEADS = [
    {"lead_id": "hist-001", "industry": "B2B SaaS", "company_size": 42, "title": "VP Sales",
     "outcome": "closed_won", "days_to_close": 24, "deal_value": 22000,
     "close_signals": ["inbound_demo", "funding_event"], "objections": []},
    {"lead_id": "hist-002", "industry": "B2B SaaS", "company_size": 18, "title": "CEO",
     "outcome": "closed_won", "days_to_close": 31, "deal_value": 15000,
     "close_signals": ["referral", "rep_change"], "objections": ["timing"]},
    {"lead_id": "hist-003", "industry": "E-commerce", "company_size": 28, "title": "Head of Growth",
     "outcome": "closed_won", "days_to_close": 19, "deal_value": 18500,
     "close_signals": ["inbound_trial", "tech_stack_match"], "objections": []},
    {"lead_id": "hist-004", "industry": "B2B SaaS", "company_size": 120, "title": "VP Marketing",
     "outcome": "timing_objection", "days_to_close": None, "deal_value": None,
     "close_signals": [], "objections": ["budget_cycle", "wrong_quarter"]},
    {"lead_id": "hist-005", "industry": "E-commerce", "company_size": 65, "title": "Director of Operations",
     "outcome": "closed_lost", "days_to_close": None, "deal_value": None,
     "close_signals": [], "objections": ["no_budget", "existing_solution"]},
    {"lead_id": "hist-006", "industry": "HealthTech", "company_size": 35, "title": "CTO",
     "outcome": "closed_won", "days_to_close": 45, "deal_value": 38000,
     "close_signals": ["compliance_need", "inbound_contact"], "objections": ["security_review"]},
]


def build_text(lead: dict) -> str:
    return (
        f"Company size: {lead['company_size']} employees. "
        f"Industry: {lead['industry']}. "
        f"Title: {lead['title']}. "
        f"Outcome: {lead['outcome']}. "
        f"Close signals: {', '.join(lead['close_signals']) or 'none'}. "
        f"Objections: {', '.join(lead['objections']) or 'none'}."
    )


def init():
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    oai = OpenAI(api_key=settings.openai_api_key)

    # Create index if not exists
    if settings.pinecone_index_name not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"Created index: {settings.pinecone_index_name}")
    else:
        print(f"Index already exists: {settings.pinecone_index_name}")

    index = pc.Index(settings.pinecone_index_name)

    # Embed and upsert sample leads
    vectors = []
    for lead in SAMPLE_HISTORICAL_LEADS:
        text = build_text(lead)
        emb = oai.embeddings.create(model=settings.embedding_model, input=text)
        vectors.append({
            "id": lead["lead_id"],
            "values": emb.data[0].embedding,
            "metadata": lead,
        })
        print(f"  Embedded: {lead['lead_id']}")

    index.upsert(vectors=vectors)
    print(f"Upserted {len(vectors)} historical leads to Pinecone.")
    print("Init complete. Run: python src/server.py")


if __name__ == "__main__":
    init()
