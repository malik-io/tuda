package com.kaomoji.overlay.ai

import kotlin.math.pow

data class PersonaCore(
    val toneProfile: MutableMap<String, Float>,
    var trustScore: Float,
    val milestones: MutableList<String>,
    val trustLedger: MutableList<String>,
    val experienceLog: MutableList<String>,
    val learnedLessons: MutableList<String>,
    val observations: MutableList<SystemObservation>
) {
    companion object {
        const val INTEGRATED_TRUST_GATE = 70f

        fun seeded(direct: Boolean, technical: Boolean, concise: Boolean): PersonaCore {
            val profile = mutableMapOf(
                "directness" to if (direct) 0.8f else 0.4f,
                "technicality" to if (technical) 0.8f else 0.3f,
                "conciseness" to if (concise) 0.8f else 0.4f,
                "warmth" to if (direct) 0.2f else 0.6f
            )
            return PersonaCore(
                toneProfile = profile,
                trustScore = 35f,
                milestones = mutableListOf(),
                trustLedger = mutableListOf("Seeded persona from onboarding toggles."),
                experienceLog = mutableListOf(),
                learnedLessons = mutableListOf(),
                observations = mutableListOf()
            )
        }
    }

    fun increaseTrust(amount: Float, reason: String) {
        trustScore = (trustScore + amount).coerceIn(0f, 100f)
        trustLedger += "INCREASE: $amount for $reason"
        observations += SystemObservation(
            message = "Observation: Trust increased due to validated interaction.",
            adjustment = "Adjustment: Ledger noted '$reason'."
        )
        unlockMilestones()
    }

    fun decayTrust(amount: Float, reason: String) {
        trustScore = (trustScore - amount).coerceIn(0f, 100f)
        trustLedger += "DECAY: $amount for $reason"
        observations += SystemObservation(
            message = "Observation: User rejection or false positive detected.",
            adjustment = "Adjustment: Reduced trust confidence because '$reason'."
        )
    }

    fun supportsIntegratedTier(): Boolean = trustScore >= INTEGRATED_TRUST_GATE

    fun addExperience(entry: String, summarizer: (List<String>) -> List<String> = ::defaultSummarizer) {
        experienceLog += entry
        if (experienceLog.size > 50) {
            val summary = summarizer(experienceLog.takeLast(50)).take(5)
            learnedLessons.clear()
            learnedLessons.addAll(summary)
            experienceLog.clear()
            observations += SystemObservation(
                message = "Observation: Experience log reached retention threshold.",
                adjustment = "Adjustment: Compacted 50 events into ${summary.size} learned lessons."
            )
        }
    }

    fun applyPreferenceHalfLife(
        nowEpochMs: Long,
        lastComplaintEpochMs: Long,
        preferenceKey: String = "directness",
        halfLifeDays: Double = 180.0
    ) {
        val daysElapsed = (nowEpochMs - lastComplaintEpochMs).toDouble() / (1000 * 60 * 60 * 24)
        if (daysElapsed <= 0) return

        val current = toneProfile[preferenceKey] ?: return
        val neutral = 0.5f
        val decayFactor = 0.5.pow(daysElapsed / halfLifeDays).toFloat()
        toneProfile[preferenceKey] = neutral + (current - neutral) * decayFactor
        observations += SystemObservation(
            message = "Observation: Preference drift decay evaluated for $preferenceKey.",
            adjustment = "Adjustment: Shifted $preferenceKey toward neutral using half-life decay."
        )
    }

    private fun unlockMilestones() {
        if (trustScore >= 50f && !milestones.contains("FIRST_CORRECTION_ADAPTED")) {
            milestones += "FIRST_CORRECTION_ADAPTED"
        }
        if (trustScore >= INTEGRATED_TRUST_GATE && !milestones.contains("MONTH_ZERO_BREACH")) {
            milestones += "MONTH_ZERO_BREACH"
        }
    }
}

private fun defaultSummarizer(entries: List<String>): List<String> {
    val buckets = entries.groupBy { it.substringBefore(':').ifBlank { "general" } }
    return buckets.entries
        .sortedByDescending { it.value.size }
        .take(5)
        .map { (topic, grouped) -> "Learned lesson: prioritize '$topic' signals (${grouped.size} events)." }
}
