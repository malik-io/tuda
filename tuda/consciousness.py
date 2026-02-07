from __future__ import annotations

import time
from typing import Optional, Protocol

from .models.state import ThermalState, TrustLevel
from .resource_governor import ResourceGovernor
from .trust_engine import TrustEngine


class StateStore(Protocol):
    def persist(self, trust: TrustLevel, thermal: ThermalState, mode: str, ts: float) -> None:
        ...


class ConsciousnessLayer:
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        self.trust_engine = TrustEngine()
        self.resource_governor = ResourceGovernor()

    def perception_loop(self, context: str, user_feedback: Optional[str] = None) -> str:
        if user_feedback:
            feedback = user_feedback.lower()
            if "correct" in feedback:
                self.trust_engine.record_user_correction_adapted()
            elif "confirm" in feedback:
                self.trust_engine.record_user_confirmed_analysis()
            elif "false positive" in feedback:
                self.trust_engine.record_false_positive()
            elif "overreach" in feedback or "rejected" in feedback:
                self.trust_engine.record_overreach_rejected()
            elif "wrong" in feedback:
                self.trust_engine.record_false_positive()

        trust = self.trust_engine.resolve_trust_level()
        thermal = self.resource_governor.get_thermal_state()
        mode = self.resource_governor.select_inference_mode(thermal)

        system_prompt = (
            f"Trust Level: {trust.name}\\n"
            f"Thermal State: {thermal.name}\\n"
            f"Inference Mode: {mode}\\n"
            f"Context: {context}"
        )

        self.state_store.persist(trust, thermal, mode, time.time())
        return system_prompt
