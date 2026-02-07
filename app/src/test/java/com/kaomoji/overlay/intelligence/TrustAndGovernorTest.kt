package com.kaomoji.overlay.intelligence

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class TrustAndGovernorTest {

    @Test
    fun `trust score gates tier 3`() {
        val store = InMemoryPersonaStore(seedPersonaCore(true, true, true))
        val observations = ObservationStore()
        val engine = TrustEngine(store, observations)

        engine.increaseTrust(45f, "User correction accepted")

        assertTrue(engine.canUseIntegratedTier3())
        assertTrue(engine.currentPersona().milestones.contains("MONTH_ZERO_BREACH"))
    }

    @Test
    fun `stress forces tier 1 with notice`() {
        val store = InMemoryPersonaStore(seedPersonaCore(true, true, true).copy(trustScore = 90f))
        val observations = ObservationStore()
        val engine = TrustEngine(store, observations)
        val telemetry = object : TelemetryProvider {
            override fun currentSnapshot(): DeviceSnapshot {
                return DeviceSnapshot(
                    batteryPercent = 15,
                    charging = false,
                    thermalState = ThermalState.HIGH,
                    inferredStressHigh = true
                )
            }
        }

        val governor = ThermalBatteryGovernor(telemetry, engine, observations)
        val decision = governor.decideTier()

        assertEquals(IntelligenceTier.TIER_1, decision.tier)
        assertTrue(decision.notice?.contains("Slowing down") == true)
    }

    @Test
    fun `pruner collapses experiences into lessons`() {
        val pruner = ConsciousnessPruner(ObservationStore())
        val state = ConsciousnessState(experienceLog = List(60) { "entry-$it" })

        val pruned = pruner.prune(state)

        assertTrue(pruned.learnedLessons.isNotEmpty())
        assertTrue(pruned.experienceLog.size <= 10)
    }
}

private class InMemoryPersonaStore(
    private var persona: PersonaCore
) : PersonaStore {
    override fun loadPersona(): PersonaCore = persona

    override fun savePersona(personaCore: PersonaCore) {
        persona = personaCore
    }
}
