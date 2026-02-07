from __future__ import annotations

from fastapi import FastAPI, Request
from pydantic import BaseModel

from .check_hardware import compute_profile
from .consciousness import PerceptionLoop
from .plugins import NERDetector, PluginContext, SpamDetector
from .storage import Storage

app = FastAPI(title="Consciousness API")

storage = Storage()
loop = PerceptionLoop(storage)
hardware_profile = compute_profile()
RUNTIME_DEVICE = "cuda" if hardware_profile["runtime_mode"] == "gpu" else "cpu"


class AnalyzeRequest(BaseModel):
    text: str


class FeedbackRequest(BaseModel):
    feedback: str


@app.middleware("http")
async def inject_consciousness(request: Request, call_next):
    request.state.consciousness = loop.read_state().model_dump()
    return await call_next(request)


@app.get("/health")
def health():
    return {"runtime_mode": hardware_profile["runtime_mode"], "warning": hardware_profile.get("warning")}


@app.get("/state")
def get_state():
    state = loop.read_state()
    return {
        "state": state.model_dump(),
        "system_prompt": loop.generate_system_prompt(state),
    }


@app.post("/analyze/spam")
def analyze_spam(payload: AnalyzeRequest, request: Request):
    context = PluginContext(device=RUNTIME_DEVICE, consciousness_state=request.state.consciousness)
    detector = SpamDetector(context)
    return detector.run(payload.text)


@app.post("/analyze/ner")
def analyze_ner(payload: AnalyzeRequest, request: Request):
    context = PluginContext(device=RUNTIME_DEVICE, consciousness_state=request.state.consciousness)
    detector = NERDetector(context)
    return detector.run(payload.text)


@app.post("/feedback")
def feedback(payload: FeedbackRequest):
    state = loop.apply_feedback(payload.feedback)
    return {
        "message": "feedback applied",
        "state": state.model_dump(),
        "system_prompt": loop.generate_system_prompt(state),
    }
