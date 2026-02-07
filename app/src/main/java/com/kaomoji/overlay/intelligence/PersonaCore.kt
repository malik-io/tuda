package com.kaomoji.overlay.intelligence

data class PersonaCore(
    val toneProfile: Map<String, Float>,
    val trustScore: Float,
    val milestones: List<String>,
    val trustHistory: List<TrustEvent>
)

data class TrustEvent(
    val reason: String,
    val delta: Float,
    val timestamp: Long = System.currentTimeMillis()
)

enum class IntelligenceTier {
    TIER_1,
    TIER_2,
    TIER_3
}

fun seedPersonaCore(direct: Boolean, technical: Boolean, concise: Boolean): PersonaCore {
    val directness = when {
        direct && concise -> 0.85f
        direct -> 0.75f
        concise -> 0.65f
        else -> 0.5f
    }
    val warmth = if (technical) 0.3f else 0.55f
    val detail = if (technical && !concise) 0.8f else if (concise) 0.35f else 0.6f

    return PersonaCore(
        toneProfile = mapOf(
            "directness" to directness,
            "warmth" to warmth,
            "detail" to detail
        ),
        trustScore = 30f,
        milestones = emptyList(),
        trustHistory = emptyList()
    )
}
