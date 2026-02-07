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
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Divider
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import com.kaomoji.overlay.intelligence.ConsciousnessPruner
import com.kaomoji.overlay.intelligence.ConsciousnessState
import com.kaomoji.overlay.intelligence.DeviceMonitor
import com.kaomoji.overlay.intelligence.ObservationStore
import com.kaomoji.overlay.intelligence.PersonaRepository
import com.kaomoji.overlay.intelligence.ThermalBatteryGovernor
import com.kaomoji.overlay.intelligence.TrustEngine

class MainActivity : ComponentActivity() {

    private val overlayPermissionLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
        if (checkOverlayPermission()) {
            startOverlayService()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                IntelligenceControlScreen(onStartOverlay = {
                    if (checkOverlayPermission()) {
                        startOverlayService()
                    } else {
                        requestOverlayPermission()
                    }
                })
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IntelligenceControlScreen(onStartOverlay: () -> Unit) {
    val context = LocalContext.current
    val observationStore = remember { ObservationStore() }
    val repository = remember { PersonaRepository(context) }
    val trustEngine = remember { TrustEngine(repository, observationStore) }
    val monitor = remember { DeviceMonitor(context) }
    val governor = remember { ThermalBatteryGovernor(monitor, trustEngine, observationStore) }
    val pruner = remember { ConsciousnessPruner(observationStore) }

    var persona by remember { mutableStateOf(repository.loadPersona()) }
    var consciousness by remember { mutableStateOf(ConsciousnessState()) }
    var activeTier by remember { mutableStateOf("TIER_2") }
    var notice by remember { mutableStateOf<String?>(null) }

    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    LaunchedEffect(Unit) {
        if (persona.trustHistory.isEmpty()) {
            persona = repository.seedAndSave(direct = true, technical = true, concise = true)
            observationStore.add(
                observation = "Persona seed created from onboarding toggles (Direct/Technical/Concise).",
                adjustment = "Initialized tone profile in encrypted state store."
            )
        }
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet {
                Text("System Insights", modifier = Modifier.padding(16.dp), style = MaterialTheme.typography.titleMedium)
                Divider()
                LazyColumn(contentPadding = PaddingValues(12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    items(observationStore.all()) {
                        Text(it, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
    ) {
        Scaffold(
            topBar = { TopAppBar(title = { Text("Trust & Thermal Controller") }) }
        ) { padding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Text("Trust Score: ${"%.2f".format(persona.trustScore)}")
                Text("Active Tier: $activeTier")
                if (notice != null) {
                    Text(notice!!, color = MaterialTheme.colorScheme.error)
                }
                Button(onClick = {
                    persona = trustEngine.increaseTrust(15f, "User correction accepted")
                }) {
                    Text("Simulate Quality Interaction")
                }
                Button(onClick = {
                    persona = trustEngine.decayTrust(10f, "User rejected response")
                }) {
                    Text("Simulate Rejection")
                }
                Button(onClick = {
                    monitor.observeInferenceLatency(2600)
                    val decision = governor.decideTier()
                    activeTier = decision.tier.name
                    notice = decision.notice
                }) {
                    Text("Simulate Stress")
                }
                Button(onClick = {
                    consciousness = pruner.prune(
                        consciousness.copy(
                            experienceLog = consciousness.experienceLog + List(55) { idx -> "Interaction note ${idx + 1}" }
                        )
                    )
                }) {
                    Text("Trigger Consciousness Pruning")
                }
                Button(onClick = {
                    onStartOverlay()
                }) {
                    Text("Start Overlay")
                }
                Button(onClick = {
                    if (drawerState.isClosed) {
                        scope.launch { drawerState.open() }
                    }
                }) {
                    Text("Open Insights Drawer")
                }
                Text("Milestones: ${persona.milestones.joinToString()}")
                Text("Lessons: ${consciousness.learnedLessons.size}")
            }
        }
    }
}
