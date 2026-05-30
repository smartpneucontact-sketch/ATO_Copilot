# Enterprise Reference Architecture Patterns

**Synthetic demo document.**

## Pattern A — 3-Tier Web Application (Internal)

- Presentation: load balancer (ALB) → ECS Fargate or AKS pods (no direct EC2 unless ARB-approved).
- Application: stateless service container behind internal ALB.
- Data: RDS PostgreSQL (see ATL-2024-DB-0017) or Aurora.
- Identity: enterprise IdP federation; no local user store.
- Logging: structured JSON → CloudWatch → Splunk forwarder.

**Approved for**: internal-only business applications, Internal + Confidential data.

## Pattern B — Public-Facing Customer Portal

- Includes everything in Pattern A, plus:
- WAF in front of public ALB.
- DDoS protection (AWS Shield Advanced).
- ARB review required.
- Penetration test required before go-live and annually.

**Approved for**: client-facing portals with strong auth (MFA).

## Pattern C — Event-Driven Microservices

- Kafka on MSK (ATL-2024-MSG-0006) for inter-service events.
- Each service owns its data store; no shared databases.
- Schema Registry mandatory.

**Approved for**: high-throughput internal pipelines, Internal + Confidential data.

## Pattern D — AI / LLM-Integrated Application

- LLM access via Azure OpenAI (ATL-2025-AI-0003) or Bedrock Claude (ATL-2025-AI-0008) — never direct public APIs.
- Mandatory DLP gate on inbound text to model.
- Prompt + completion logs to SIEM.
- Vector store: Azure AI Search (preferred) or OpenSearch.
- ARB review required for any first-party customer use case.

## Anti-Patterns (DO NOT USE)

- Self-managed Kubernetes on EC2 without strong justification.
- Local user/password stores.
- Public-facing services without WAF.
- Stateful services in containers without persistent storage strategy.
- Direct OpenAI API or any non-ATL LLM endpoint.
- Self-hosted LLMs on GPU EC2 without ARB exception.
