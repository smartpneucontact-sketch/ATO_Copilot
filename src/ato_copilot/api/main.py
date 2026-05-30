from __future__ import annotations

import json
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ato_copilot.api.deps import AppState, build_app_state
from ato_copilot.notifications import diagnostic_status, maybe_notify_visitor, send_test_email

_STATIC_DIR = Path(__file__).resolve().parent.parent / "ui" / "static"
_SAMPLES_DIR = Path("data/samples")


class RequestPayload(BaseModel):
    request_id: str
    submitted_by: str | None = None
    business_unit: str | None = None
    date: str | None = None
    description: str = Field(..., description="Free-text NTAP / ATO request")


class AgentResponse(BaseModel):
    run_id: str
    parsed: dict[str, Any] | None
    final_text: str
    steps: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    tool_invocations: list[dict[str, Any]]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.app_state = build_app_state()
    yield


app = FastAPI(
    title="ATO Copilot",
    version="0.1.0",
    description=(
        "AI-assisted ATO/NTAP triage with Approved Technology List check, control mapping, "
        "and risk classification. Portfolio demo for State Street."
    ),
    lifespan=lifespan,
)


@app.middleware("http")
async def site_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.method == "GET" and request.url.path == "/":
        try:
            await maybe_notify_visitor(request, request.url.path)
        except Exception as e:
            print(f"[ato-copilot] visitor notify error: {e}", flush=True)
    if request.url.path.startswith("/static/") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


def _state(request: Request) -> AppState:
    return request.app.state.app_state


@app.get("/healthz")
def healthz(request: Request) -> dict[str, Any]:
    s = _state(request)
    return {
        "status": "ok",
        "model": s.settings.model,
        "corpus_chunks": s.retriever.size(),
        "use_mock_llm": s.ato_agent.llm.use_mock,
    }


@app.get("/api", include_in_schema=False)
def api_info(request: Request) -> dict[str, Any]:
    s = _state(request)
    return {
        "service": "ATO Copilot",
        "version": "0.1.0",
        "description": "AI-assisted ATO/NTAP triage for enterprise governance workflows.",
        "endpoints": {
            "GET /": "HTML UI",
            "POST /agents/ato/triage": "Triage an NTAP/ATO request",
            "GET /healthz": "Liveness + model status",
            "GET /api/samples/requests": "Sample NTAP/ATO requests",
        },
        "mode": "MOCK" if s.ato_agent.llm.use_mock else f"LIVE ({s.settings.model})",
    }


@app.get("/api/samples/requests", include_in_schema=False)
def sample_requests() -> list[dict[str, Any]]:
    p = _SAMPLES_DIR / "request_inbox.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


@app.get("/api/notify/diag", include_in_schema=False)
def notify_diag() -> dict[str, Any]:
    return diagnostic_status()


@app.post("/api/notify/test", include_in_schema=False)
async def notify_test() -> dict[str, Any]:
    return await send_test_email()


@app.post("/agents/ato/triage", response_model=AgentResponse)
def ato_triage(payload: RequestPayload, request: Request) -> AgentResponse:
    s = _state(request)
    try:
        result = s.ato_agent.run_request(payload.model_dump())
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[ato-copilot] ato triage failed: {type(e).__name__}: {e}\n{tb}", flush=True)
        raise HTTPException(
            status_code=500,
            detail={"error": type(e).__name__, "message": str(e), "agent": "ato_triage"},
        )
    return AgentResponse(
        run_id=result.run_id,
        parsed=result.parsed,
        final_text=result.final_text,
        steps=result.steps,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cost_usd=round(result.cost_usd, 6),
        tool_invocations=result.tool_invocations,
    )


if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(_STATIC_DIR / "index.html")
