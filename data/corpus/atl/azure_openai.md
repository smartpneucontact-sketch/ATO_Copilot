# ATL Entry — Azure OpenAI Service

**Synthetic demo document.**

| Field | Value |
| --- | --- |
| **Status** | CONDITIONALLY APPROVED |
| **ATL ID** | ATL-2025-AI-0003 |
| **Approved models** | gpt-4o, gpt-4o-mini, text-embedding-3-large |
| **Approved regions** | East US 2, North Central US |
| **Deployment model** | Provisioned Throughput Units (PTU) or Standard (S1) deployments via private endpoint |
| **Data classifications permitted** | Internal, Confidential — subject to data residency conditions below |
| **Owner** | AI Platform Team |

## Conditions

1. **Private Endpoint required** — no public network access. All traffic via VNet integration.
2. **No client funds data, no PII without DLP gate** — must traverse the enterprise DLP scanner before submission to the model endpoint.
3. **Content filtering enabled** — Azure Content Filter at default sensitivity minimum.
4. **Logging** — All prompts and completions logged to Azure Monitor + enterprise SIEM. Retention 90 days.
5. **Prompt injection mitigation** — Application must implement input sanitization per AI-SEC-STD-02.
6. **No fine-tuning on production data without separate ATO.**

## Not on ATL

- **OpenAI direct API** (api.openai.com): NOT approved — no enterprise data processing agreement on file.
- **Anthropic Claude direct API**: NOT approved as of this revision. AWS Bedrock Claude is approved separately (see ATL-2025-AI-0008).
- **Self-hosted LLMs on EC2 GPU**: NOT approved without an Architecture Review Board exception.
