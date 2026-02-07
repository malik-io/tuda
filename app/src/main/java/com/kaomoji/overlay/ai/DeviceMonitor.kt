package com.kaomoji.overlay.ai

enum class ThermalState {
    COOL,
    MODERATE,
    HIGH
}

data class TelemetrySnapshot(
    val batteryPercent: Int,
    val isCharging: Boolean,
    val thermalState: ThermalState,
    val inferenceLatencyMs: Long
)

class DeviceMonitor {
    private var simulatedSnapshot: TelemetrySnapshot? = null

    fun setSimulatedStress(snapshot: TelemetrySnapshot?) {
        simulatedSnapshot = snapshot
    }

    fun currentSnapshot(defaultLatencyMs: Long = 0L): TelemetrySnapshot {
        return simulatedSnapshot ?: TelemetrySnapshot(
            batteryPercent = 100,
            isCharging = false,
            thermalState = ThermalState.COOL,
            inferenceLatencyMs = defaultLatencyMs
        )
    }

    fun resolveResourceTier(snapshot: TelemetrySnapshot): IntelligenceTier {
        if (snapshot.batteryPercent < 20 || snapshot.thermalState == ThermalState.HIGH) {
            return IntelligenceTier.TIER_1
        }
        if (snapshot.isCharging && snapshot.thermalState == ThermalState.COOL) {
            return IntelligenceTier.TIER_3
        }
        return if (snapshot.inferenceLatencyMs > 1_500) IntelligenceTier.TIER_1 else IntelligenceTier.TIER_2
    }

    fun slowdownMessage(snapshot: TelemetrySnapshot): String? {
        return if (snapshot.batteryPercent < 20 || snapshot.thermalState == ThermalState.HIGH) {
            "Slowing down to save your battery/cool your device."
        } else {
            null
        }
    }
}
