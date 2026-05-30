from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic


@dataclass
class LLMResponse:
    text: str
    tool_calls: list[dict[str, Any]]
    stop_reason: str
    input_tokens: int
    output_tokens: int
    raw: Any = None


_PRICING = {
    "claude-opus-4-7": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (0.80, 4.0),
}


def estimate_cost_usd(model: str, in_tokens: int, out_tokens: int) -> float:
    for key, (pin, pout) in _PRICING.items():
        if model.startswith(key):
            return (in_tokens / 1_000_000) * pin + (out_tokens / 1_000_000) * pout
    return (in_tokens / 1_000_000) * 3.0 + (out_tokens / 1_000_000) * 15.0


class LLMClient:
    """Anthropic client with mock-mode fallback. Same shape as Site Copilot
    and Case Pilot — interface is portable to Azure OpenAI or Microsoft
    Copilot Studio via a constructor swap."""

    def __init__(self, *, api_key: str | None, model: str, use_mock: bool = False):
        self.model = model
        self.use_mock = use_mock or os.environ.get("ATO_COPILOT_USE_MOCK_LLM") == "1"
        self._client: Anthropic | None = None
        if not self.use_mock and not api_key:
            print(
                "[ato-copilot] WARNING: ANTHROPIC_API_KEY not set; falling back to mock mode.",
                flush=True,
            )
            self.use_mock = True
        if not self.use_mock:
            self._client = Anthropic(api_key=api_key)

    def complete(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1500,
        temperature: float = 0.2,
    ) -> LLMResponse:
        if self.use_mock:
            return self._mock_complete(system=system, messages=messages, tools=tools)
        assert self._client is not None
        kwargs: dict[str, Any] = {
            "model": self.model,
            "system": system,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
        resp = self._client.messages.create(**kwargs)
        text_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        for block in resp.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append({"id": block.id, "name": block.name, "input": block.input})
        return LLMResponse(
            text="\n".join(text_parts).strip(),
            tool_calls=tool_calls,
            stop_reason=resp.stop_reason or "",
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            raw=resp,
        )

    def _mock_complete(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
    ) -> LLMResponse:
        already_used_tool = any(
            isinstance(msg.get("content"), list)
            and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in msg["content"])
            for msg in messages
        )
        if tools and not already_used_tool:
            return LLMResponse(
                text="",
                tool_calls=[{
                    "id": "toolu_mock",
                    "name": "retrieve",
                    "input": {"query": "approved technology list cloud database", "k": 6},
                }],
                stop_reason="tool_use",
                input_tokens=420,
                output_tokens=18,
            )

        draft = {
            "request_summary": (
                "Engineering team requests onboarding of PostgreSQL 16 on AWS RDS for a new "
                "customer-reporting application. (Mock response.)"
            ),
            "atl_status": {
                "status": "approved",
                "approved_entry": "PostgreSQL 14 on AWS RDS (managed)",
                "note": "Major-version uplift to 16 inherits ATL approval per ATL-POL-04; no fresh approval required.",
                "source": "atl:postgresql_rds",
            },
            "control_mapping": [
                {"control": "AC-2 Account Management", "applicability": "high",
                 "source": "controls:nist_800_53_ac"},
                {"control": "AU-2 Audit Events", "applicability": "high",
                 "source": "controls:nist_800_53_au"},
                {"control": "SC-13 Cryptographic Protection",
                 "applicability": "high (at-rest + in-transit encryption required)",
                 "source": "controls:nist_800_53_sc"},
            ],
            "architecture_review": {
                "pattern": "Approved 3-tier app, single-region RDS with cross-region read replica",
                "fits_reference_architecture": True,
                "issues": [],
            },
            "risk_classification": {
                "band": "low",
                "rationale": "Approved tech, customer-reporting (no client funds movement), single-region with documented failover.",
            },
            "recommended_decision": "ATO-APPROVED with annual review",
            "open_items": [
                "Confirm CMK rotation policy with InfoSec",
                "Attach DR runbook to the ATO package",
            ],
            "needs_arb_review": False,
            "rationale": "Mock rationale.",
        }
        return LLMResponse(
            text=json.dumps(draft, indent=2),
            tool_calls=[],
            stop_reason="end_turn",
            input_tokens=1200,
            output_tokens=260,
        )
