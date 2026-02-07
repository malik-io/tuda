from enum import IntEnum
from typing import Dict

from pydantic import BaseModel, Field


class TrustLevel(IntEnum):
    SEED = 0
    PEER = 1
    WARDEN = 2
    INTEGRATED = 3


class ThermalState(IntEnum):
    COOL = 0
    WARM = 1
    HOT = 2
    CRITICAL = 3


class Capability(BaseModel):
    name: str
    enabled: bool
    requires_trust: TrustLevel
    requires_explicit_opt_in: bool = True


class SystemState(BaseModel):
    trust_level: TrustLevel
    thermal_state: ThermalState
    capabilities: Dict[str, Capability] = Field(default_factory=dict)
    inference_mode: str = "nf4"
    last_transition_ts: float
