package com.kaomoji.overlay.ai

import java.time.Instant

data class SystemObservation(
    val message: String,
    val adjustment: String,
    val timestampEpochMs: Long = Instant.now().toEpochMilli()
)
