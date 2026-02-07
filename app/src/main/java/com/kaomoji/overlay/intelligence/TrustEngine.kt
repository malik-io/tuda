package com.kaomoji.overlay.intelligence

class TrustEngine(
    private val repository: PersonaStore,
    private val observationStore: ObservationStore
) {
    private val tier3Threshold = 70f

    fun currentPersona(): PersonaCore = repository.loadPersona()

    fun increaseTrust(amount: Float, reason: String): PersonaCore {
        return updateTrust(amount.coerceAtLeast(0f), reason)
    }

    fun decayTrust(amount: Float, reason: String): PersonaCore {
        return updateTrust(-amount.coerceAtLeast(0f), reason)
    }

    fun canUseIntegratedTier3(): Boolean = currentPersona().trustScore >= tier3Threshold

    private fun updateTrust(delta: Float, reason: String): PersonaCore {
        val current = currentPersona()
        val nextTrust = (current.trustScore + delta).coerceIn(0f, 100f)
        val history = (current.trustHistory + TrustEvent(reason = reason, delta = delta)).takeLast(200)
        val milestones = unlockMilestones(current.milestones, nextTrust, reason)
        val updated = current.copy(trustScore = nextTrust, milestones = milestones, trustHistory = history)
        repository.savePersona(updated)

        observationStore.add(
            observation = "Trust adjusted by $delta for reason: $reason.",
            adjustment = "Current trust score is ${"%.2f".format(nextTrust)}."
        )

        return updated
    }

    private fun unlockMilestones(existing: List<String>, trust: Float, reason: String): List<String> {
        val mutable = existing.toMutableSet()
        if (reason.contains("correction", ignoreCase = true)) {
            mutable.add("FIRST_CORRECTION_ADAPTED")
        }
        if (trust >= tier3Threshold) {
            mutable.add("MONTH_ZERO_BREACH")
        }
        return mutable.toList().sorted()
    }
}
