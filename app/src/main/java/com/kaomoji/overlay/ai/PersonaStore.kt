package com.kaomoji.overlay.ai

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import org.json.JSONArray
import org.json.JSONObject

class PersonaStore(context: Context) {
    private val preferences: SharedPreferences = try {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        EncryptedSharedPreferences.create(
            context,
            "persona_secure_store",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    } catch (_: Exception) {
        context.getSharedPreferences("persona_fallback_store", Context.MODE_PRIVATE)
    }

    fun save(persona: PersonaCore) {
        preferences.edit().putString(KEY_PERSONA_JSON, encode(persona)).apply()
    }

    fun loadOrSeed(direct: Boolean = true, technical: Boolean = true, concise: Boolean = true): PersonaCore {
        val raw = preferences.getString(KEY_PERSONA_JSON, null)
        return if (raw.isNullOrBlank()) {
            PersonaCore.seeded(direct, technical, concise).also(::save)
        } else {
            decode(raw)
        }
    }

    private fun encode(persona: PersonaCore): String {
        return JSONObject().apply {
            put("trustScore", persona.trustScore)
            put("toneProfile", JSONObject(persona.toneProfile.mapValues { it.value.toDouble() }))
            put("milestones", JSONArray(persona.milestones))
            put("trustLedger", JSONArray(persona.trustLedger))
            put("experienceLog", JSONArray(persona.experienceLog))
            put("learnedLessons", JSONArray(persona.learnedLessons))
            put("observations", JSONArray(persona.observations.map {
                JSONObject().apply {
                    put("message", it.message)
                    put("adjustment", it.adjustment)
                    put("timestamp", it.timestampEpochMs)
                }
            }))
        }.toString()
    }

    private fun decode(value: String): PersonaCore {
        val json = JSONObject(value)
        val tone = json.getJSONObject("toneProfile")
        val toneMap = mutableMapOf<String, Float>()
        tone.keys().forEach { key -> toneMap[key] = tone.getDouble(key).toFloat() }

        return PersonaCore(
            toneProfile = toneMap,
            trustScore = json.optDouble("trustScore", 35.0).toFloat(),
            milestones = json.optJSONArray("milestones").toMutableStringList(),
            trustLedger = json.optJSONArray("trustLedger").toMutableStringList(),
            experienceLog = json.optJSONArray("experienceLog").toMutableStringList(),
            learnedLessons = json.optJSONArray("learnedLessons").toMutableStringList(),
            observations = json.optJSONArray("observations").toObservationList()
        )
    }

    companion object {
        private const val KEY_PERSONA_JSON = "persona_json"
    }
}

private fun JSONArray?.toMutableStringList(): MutableList<String> {
    if (this == null) return mutableListOf()
    return MutableList(length()) { index -> getString(index) }
}

private fun JSONArray?.toObservationList(): MutableList<SystemObservation> {
    if (this == null) return mutableListOf()
    return MutableList(length()) { index ->
        val item = getJSONObject(index)
        SystemObservation(
            message = item.getString("message"),
            adjustment = item.getString("adjustment"),
            timestampEpochMs = item.optLong("timestamp", 0L)
        )
    }
}
