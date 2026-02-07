package com.kaomoji.overlay.intelligence

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import org.json.JSONArray
import org.json.JSONObject

interface PersonaStore {
    fun loadPersona(): PersonaCore
    fun savePersona(personaCore: PersonaCore)
}

class PersonaRepository(context: Context) : PersonaStore {
    private val prefs = EncryptedSharedPreferences.create(
        context,
        "persona_secure_store",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    override fun loadPersona(): PersonaCore {
        val raw = prefs.getString(KEY_PERSONA, null) ?: return seedPersonaCore(
            direct = false,
            technical = false,
            concise = false
        )
        return parsePersona(raw)
    }

    fun seedAndSave(direct: Boolean, technical: Boolean, concise: Boolean): PersonaCore {
        val persona = seedPersonaCore(direct, technical, concise)
        savePersona(persona)
        return persona
    }

    override fun savePersona(personaCore: PersonaCore) {
        prefs.edit().putString(KEY_PERSONA, serializePersona(personaCore)).apply()
    }

    private fun serializePersona(personaCore: PersonaCore): String {
        val tone = JSONObject()
        personaCore.toneProfile.forEach { (key, value) -> tone.put(key, value.toDouble()) }

        val milestones = JSONArray()
        personaCore.milestones.forEach { milestones.put(it) }

        val trustHistory = JSONArray()
        personaCore.trustHistory.forEach {
            trustHistory.put(
                JSONObject()
                    .put("reason", it.reason)
                    .put("delta", it.delta.toDouble())
                    .put("timestamp", it.timestamp)
            )
        }

        return JSONObject()
            .put("toneProfile", tone)
            .put("trustScore", personaCore.trustScore.toDouble())
            .put("milestones", milestones)
            .put("trustHistory", trustHistory)
            .toString()
    }

    private fun parsePersona(raw: String): PersonaCore {
        val root = JSONObject(raw)
        val toneObj = root.getJSONObject("toneProfile")
        val toneMap = buildMap<String, Float> {
            toneObj.keys().forEach { put(it, toneObj.getDouble(it).toFloat()) }
        }

        val milestones = buildList {
            val array = root.optJSONArray("milestones") ?: JSONArray()
            for (i in 0 until array.length()) {
                add(array.getString(i))
            }
        }

        val history = buildList {
            val array = root.optJSONArray("trustHistory") ?: JSONArray()
            for (i in 0 until array.length()) {
                val item = array.getJSONObject(i)
                add(
                    TrustEvent(
                        reason = item.getString("reason"),
                        delta = item.getDouble("delta").toFloat(),
                        timestamp = item.getLong("timestamp")
                    )
                )
            }
        }

        return PersonaCore(
            toneProfile = toneMap,
            trustScore = root.getDouble("trustScore").toFloat(),
            milestones = milestones,
            trustHistory = history
        )
    }

    companion object {
        private const val KEY_PERSONA = "persona_core"
    }
}
