package com.kaomoji.overlay

import android.accessibilityservice.AccessibilityService
import android.util.Log
import android.view.accessibility.AccessibilityEvent

class KaomojiAccessibilityService : AccessibilityService() {

    private val TAG = "KaomojiAccessibility"

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        event?.let {
            val eventText = it.text.joinToString("\n")
            if (eventText.isNotBlank()) {
                Log.d(TAG, "Captured text: $eventText")
            }
        }
    }

    override fun onInterrupt() {
        Log.d(TAG, "Accessibility service interrupted.")
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.d(TAG, "Accessibility service connected.")
    }
}
