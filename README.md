# Agentic Lead Scoring Engine
**myAutoBots.AI | Python + LangChain + LangGraph + Pinecone**

> RAG-backed lead intelligence engine. Scores B2B leads 0–100 using enrichment data, behavioral signals, and context retrieved from historical deal outcomes — not just rules.

📅 [Book a free 30-min revenue diagnostic](https://calendly.com/ssam8005/30min) · 🌐 [myautobots.ai](https://myautobots.ai)

**Used in:** [n8n Revenue Automation — Workflow 05](https://github.com/ssam8005/n8n-revenue-automation/blob/main/workflows/05-intent-scoring-pipeline.md)

---

## What This Does

Most lead scoring systems are rules-based: assign points for company size, title seniority, and industry match. That approach ignores the most valuable signal available — your own deal history.

This engine:
1. Embeds the enriched lead record
2. Retrieves the top-5 most similar historical leads from Pinecone (with their outcomes)
3. Passes lead + context to a LangGraph multi-agent pipeline for reasoning
4. Returns a score (0–100), tier (Hot/Warm/Cold), and natural-language reasoning memo

The scoring agent reasons like a senior sales rep reviewing a lead — not like a spreadsheet.

---

## Architecture

```mermaid
graph TD
    Input[Enriched Lead Record
JSON from n8n webhook] --> Preprocessor[Lead Preprocessor
Normalize + validate fields]
    Preprocessor --> Embedder[Embedding Agent
text-embedding-3-small]
    Embedder --> Pinecone[(Pinecone Index
lead-intelligence)]
    Pinecone --> Retriever[RAG Retriever
Top-K similar leads + outcomes]
    Retriever --> Context[Context Builder
Format retrieved leads for LLM]
    Context --> ScoringAgent[Scoring Agent
Claude claude-3-5-sonnet]
    Preprocessor --> ScoringAgent
    ScoringAgent --> Validator[Output Validator
Score range · required fields]
    Validator --> Response[Score Response
Score · Tier · Memo · Confidence]
    Response --> Webhook[Return to n8n
HTTP Response]

    subgraph LangGraph["LangGraph Multi-Agent Pipeline"]
        Preprocessor
        Embedder
        Retriever
        Context
        ScoringAgent
        Validator
    end

    style LangGraph fill:#0d2137,color:#e0e0e0,stroke:#5ba3f5
    style Pinecone fill:#1a1a2e,color:#e0e0e0,stroke:#00B4D8
```

---

## Multi-Agent Flow (LangGraph)

```mermaid
stateDiagram-v2
    [*] --> preprocess: Lead received
    preprocess --> embed: Normalized
    embed --> retrieve: Embedding ready
    retrieve --> build_context: Top-K retrieved
    build_context --> score: Context formatted
    score --> validate: Score generated
    validate --> [*]: Valid output
    validate --> score: Invalid — retry (max 2)
    score --> fallback: Max retries exceeded
    fallback --> [*]: Rules-based fallback score
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your API keys
```

### 3. Initialize Pinecone index

```bash
python scripts/init_pinecone.py
```

### 4. Run the scoring server

```bash
python src/server.py
# Starts webhook server on port 8080
```

### 5. Score a lead

```bash
curl -X POST http://localhost:8080/score \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "lead-001",
    "email": "jane.doe@example.com",
    "company": "Acme SaaS",
    "title": "VP Sales",
    "company_size": 45,
    "industry": "B2B SaaS",
    "lead_source": "inbound_demo_request",
    "enrichment_provider": "apollo"
  }'
```

### Example response

```json
{
  "lead_id": "lead-001",
  "score": 84,
  "tier": "HOT",
  "confidence": 0.91,
  "reasoning": "Strong ICP alignment — Series A SaaS company (45 employees), VP Sales with purchasing authority. Retrieved context: 3 of 5 most similar historical leads were closed-won, average 26 days to close. Common close signal: inbound demo request from VP-level (present here). Recommend same-day outreach.",
  "recommended_sequence": "saas-hot-6step",
  "suggested_angle": "Pipeline velocity at current growth stage",
  "processing_time_ms": 1840
}
```

---

## Repo Structure

```
agentic-lead-scoring/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── server.py              # FastAPI webhook server
│   ├── pipeline.py            # LangGraph pipeline definition
│   ├── agents/
│   │   ├── preprocessor.py    # Lead normalization agent
│   │   ├── embedder.py        # Embedding agent
│   │   ├── retriever.py       # Pinecone RAG retrieval agent
│   │   ├── scorer.py          # Claude scoring agent
│   │   └── validator.py       # Output validation agent
│   ├── models.py              # Pydantic models
│   └── config.py              # Configuration management
├── scripts/
│   └── init_pinecone.py       # Initialize Pinecone index with historical data
└── docs/
    └── architecture.md        # Extended architecture documentation
```

---

## Related Repos

- [neural-gtm-sprint](https://github.com/ssam8005/neural-gtm-sprint) — Full methodology and engagement framework
- [n8n-revenue-automation](https://github.com/ssam8005/n8n-revenue-automation) — Workflow 05 calls this server

---

*Built by [Sammy Samet](https://linkedin.com/in/ssamet) — Principal Technologist, [myAutoBots.AI](https://myautobots.ai)*
