package com.kaomoji.overlay

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.kaomoji.overlay.ai.DeviceMonitor
import com.kaomoji.overlay.ai.PersonaStore
import com.kaomoji.overlay.ai.StateController
import com.kaomoji.overlay.ai.TelemetrySnapshot
import com.kaomoji.overlay.ai.ThermalState
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    private val overlayPermissionLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
        if (checkOverlayPermission()) {
            startOverlayService()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val personaStore = PersonaStore(this)
        val deviceMonitor = DeviceMonitor()
        val stateController = StateController(deviceMonitor)

        setContent {
            val personaState = remember { mutableStateOf(personaStore.loadOrSeed(direct = true, technical = true, concise = true)) }
            val decisionState = remember { mutableStateOf(stateController.chooseTier(personaState.value)) }
            val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
            val scope = rememberCoroutineScope()

            LaunchedEffect(personaState.value.trustScore) {
                personaStore.save(personaState.value)
            }

            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    ModalNavigationDrawer(
                        drawerState = drawerState,
                        drawerContent = {
                            InsightsDrawer(personaState.value.observations)
                        }
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Text("Current Tier: ${decisionState.value.tier}")
                            Text("Reason: ${decisionState.value.reason}")
                            decisionState.value.notification?.let { Text(it) }

                            Button(onClick = {
                                personaState.value.increaseTrust(12f, "User accepted adaptation")
                                decisionState.value = stateController.chooseTier(personaState.value)
                                personaStore.save(personaState.value)
                            }) {
                                Text("Simulate quality interaction")
                            }

                            Button(onClick = {
                                personaState.value.decayTrust(20f, "User rejected suggestion")
                                decisionState.value = stateController.chooseTier(personaState.value)
                                personaStore.save(personaState.value)
                            }) {
                                Text("Simulate rejection")
                            }

                            Button(onClick = {
                                deviceMonitor.setSimulatedStress(
                                    TelemetrySnapshot(15, isCharging = false, thermalState = ThermalState.HIGH, inferenceLatencyMs = 2300)
                                )
                                decisionState.value = stateController.chooseTier(personaState.value)
                            }) {
                                Text("Simulate stress")
                            }

                            Button(onClick = {
                                deviceMonitor.setSimulatedStress(
                                    TelemetrySnapshot(95, isCharging = true, thermalState = ThermalState.COOL, inferenceLatencyMs = 200)
                                )
                                decisionState.value = stateController.chooseTier(personaState.value)
                            }) {
                                Text("Simulate cool charging")
                            }

                            Button(onClick = {
                                personaState.value.addExperience("verbosity:User dismissed long summary")
                                personaState.value.applyPreferenceHalfLife(
                                    nowEpochMs = System.currentTimeMillis(),
                                    lastComplaintEpochMs = System.currentTimeMillis() - (190L * 24 * 60 * 60 * 1000)
                                )
                                personaStore.save(personaState.value)
                            }) {
                                Text("Trigger pruning/decay check")
                            }

                            Button(onClick = { scope.launch { drawerState.open() } }) {
                                Text("Open Insights drawer")
                            }

                            Button(onClick = {
                                if (checkOverlayPermission()) {
                                    startOverlayService()
                                } else {
                                    requestOverlayPermission()
                                }
                            }) {
                                Text("Start Overlay")
                            }
                        }
                    }
                }
            }
        }
    }

    private fun checkOverlayPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Settings.canDrawOverlays(this)
        } else {
            true
        }
    }

    private fun requestOverlayPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            overlayPermissionLauncher.launch(intent)
        }
    }

    private fun startOverlayService() {
        val intent = Intent(this, OverlayService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }
}

@Composable
private fun InsightsDrawer(observations: List<com.kaomoji.overlay.ai.SystemObservation>) {
    ModalDrawerSheet {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Insights", style = MaterialTheme.typography.titleLarge)
            if (observations.isEmpty()) {
                Text("No observations yet.")
            } else {
                observations.takeLast(10).reversed().forEach {
                    Text("${it.message} ${it.adjustment}")
                }
            }
        }
    }
}
