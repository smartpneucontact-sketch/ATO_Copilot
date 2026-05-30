from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ato_copilot.rag.retriever import Retriever


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    fn: Callable[..., Any]

    def to_anthropic(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "input_schema": self.input_schema}


class ToolRegistry:
    def __init__(self, tools: list[ToolSpec] | None = None):
        self._tools: dict[str, ToolSpec] = {}
        for t in tools or []:
            self.register(t)

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def to_anthropic(self) -> list[dict[str, Any]]:
        return [t.to_anthropic() for t in self._tools.values()]

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        if name not in self._tools:
            return {"error": f"unknown tool: {name}"}
        try:
            return self._tools[name].fn(**arguments)
        except TypeError as e:
            return {"error": f"bad arguments for {name}: {e}"}
        except Exception as e:
            return {"error": f"{name} raised: {type(e).__name__}: {e}"}


def _make_retrieve_tool(retriever: Retriever) -> ToolSpec:
    def retrieve(query: str, k: int = 6, source_type: str | None = None) -> dict[str, Any]:
        filters = {"source_type": source_type} if source_type else None
        results = retriever.search(query, k=k, filters=filters)
        return {
            "results": [
                {
                    "chunk_id": r.chunk.chunk_id,
                    "source_type": r.chunk.source_type,
                    "source_id": r.chunk.source_id,
                    "section": r.chunk.section,
                    "score": round(r.score, 3),
                    "text": r.chunk.text,
                }
                for r in results
            ],
            "count": len(results),
        }

    return ToolSpec(
        name="retrieve",
        description=(
            "Search the governance corpus (Approved Technology List, security control families, "
            "reference architecture patterns, prior ATO decisions). Always call BEFORE drafting "
            "an ATO recommendation. Returns chunks with their source so every claim can be cited."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 6},
                "source_type": {
                    "type": "string",
                    "enum": ["atl", "control", "architecture", "prior_ato"],
                    "description": "Optional filter to one source type.",
                },
            },
            "required": ["query"],
        },
        fn=retrieve,
    )


def _classify_risk() -> ToolSpec:
    def classify_risk(
        handles_client_funds: bool = False,
        handles_pii_or_pci: bool = False,
        is_public_facing: bool = False,
        is_new_to_atl: bool = False,
        critical_business_function: bool = False,
    ) -> dict[str, Any]:
        score = 0
        if handles_client_funds:
            score += 3
        if handles_pii_or_pci:
            score += 2
        if is_public_facing:
            score += 2
        if is_new_to_atl:
            score += 1
        if critical_business_function:
            score += 2
        if score >= 5:
            band = "high"
        elif score >= 2:
            band = "medium"
        else:
            band = "low"
        return {
            "risk_band": band,
            "score": score,
            "rationale": (
                f"client_funds={handles_client_funds}, pii_pci={handles_pii_or_pci}, "
                f"public={is_public_facing}, new_to_atl={is_new_to_atl}, critical={critical_business_function}"
            ),
        }

    return ToolSpec(
        name="classify_risk",
        description=(
            "Classify ATO request risk based on data sensitivity, exposure, ATL novelty, and "
            "business criticality. High-risk requests should be flagged for ARB / Senior Architect review."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "handles_client_funds": {"type": "boolean", "default": False},
                "handles_pii_or_pci": {"type": "boolean", "default": False},
                "is_public_facing": {"type": "boolean", "default": False},
                "is_new_to_atl": {"type": "boolean", "default": False,
                                  "description": "True if the technology is not already on the ATL."},
                "critical_business_function": {"type": "boolean", "default": False},
            },
            "required": [],
        },
        fn=classify_risk,
    )


def _estimate_cycle_time() -> ToolSpec:
    def estimate_cycle_time(
        risk_band: str = "low",
        is_new_to_atl: bool = False,
        needs_arb_review: bool = False,
    ) -> dict[str, Any]:
        # Rough days-to-decision estimates aligned with typical enterprise governance windows.
        base = {"low": 2, "medium": 5, "high": 12}.get(risk_band, 7)
        if is_new_to_atl:
            base += 7
        if needs_arb_review:
            base += 5
        return {
            "estimated_days_to_decision": base,
            "breakdown": {
                "base_for_risk": {"low": 2, "medium": 5, "high": 12}.get(risk_band, 7),
                "atl_new_entry_overhead": 7 if is_new_to_atl else 0,
                "arb_review_overhead": 5 if needs_arb_review else 0,
            },
        }

    return ToolSpec(
        name="estimate_cycle_time",
        description=(
            "Estimate calendar days to ATO decision based on risk band, ATL novelty, and ARB-review "
            "requirement. Useful for setting requestor expectations."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "risk_band": {"type": "string", "enum": ["low", "medium", "high"], "default": "low"},
                "is_new_to_atl": {"type": "boolean", "default": False},
                "needs_arb_review": {"type": "boolean", "default": False},
            },
            "required": [],
        },
        fn=estimate_cycle_time,
    )


def build_ato_tools(retriever: Retriever) -> ToolRegistry:
    return ToolRegistry(tools=[
        _make_retrieve_tool(retriever),
        _classify_risk(),
        _estimate_cycle_time(),
    ])
