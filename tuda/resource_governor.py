from __future__ import annotations

import psutil

from .models.state import ThermalState


class ResourceGovernor:
    """
    Controls inference strategy based on thermal + battery conditions.
    """

    def get_thermal_state(self) -> ThermalState:
        temps = psutil.sensors_temperatures()
        if not temps:
            return ThermalState.COOL

        max_temp = max(t.current for sensor in temps.values() for t in sensor)

        if max_temp < 60:
            return ThermalState.COOL
        if max_temp < 75:
            return ThermalState.WARM
        if max_temp < 85:
            return ThermalState.HOT
        return ThermalState.CRITICAL

    def select_inference_mode(self, thermal: ThermalState) -> str:
        if thermal == ThermalState.COOL:
            return "nf4"
        if thermal == ThermalState.WARM:
            return "int8"
        if thermal == ThermalState.HOT:
            return "heuristic"
        return "sleep"
