# ATO Copilot

AI-assisted **NTAP / ATO triage** for enterprise governance workflows. Portfolio demo for [State Street](https://www.statestreet.com) — *ATO AI Process and Automation Engineer, Assistant Vice President* role (Boston).

> A delivery team's free-text NTAP request goes in. A structured ATO package comes out — ATL status check, NIST 800-53 control mapping, reference-architecture review, risk classification, cycle-time estimate, and a recommended decision (ATO-APPROVED / CONDITIONS / DENIED / ARB-ROUTING). Every claim cited.

## Demo (60 seconds)

```bash
make install
make ingest           # smoke-test the corpus
export ANTHROPIC_API_KEY=sk-ant-...
make serve            # http://localhost:8000
```

## How it maps to State Street's stack

| This demo | State Street production target |
| --- | --- |
| Anthropic Claude Sonnet 4.6 | Microsoft **Copilot Studio** + **Azure OpenAI** (gpt-4o) |
| BM25 over markdown corpus | **Azure AI Search** / **SharePoint Search** on governance KB |
| FastAPI + Pydantic backend | **ServiceNow** workflow + **Azure Function** via **Power Automate** |
| Single-page UI | **ServiceNow** service portal / **Power Apps** canvas |
| JSONL traces | **Splunk** + **Azure Monitor** |
| Synthetic ATL corpus | **Flexera** ITAM data + SharePoint ATL document library |
| Visitor-notify webhook | Power Automate flow → Outlook / Teams alert |

## What it does

**One agent**: `ATORequestAgent`.

**Tools**:
- `retrieve` — search the governance corpus (ATL, controls, architecture, prior ATOs)
- `classify_risk` — bands a request on data sensitivity + exposure + ATL novelty + criticality
- `estimate_cycle_time` — calendar-days SLA based on risk band, ATL novelty, ARB requirement

**Output**: structured ATO package with ATL status + control mapping + architecture review + risk band + cycle-time estimate + recommended decision + open items + reviewer rationale.

## Corpus

Synthetic, MasterFormat-shaped governance documents:
- `data/corpus/atl/` — Approved Technology List entries (PostgreSQL/RDS, Kafka/MSK, Azure OpenAI)
- `data/corpus/controls/` — NIST 800-53 control family summaries (AC, AU, SC, SI)
- `data/corpus/architecture/` — reference patterns + anti-patterns
- `data/corpus/prior_atos/` — prior ATO decision precedents

## Visitor notify

Same pattern as Site Copilot + Case Pilot — Resend HTTPS API, dedup + bot filter, ipapi.co geo lookup. Set in Railway:
- `RESEND_API_KEY=re_...`
- `NOTIFY_TO_EMAIL=arsen.khanguieldyan@gmail.com`

## Honest limits

- Synthetic corpus, not real ATL or NIST mappings.
- No ServiceNow / Power Platform wiring — the FastAPI prototype demonstrates the pattern only.
- No human-in-the-loop UI for InfoSec / ARB reviewer to edit and route the package.
- No labeled golden set for the eval suite yet — production needs 100+ historical ATOs to score the recommendation field.

---

Author: **Arsen Khanguieldyan** · arsen.khanguieldyan@gmail.com
