<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import TheMap from './components/TheMap.vue';
import FlightList from './components/FlightList.vue';
import FlightDetailPanel from './components/FlightDetailPanel.vue'; 
import BootSequence from './components/BootSequence.vue';
import SystemLog from './components/SystemLog.vue';
import AnalyticsPanel from './components/AnalyticsPanel.vue';
import ShutdownScreen from './components/ShutdownScreen.vue';
import api from './services/api';

const flights = ref([]);
const selectedFlight = ref(null);
const loading = ref(true);
const booted = ref(false); // Controls boot sequence
const isShuttingDown = ref(false); // Controls shutdown sequence
const isDrawerOpen = ref(false);

const handleReboot = () => {
   isShuttingDown.value = false;
   booted.value = false; // Triggers BootSequence v-if="!booted"
   // Reset other states
   isStartMenuOpen.value = false;
   showMonitor.value = false;
   showTerminal.value = false;
   showAnalytics.value = false;
};

// Window Management
const isStartMenuOpen = ref(false);
const showMonitor = ref(false);
const showTerminal = ref(false);
const showAnalytics = ref(false);

// Map Theme Logic
const theme = ref('cyber');
const toggleTheme = () => {
  if (theme.value === 'cyber') theme.value = 'pro';
  else if (theme.value === 'pro') theme.value = 'light';
  else theme.value = 'cyber';
};

watch(theme, (newTheme) => {
  document.body.setAttribute('data-theme', newTheme);
}, { immediate: true });

const mapTileUrl = computed(() => {
  if (theme.value === 'light') return 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
  return 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
});

const loadData = async () => {
  const data = await api.getFlights();
  flights.value = data;
  loading.value = false;
  
  if (selectedFlight.value) {
    const updated = flights.value.find(f => f.icao24 === selectedFlight.value.icao24);
    if (updated) selectedFlight.value = updated;
  }
};

// Deduplicated & Filtered List
const sortedFlights = computed(() => {
  const unique = new Map();
  flights.value.forEach(f => {
    // Deduplication Priority: Analyzed > Raw
    if (!unique.has(f.icao24)) {
      unique.set(f.icao24, f);
    } else {
      const existing = unique.get(f.icao24);
      if (existing.status === 'Raw' && f.status !== 'Raw') {
        unique.set(f.icao24, f);
      }
    }
  });

  return Array.from(unique.values())
    .filter(f => f.status !== 'Raw')
    //.filter(f => f.origin_country === 'Australia') // Temporarily disabled for debugging
    .sort((a, b) => a.efficiency_score - b.efficiency_score);
});

// Critical Flights for Monitor
const criticalFlights = computed(() => {
  return sortedFlights.value.filter(f => f.efficiency_score < 80);
});

// Map Data Source (Synced with List Filters)
const mapFlights = ref([]);

const handleSelectFlight = (flight) => {
  selectedFlight.value = flight;
  if (flight && flight.efficiency_score < 80) {
    isDrawerOpen.value = true;
  }
};

const selectionRecommendations = computed(() => {
  if (!selectedFlight.value) return ["Select a flight track for analysis."];
  const f = selectedFlight.value;
  const recs = [];
  if (f.efficiency_score < 70) recs.push("CRITICAL: Efficiency low. Request FL change.");
  if (f.wind_speed_kmh > 40) recs.push(`Headwind detected (${Math.round(f.wind_speed_kmh)} km/h). Deviation advised.`);
  if (f.predicted_velocity && f.velocity < f.predicted_velocity) recs.push("Velocity below physics model baseline. Check throttle.");
  if (recs.length === 0) recs.push("Flight parameters nominal. Continue monitoring.");
  return recs;
});

onMounted(() => {
  document.body.setAttribute('data-theme', theme.value);
  loadData();
  setInterval(loadData, 10000); 
});
</script>

<template>
  <BootSequence v-if="!booted" @complete="booted = true" />
  <ShutdownScreen v-if="isShuttingDown" @reboot="handleReboot" />

  <div v-else class="desktop">
    <div class="scanlines"></div>
    <!-- Taskbar -->
    <div class="taskbar">
       <div class="start-btn-wrapper">
         <button class="start-btn" :class="{ active: isStartMenuOpen }" @click="isStartMenuOpen = !isStartMenuOpen">
            <span style="font-size:16px; margin-right:4px;">✈</span> Start
         </button>
       </div>
       <div class="divider"></div>
       <div class="active-app">AeroStream Manager.exe</div>
       <div v-if="showMonitor" class="active-app monitor-task" @click="showMonitor = true">Flight Monitor</div>
       <div class="system-tray">
          <span class="tray-icon">🔊</span>
          <span>{{ new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
       </div>
    </div>

    <!-- Start Menu -->
    <div v-if="isStartMenuOpen" class="start-menu retro-window">
       <div class="start-side-strip">
          <span class="vertical-text">AEROSTREAM 98</span>
       </div>
       <div class="start-options">
          <div class="start-item" @click="showMonitor = true; isStartMenuOpen = false">
             <span class="icon">⚠</span> 
             <span class="label">Priority Monitor...</span>
          </div>
          <div class="start-item" @click="showTerminal = true; isStartMenuOpen = false">
             <span class="icon">_</span> 
             <span class="label">System Terminal...</span>
          </div>
          <div class="start-item" @click="showAnalytics = true; isStartMenuOpen = false">
             <span class="icon" style="filter: grayscale(100%) brightness(0);">📉</span> 
             <span class="label">Fleet Analytics...</span>
          </div>
          <div class="start-item" @click="loadData(); isStartMenuOpen = false">
             <span class="icon">⟳</span> 
             <span class="label">Refresh Sensors</span>
          </div>
          <hr class="menu-divider">
          <div class="start-item" @click="isShuttingDown = true; isStartMenuOpen = false">
             <span class="icon">x</span> 
             <span class="label">Shut Down</span>
          </div>
       </div>
    </div>

    <!-- Monitor Window (Floating) -->
    <div v-if="showMonitor" class="retro-window monitor-window">
       <div class="window-title-bar warning-title">
          <span class="title-text">⚠ PRIORITY MONITORING LIST</span>
          <button class="win-btn" @click="showMonitor = false">×</button>
       </div>
       <div class="window-content" style="background:white; padding:4px;">
           <div v-if="criticalFlights.length === 0" class="safe-state">
              No critical flights detected.
           </div>
           <FlightList 
             v-else
             :flights="criticalFlights" 
             :selected-id="selectedFlight?.icao24"
             @select-flight="handleSelectFlight" 
           />
       </div>
       <div class="status-bar">
          {{ criticalFlights.length }} Objects Tracking
       </div>
    </div>

    <!-- Terminal Window -->
    <div v-if="showTerminal" class="retro-window monitor-window" style="top:50px; left:300px; height:300px; z-index:2001;">
       <div class="window-title-bar" style="background:#000080;">
          <span class="title-text">C:\SYSTEM\LOG.EXE</span>
          <button class="win-btn" @click="showTerminal = false">×</button>
       </div>
       <div class="window-content">
          <SystemLog :flights="flights" />
       </div>
    </div>

    <!-- Analytics Window -->
    <div v-if="showAnalytics" class="retro-window monitor-window" style="top:150px; left:400px; height:400px; width:400px; z-index:2002;">
       <div class="window-title-bar" style="background:#008080;">
          <span class="title-text">Dashboard_Analytics.xls</span>
          <button class="win-btn" @click="showAnalytics = false">×</button>
       </div>
       <div class="window-content">
          <AnalyticsPanel :flights="flights" />
       </div>
    </div>

    <main class="grid-layout">
      <!-- Normal Windows (List, Map, Details) -->
      <aside class="retro-window">
        <div class="window-title-bar">
           <span class="title-text">Flight_Sensors</span>
           <div class="win-controls">
              <button class="win-btn">_</button>
              <button class="win-btn">×</button>
           </div>
        </div>
        <div class="window-content" style="background:#d4d0c8;">
             <div v-if="loading && flights.length === 0" class="loading-text">Loading drivers...</div>
             <FlightList 
               v-else 
               :flights="sortedFlights" 
               :selected-id="selectedFlight?.icao24"
                @select-flight="handleSelectFlight" 
                @filter-update="mapFlights = $event"
              />
        </div>
      </aside>


      <!-- Window 2: Map -->
      <section class="retro-window">
         <div class="window-title-bar">
           <span class="title-text">Global_Map_View</span>
           <div class="win-controls">
              <button class="win-btn">_</button>
              <button class="win-btn">□</button>
              <button class="win-btn">×</button>
           </div>
        </div>
         <div class="window-content inset-panel map-container">
            <TheMap 
                :flights="mapFlights" 
                :selected-flight-id="selectedFlight?.icao24"
                @select-flight="handleSelectFlight"
            />

            <!-- COLLAPSIBLE BOTTOM DRAWER -->
            <div class="map-drawer" :class="{ open: isDrawerOpen }">
               <div class="drawer-handle" @click="isDrawerOpen = !isDrawerOpen">
                  <span>{{ isDrawerOpen ? '▼ Hide Recommendation Engine' : '▲ Show Intelligence' }}</span>
               </div>
               <div class="drawer-content inset-panel">
                  <div class="rec-icon">
                     💡
                  </div>
                  <div class="rec-text">
                     <div v-for="(rec, i) in selectionRecommendations" :key="i" class="rec-line">
                        > {{ rec }}
                     </div>
                  </div>
               </div>
            </div>
         </div>
      </section>

      <!-- Window 3: Details -->
      <aside class="details-container"> 
         <FlightDetailPanel 
            :flight="selectedFlight" 
            @close="selectedFlight = null" 
         />
      </aside>
    </main>
  </div>
</template>

<style scoped>
.desktop {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 4px;
  gap: 4px;
  background-color: var(--bg-desktop); 
  position: relative;
  overflow: hidden;
}

.scanlines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.1),
    rgba(0, 0, 0, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
  z-index: 9999;
}

/* Taskbar Updates */
.taskbar {
  background: var(--win-bg);
  border-top: 2px solid var(--win-border-light);
  border-left: 2px solid var(--win-border-light);
  border-right: 2px solid var(--win-border-darker);
  border-bottom: 2px solid var(--win-border-darker);
  height: 28px;
  padding: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.start-btn {
  font-weight: bold;
  height: 20px;
  display: flex;
  align-items: center;
  padding: 0 6px;
}

.active-app {   
   background: #e0e0e0; 
   border: 2px solid; 
   border-color: #808080 white white #808080;
   padding: 2px 8px;
   font-weight: bold;
   color: black;
}

.system-tray {
  margin-left: auto;
  border: 2px solid;
  border-color: #808080 white white #808080;
  padding: 0 8px;
  height: 22px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--win-bg);
}

.grid-layout {
  display: grid;
  grid-template-columns: 250px 1fr 300px; /* Adjusted col widths */
  gap: 6px;
  flex: 1;
  min-height: 0;
}

/* Map Container Relative for Drawer */
.map-container {
  position: relative;
  overflow: hidden; /* Clip drawer */
}

/* DRAWER STYLES */
.map-drawer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--win-bg);
  border-top: 2px solid var(--win-border-light);
  transform: translateY(100px); /* Hidden by default */
  transition: transform 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  height: 120px; /* Fixed height for drawer */
}

.map-drawer.open {
  transform: translateY(0);
}

.drawer-handle {
  height: 18px;
  background: navy;
  color: white;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 1px solid white;
}

.drawer-content {
  flex: 1;
  margin: 4px;
  background: white;
  display: flex;
  align-items: flex-start;
  padding: 8px;
  gap: 10px;
  overflow-y: auto;
}

.rec-icon { font-size: 24px; }
.rec-text { font-family: 'Tahoma', sans-serif; font-size: 11px; color: black; }
.rec-line { margin-bottom: 4px; }

/* Structural classes reused from before */
.retro-window { display: flex; flex-direction: column; min-height:0; }
.window-title-bar { background: linear-gradient(to right, navy, #1084d0); color: white; padding: 2px 4px; display: flex; font-weight: bold; height: 18px; align-items: center; }
.title-text { flex: 1; font-size: 11px; }
.win-controls { display: flex; gap: 2px; }
.win-btn { width: 14px; height: 14px; font-size: 9px; line-height: 1; background: #c0c0c0; border: 1px outset white; padding: 0; }

.window-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Important: Child components handle their own scroll */
  position: relative;
}
.details-container { display: flex; flex-direction: column; min-height: 0; }
.map-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--grid-line);
  font-family: var(--font-tech);
  border: 1px dashed var(--border-color);
}

.overlay-hud {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 4px 8px;
  background: var(--bg-color);
  border: 1px solid var(--accent);
  color: var(--accent);
  font-size: 10px;
  font-family: var(--font-tech);
  pointer-events: none;
}

/* Start Menu */
.start-menu {
  position: absolute;
  bottom: 34px;
  left: 4px;
  width: 200px;
  background: #d4d0c8;
  z-index: 5000;
  display: flex;
  padding: 2px;
  border: 2px solid;
  border-color: white #808080 #808080 white;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
}
.start-side-strip {
  width: 25px;
  background: linear-gradient(to bottom, #000040, #000080);
  color: white;
  display: flex;
  align-items: flex-end;
  padding-bottom: 5px;
}
.vertical-text {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  font-weight: bold;
  font-size: 14px;
  padding: 4px;
}
.start-options {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.start-item {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Tahoma', sans-serif;
  color: black;
}
.start-item:hover {
  background: #000080;
  color: white;
}
.menu-divider {
  border-top: 1px solid #808080;
  border-bottom: 1px solid white;
  margin: 4px 2px;
}

/* Monitor Window */
.monitor-window {
  position: absolute;
  top: 100px; 
  left: 100px;
  width: 300px;
  height: 400px;
  z-index: 2000;
  box-shadow: 4px 4px 0 rgba(0,0,0,0.5);
}
.warning-title {
  background: linear-gradient(to right, #800000, #ff0000);
}
.monitor-task {
  margin-left: 4px;
  cursor: pointer;
}
.safe-state {
  text-align: center;
  padding: 20px;
  color: #008000;
  font-weight: bold;
}
.status-bar {
  border-top: 1px solid #808080;
  border-bottom: 1px solid white;
  padding: 2px 4px;
  font-size: 10px;
  color: #404040;
}

/* Pressed Start Button */
.start-btn.active {
  border-color: #404040 white white #404040;
  background: #e0e0e0;
  padding: 1px 5px 0 7px; /* Shift effect */
}
</style>
