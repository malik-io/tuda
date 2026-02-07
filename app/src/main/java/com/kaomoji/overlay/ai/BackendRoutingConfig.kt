package com.kaomoji.overlay.ai

object BackendRoutingConfig {
    val backendUrl: String = System.getenv("TUDA_BACKEND_URL") ?: "http://10.0.2.2:8000"

    val computeMode: ComputeMode = runCatching {
        ComputeMode.valueOf(System.getenv("TUDA_COMPUTE_MODE") ?: ComputeMode.ADAPTIVE.name)
    }.getOrDefault(ComputeMode.ADAPTIVE)
}
