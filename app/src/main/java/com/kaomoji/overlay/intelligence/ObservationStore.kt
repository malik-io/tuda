package com.kaomoji.overlay.intelligence

import kotlin.math.max

class ObservationStore {
    private val observations = mutableListOf<String>()

    fun add(observation: String, adjustment: String) {
        val entry = "Observation: $observation Action: $adjustment"
        observations.add(entry)
        if (observations.size > 100) {
            observations.removeAt(0)
        }
    }

    fun all(): List<String> = observations.toList()
}

data class ConsciousnessState(
    val experienceLog: List<String> = emptyList(),
    val learnedLessons: List<String> = emptyList(),
    val lastVerbosityComplaintEpochMs: Long? = null
)

class ConsciousnessPruner(
    private val observationStore: ObservationStore
) {
    fun prune(state: ConsciousnessState): ConsciousnessState {
        if (state.experienceLog.size <= 50) {
            return enforceStorageBudget(state)
        }

        val window = state.experienceLog.takeLast(50)
        val lessonGroups = window.chunked(max(1, window.size / 5))
        val lessons = lessonGroups.take(5).mapIndexed { index, entries ->
            "Lesson ${index + 1}: ${entries.first().take(120)}"
        }

        observationStore.add(
            observation = "Experience log exceeded 50 entries.",
            adjustment = "Condensing recent interactions into 5 learned lessons."
        )

        return enforceStorageBudget(
            state.copy(
                experienceLog = state.experienceLog.drop(50),
                learnedLessons = (state.learnedLessons + lessons).takeLast(20)
            )
        )
    }

    fun applyPreferenceHalfLife(
        personaCore: PersonaCore,
        nowEpochMs: Long,
        halfLifeDays: Int = 180
    ): PersonaCore {
        val complaintTime = personaCore.trustHistory
            .lastOrNull { it.reason.contains("verbosity", ignoreCase = true) }
            ?.timestamp
            ?: return personaCore

        val halfLifeMs = halfLifeDays * 24L * 60L * 60L * 1000L
        val elapsed = (nowEpochMs - complaintTime).coerceAtLeast(0)
        if (elapsed < halfLifeMs) {
            return personaCore
        }

        val original = personaCore.toneProfile["directness"] ?: 0.5f
        val decayed = 0.5f + ((original - 0.5f) * 0.5f)

        observationStore.add(
            observation = "No recent verbosity complaints in half-life window.",
            adjustment = "Moving directness profile gradually toward neutral."
        )

        return personaCore.copy(
            toneProfile = personaCore.toneProfile + ("directness" to decayed)
        )
    }

    private fun enforceStorageBudget(state: ConsciousnessState): ConsciousnessState {
        val maxChars = 5 * 1024 * 1024
        var log = state.experienceLog
        var lessons = state.learnedLessons
        while ((log.joinToString("\n").length + lessons.joinToString("\n").length) > maxChars && log.isNotEmpty()) {
            log = log.drop(1)
        }
        while ((log.joinToString("\n").length + lessons.joinToString("\n").length) > maxChars && lessons.isNotEmpty()) {
            lessons = lessons.drop(1)
        }
        return state.copy(experienceLog = log, learnedLessons = lessons)
    }
}
