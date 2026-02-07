package com.kaomoji.overlay.ai

import android.util.Log

data class RoutingDecision(
    val tier: IntelligenceTier,
    val reason: String,
    val notification: String?
)

class StateController(
    private val deviceMonitor: DeviceMonitor
) {
    fun chooseTier(persona: PersonaCore, latencyMs: Long = 0L): RoutingDecision {
        val telemetry = deviceMonitor.currentSnapshot(latencyMs)
        val resourceTier = deviceMonitor.resolveResourceTier(telemetry)
        val trustTier = when {
            persona.supportsIntegratedTier() -> IntelligenceTier.TIER_3
            persona.trustScore >= 35f -> IntelligenceTier.TIER_2
            else -> IntelligenceTier.TIER_1
        }
        val chosen = minOf(resourceTier, trustTier)
        val reason = "resource=$resourceTier trust=$trustTier trustScore=${persona.trustScore}"
        val notification = deviceMonitor.slowdownMessage(telemetry)
        Log.i("StateController", "Model switch decision: $reason -> $chosen")
        return RoutingDecision(chosen, reason, notification)
    }
}
