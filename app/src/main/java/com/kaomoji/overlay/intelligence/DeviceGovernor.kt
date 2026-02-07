package com.kaomoji.overlay.intelligence

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import android.util.Log

enum class ThermalState {
    COOL,
    NORMAL,
    HIGH
}

data class DeviceSnapshot(
    val batteryPercent: Int,
    val charging: Boolean,
    val thermalState: ThermalState,
    val inferredStressHigh: Boolean
)

interface TelemetryProvider {
    fun currentSnapshot(): DeviceSnapshot
}

class DeviceMonitor(private val context: Context) : TelemetryProvider {
    private var latencySamples = ArrayDeque<Long>()

    fun observeInferenceLatency(durationMs: Long) {
        latencySamples.addLast(durationMs)
        if (latencySamples.size > 10) {
            latencySamples.removeFirst()
        }
    }

    override fun currentSnapshot(): DeviceSnapshot {
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val level = batteryIntent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryIntent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        val status = batteryIntent?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: -1
        val charging = status == BatteryManager.BATTERY_STATUS_CHARGING || status == BatteryManager.BATTERY_STATUS_FULL

        val batteryPercent = if (level >= 0 && scale > 0) ((level * 100f) / scale).toInt() else 50

        val tempRaw = batteryIntent?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1) ?: -1
        val tempC = tempRaw / 10f
        val thermalState = when {
            tempC >= 43 -> ThermalState.HIGH
            tempC in 0f..34f -> ThermalState.COOL
            else -> ThermalState.NORMAL
        }

        val avgLatency = latencySamples.average().takeIf { !it.isNaN() } ?: 0.0
        val inferredStressHigh = avgLatency > 2000

        return DeviceSnapshot(
            batteryPercent = batteryPercent,
            charging = charging,
            thermalState = thermalState,
            inferredStressHigh = inferredStressHigh
        )
    }
}

data class GovernorDecision(
    val tier: IntelligenceTier,
    val notice: String?
)

class ThermalBatteryGovernor(
    private val telemetryProvider: TelemetryProvider,
    private val trustEngine: TrustEngine,
    private val observationStore: ObservationStore
) {
    fun decideTier(): GovernorDecision {
        val snapshot = telemetryProvider.currentSnapshot()

        if (snapshot.batteryPercent < 20 || snapshot.thermalState == ThermalState.HIGH || snapshot.inferredStressHigh) {
            Log.i("ThermalBatteryGovernor", "Switching to Tier 1 due to stress: $snapshot")
            observationStore.add(
                observation = "Device stress detected (battery=${snapshot.batteryPercent}, thermal=${snapshot.thermalState}).",
                adjustment = "Downshifting to Tier 1 heuristics."
            )
            return GovernorDecision(
                tier = IntelligenceTier.TIER_1,
                notice = "Slowing down to save your battery/cool your device."
            )
        }

        if (snapshot.charging && snapshot.thermalState == ThermalState.COOL && trustEngine.canUseIntegratedTier3()) {
            Log.i("ThermalBatteryGovernor", "Switching to Tier 3: $snapshot")
            return GovernorDecision(tier = IntelligenceTier.TIER_3, notice = null)
        }

        Log.i("ThermalBatteryGovernor", "Using Tier 2 fallback: $snapshot")
        return GovernorDecision(tier = IntelligenceTier.TIER_2, notice = null)
    }
}
