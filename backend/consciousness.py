from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field

from .storage import Storage


class ConsciousnessState(BaseModel):
    directives: List[str] = Field(default_factory=list)
    learned_preferences: Dict[str, str] = Field(default_factory=dict)
    history_summary: str = ""


class PerceptionLoop:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def read_state(self) -> ConsciousnessState:
        raw = self.storage.load_state()
        if raw:
            return ConsciousnessState.model_validate(raw)
        state = ConsciousnessState()
        self.write_state(state)
        return state

    def write_state(self, state: ConsciousnessState) -> None:
        self.storage.save_state(state.model_dump())

    def generate_system_prompt(self, state: ConsciousnessState) -> str:
        directives = "\n".join(f"- {d}" for d in state.directives) or "- none"
        prefs = "\n".join(f"- {k}: {v}" for k, v in state.learned_preferences.items()) or "- none"
        return (
            "You are an adaptive assistant.\n"
            f"Directives:\n{directives}\n"
            f"Learned preferences:\n{prefs}\n"
            f"History summary: {state.history_summary or 'none'}"
        )

    def process_input(self, user_input: str) -> ConsciousnessState:
        state = self.read_state()
        if "hate long summaries" in user_input.lower():
            state.learned_preferences["summary_length"] = "short"
        if user_input:
            state.history_summary = (state.history_summary + " | " + user_input).strip(" |")[-500:]
        self.write_state(state)
        return state

    def apply_feedback(self, feedback: str) -> ConsciousnessState:
        state = self.read_state()
        state.learned_preferences["last_feedback"] = feedback
        if "wasn't spam" in feedback.lower() or "was not spam" in feedback.lower():
            state.learned_preferences["spam_sensitivity"] = "lower"
        self.write_state(state)
        return state
