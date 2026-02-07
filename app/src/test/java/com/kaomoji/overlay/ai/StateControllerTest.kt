package com.kaomoji.overlay.ai

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class StateControllerTest {
    @Test
    fun `trust gate blocks tier 3 until milestone trust reached`() {
        val monitor = DeviceMonitor().apply {
            setSimulatedStress(TelemetrySnapshot(95, isCharging = true, thermalState = ThermalState.COOL, inferenceLatencyMs = 120))
        }
        val controller = StateController(monitor)
        val persona = PersonaCore.seeded(direct = true, technical = true, concise = true)

        val before = controller.chooseTier(persona)
        assertEquals(IntelligenceTier.TIER_2, before.tier)

        persona.increaseTrust(40f, "High quality feedback cycle")
        val after = controller.chooseTier(persona)
        assertEquals(IntelligenceTier.TIER_3, after.tier)
    }

    @Test
    fun `thermal governor forces tier 1 under stress`() {
        val monitor = DeviceMonitor().apply {
            setSimulatedStress(TelemetrySnapshot(10, isCharging = false, thermalState = ThermalState.HIGH, inferenceLatencyMs = 2600))
        }
        val controller = StateController(monitor)
        val persona = PersonaCore.seeded(direct = true, technical = true, concise = true).apply {
            increaseTrust(80f, "Trusted")
        }

        val decision = controller.chooseTier(persona)
        assertEquals(IntelligenceTier.TIER_1, decision.tier)
        assertTrue(decision.notification?.contains("Slowing down") == true)
    }

    @Test
    fun `experience log compacts to learned lessons`() {
        val persona = PersonaCore.seeded(direct = true, technical = false, concise = true)

        repeat(51) { persona.addExperience("verbosity:event-$it") }

        assertEquals(0, persona.experienceLog.size)
        assertTrue(persona.learnedLessons.isNotEmpty())
        assertTrue(persona.learnedLessons.size <= 5)
    }
}
