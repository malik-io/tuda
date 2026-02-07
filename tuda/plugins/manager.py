def run_plugin(plugin, system_state):
    if system_state.trust_level < plugin.required_trust:
        raise PermissionError("Trust level insufficient")

    if system_state.inference_mode == "sleep":
        return {"status": "deferred"}

    return plugin.run(system_state)
