# Security and responsible use

This repository is an experimental sales-meeting preparation tool, not a production-grade or independently security-audited service.

- Never commit .env files, API keys or user/customer information.
- User-provided company names and meeting context are sent to external AI API providers. When web research is enabled, search queries are sent to Tavily. ChromaDB stores the seeded demonstration knowledge base on disk until manually deleted.
- Do not use real confidential sales or customer data without a proper assessment of consent, contractual obligations, retention policies, security and UK GDPR requirements.
- All seeded company profiles, ROI numbers, product claims and case studies are **fictional demonstration content**. They must not be represented as independently verified commercial facts.
- LLM-generated commercial or factual statements require verification against original sources before use.
- The session counter is not an effective production-grade API rate limit.
- Do not claim GDPR compliance or that data is never retained; third-party providers may process inputs according to their terms and policies.

Please report suspected vulnerabilities privately to the maintainer rather than publishing credentials or personal information in an issue.
