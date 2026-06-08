"""
Ingest synthetic company knowledge base into ChromaDB.
Run once: python -m utils.ingest
"""
import os
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

SYNTHETIC_DOCS = [
    {
        "id": "acme-1",
        "content": """Acme Corp is a mid-market SaaS company focused on supply chain logistics.
Founded 2015, Series C ($120M). 800 employees. HQ: Austin, TX.
Key pain points: legacy ERP integrations, manual reporting, data silos across warehouses.
Recent initiatives: digital transformation roadmap 2024–2026, piloting AI for demand forecasting.
Key contacts: Sarah Chen (CTO), Mike Torres (VP Operations).
Current tech stack: SAP ERP, Salesforce, Power BI (underutilised).""",
        "metadata": {"company": "Acme Corp", "industry": "logistics", "size": "mid-market"},
    },
    {
        "id": "beacon-1",
        "content": """Beacon Health is a regional NHS-adjacent private healthcare group.
3,200 staff, 12 hospitals across the Midlands. Revenue ~£280M.
Pain points: fragmented patient data, manual care pathway tracking, compliance reporting burden.
Strategic priorities: interoperability (HL7/FHIR), staff retention analytics, cost reduction.
Budget cycle: April–March. New CFO appointed Jan 2024 with mandate to cut OpEx by 15%.
Previous vendor: MedTech Solutions (contract ends June 2025 — renewal risk).""",
        "metadata": {"company": "Beacon Health", "industry": "healthcare", "size": "enterprise"},
    },
    {
        "id": "nova-1",
        "content": """Nova Fintech is a challenger bank targeting SME lending in the UK.
Founded 2019, Series B (£45M). 320 employees. FCA regulated.
Pain points: KYC/AML automation, credit decisioning latency, customer churn in year 2.
Tech stack: AWS, dbt, Snowflake, Looker. Engineering-led culture.
Competitor: Starling Business, Tide. Differentiation: embedded finance APIs.
CTO blog signals interest in LLM-powered credit underwriting (posted March 2024).""",
        "metadata": {"company": "Nova Fintech", "industry": "fintech", "size": "growth"},
    },
    {
        "id": "stellar-1",
        "content": """Stellar Retail is a UK fashion retailer with 180 stores and a growing e-commerce arm.
Revenue £620M. Facing margin pressure from returns (28% online return rate).
Pain points: personalisation at scale, inventory forecasting, returns fraud detection.
IT landscape: Shopify Plus, SAP, Adobe Analytics. 
2024 priority: reduce returns by 10%, improve customer lifetime value.
CMO recently changed (new hire from ASOS — digital-native background).""",
        "metadata": {"company": "Stellar Retail", "industry": "retail", "size": "enterprise"},
    },
    {
        "id": "greenfield-1",
        "content": """Greenfield Energy is a renewable energy developer (solar + wind).
£1.2B project pipeline. 180 staff. Series D.
Pain points: project portfolio analytics, ESG reporting for investors, asset performance monitoring.
Regulatory context: UK Net Zero commitments, TCFD reporting mandatory from 2025.
Tech: mainly Excel-based operations, moving to cloud. Budget allocated for data platform Q3 2024.
Key stakeholder: Head of Digital, James Okafor (ex-McKinsey, data-savvy).""",
        "metadata": {"company": "Greenfield Energy", "industry": "energy", "size": "growth"},
    },
    {
        "id": "product-overview",
        "content": """Our platform: AI-powered analytics and automation suite.
Core modules: Predictive Analytics, Natural Language Reporting, Data Integration Hub, Workflow Automation.
Key differentiators: no-code setup, 200+ native connectors, explainable AI outputs, UK data residency.
Typical ROI: 40% reduction in manual reporting time, 25% faster decision cycles.
Pricing: £2,500–£15,000/month depending on seats and modules.
Implementation: 6–12 weeks typical, dedicated CSM, SLA 99.9%.
Case studies: NHS Trust (saved £650K annually), Retailer (reduced returns by 12%).""",
        "metadata": {"type": "product", "category": "overview"},
    },
    {
        "id": "objection-handlers",
        "content": """Common objections and responses:
'We already have Power BI/Tableau': Our platform layers AI on top — augments, doesn't replace. 
'Too expensive': TCO analysis shows 3x ROI within 18 months for similar clients.
'Integration complexity': 200+ pre-built connectors; avg integration time 2 weeks.
'Data security concerns': ISO 27001 certified, UK data residency, SOC 2 Type II.
'We need IT sign-off': Offer IT sandbox trial, provide security questionnaire pre-filled.
'Not the right time': Ask about Q1 budget cycle, tie to a live pain point.""",
        "metadata": {"type": "product", "category": "objections"},
    },
    {
        "id": "competitive-intel",
        "content": """Competitive landscape:
Tableau/PowerBI: strong visualisation, weak AI/automation. We win on automation depth.
Palantir: strong AI but £multi-million, 12+ month impl. We win on speed and price.
DataRobot: ML-focused, less strong on reporting. We win on business-user accessibility.
Salesforce Einstein: CRM-native, limited to Salesforce data. We win on breadth.
Key messaging vs competition: faster time-to-value, no data science team needed, UK-based support.""",
        "metadata": {"type": "product", "category": "competitive"},
    },
]


def ingest(chroma_path: str = "./chroma_db"):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    client = chromadb.PersistentClient(path=chroma_path)
    embedding_fn = OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-3-small",
    )

    collection = client.get_or_create_collection(
        name="sales_knowledge",
        embedding_function=embedding_fn,
    )

    existing = collection.get()["ids"]
    new_docs = [d for d in SYNTHETIC_DOCS if d["id"] not in existing]

    if not new_docs:
        print("✓ ChromaDB already up to date — nothing to ingest.")
        return

    collection.add(
        ids=[d["id"] for d in new_docs],
        documents=[d["content"] for d in new_docs],
        metadatas=[d["metadata"] for d in new_docs],
    )
    print(f"✓ Ingested {len(new_docs)} documents into ChromaDB.")


if __name__ == "__main__":
    ingest()
