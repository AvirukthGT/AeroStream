<script setup>
import { computed, ref } from 'vue';
import EfficiencyGauge from './EfficiencyGauge.vue';

const props = defineProps({
  flight: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close']);
const activeTab = ref('General');

// Inference
const fuelWaste = computed(() => {
  if (!props.flight || !props.flight.efficiency_score) return null;
  const inefficiency = 100 - props.flight.efficiency_score;
  return Math.round(inefficiency * 12); 
});

const timeDelay = computed(() => {
  if (!props.flight || !props.flight.predicted_velocity || !props.flight.velocity) return null;
  const diff = props.flight.predicted_velocity - props.flight.velocity;
  if (diff <= 0) return 0;
  return Math.round((diff / props.flight.predicted_velocity) * 60);
});

const weatherText = computed(() => {
  if (!props.flight) return '--';
  const code = props.flight.weather_code;
  if (code === null || code === undefined) return 'Unknown';
  if (code < 3) return 'Clear/Cloudy';
  if (code < 50) return 'Fog/Mist';
  if (code < 80) return 'Rain';
  return 'Storm';
});
</script>

<template>
  <div class="retro-window detail-panel">
    <div class="window-title-bar">
      <span class="title-text">System Properties: {{ flight ? flight.callsign : 'Acc. Selection' }}</span>
      <button class="win-btn" @click="$emit('close')">×</button>
    </div>

    <div v-if="flight" class="content">
      <!-- Functional Tabs -->
      <div class="tabs">
         <div class="tab" :class="{ active: activeTab === 'General' }" @click="activeTab = 'General'">General</div>
         <div class="tab" :class="{ active: activeTab === 'Telemetry' }" @click="activeTab = 'Telemetry'">Telemetry</div>
         <div class="tab" :class="{ active: activeTab === 'Resources' }" @click="activeTab = 'Resources'">Resources</div>
      </div>

      <div class="tab-content inset-panel">
          
          <!-- TAB 1: GENERAL -->
          <div v-if="activeTab === 'General'" class="tab-pane">
              <div class="general-header">
                <div class="icon-box">
                  <!-- Pixel Art Plane Placeholder -->
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="#000080">
                     <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
                  </svg>
                </div>
                <div class="ident-info">
                   <div class="field-row"><strong>I/O Device:</strong> {{ flight.callsign || flight.icao24 }}</div>
                   <div class="field-row"><strong>Manufacturer:</strong> {{ flight.origin_country }}</div>
                   <div class="field-row"><strong>Status:</strong> {{ flight.status }}</div>
                </div>
              </div>

              <div class="separator"></div>

              <!-- Diagnostics List -->
              <div class="driver-status inset-panel">
                 <div class="list-header">Predictive Diagnostics</div>
                 <ul>
                    <li v-if="fuelWaste">
                       <span class="warning">⚠ Fuel_Inefficiency</span>
                       <span class="val">+{{ fuelWaste }} kg/h</span>
                    </li>
                    <li v-if="timeDelay">
                       <span class="danger">🗲 Late_Arrival_Risk</span>
                       <span class="val">+{{ timeDelay }} min</span>
                    </li>
                    <li v-if="!fuelWaste && !timeDelay">System Optimal.</li>
                 </ul>
              </div>

              <!-- New System Monitor (Formerly Gauge) -->
              <fieldset class="monitor-frame">
                 <legend>Performance Monitor</legend>
                 <EfficiencyGauge :flight="flight" />
              </fieldset>
          </div>

          <!-- TAB 2: TELEMETRY -->
          <div v-if="activeTab === 'Telemetry'" class="tab-pane">
              <fieldset class="data-group">
                <legend>Positional Data</legend>
                <div class="data-row"><span>Barometric_Alt:</span> <span class="mono">{{ flight.baro_altitude }} ft</span></div>
                <div class="data-row"><span>Geometric_Alt:</span> <span class="mono">{{ flight.geo_altitude }} ft</span></div>
                <div class="data-row"><span>Velocity_Vector:</span> <span class="mono">{{ Math.round(flight.velocity) }} km/h</span></div>
                <div class="data-row"><span>Heading_Angle:</span> <span class="mono">{{ flight.plane_heading || flight.true_track }}°</span></div>
              </fieldset>

              <fieldset class="data-group">
                <legend>Environmental Sensors</legend>
                <div class="data-row"><span>Atmosphere:</span> <span class="mono">{{ weatherText }}</span></div>
                <div class="data-row"><span>Temp_Outside:</span> <span class="mono">{{ flight.temperature_c }}°C</span></div>
                <div class="data-row"><span>Wind_Reading:</span> <span class="mono">{{ flight.wind_speed_kmh }} km/h</span></div>
              </fieldset>
          </div>

          <!-- TAB 3: RESOURCES -->
          <div v-if="activeTab === 'Resources'" class="tab-pane">
             <div class="data-row">Resource settings:</div>
             <div class="resource-list inset-panel mono">
                I/O Range: {{ flight.icao24.toUpperCase() }} - FFFF<br>
                IRQ: 14<br>
                Memory: {{ flight.request_time_utc || 'N/A' }}<br>
                Driver: v2.0 (AeroStream)<br>
                <br>
                Conflicting device list:<br>
                No conflicts.
             </div>
          </div>

      </div>
      
      <div class="dialog-buttons">
         <button class="win-btn-large">OK</button>
         <button class="win-btn-large" @click="$emit('close')">Cancel</button>
         <button class="win-btn-large" disabled>Apply</button>
      </div>
    </div>
    <div v-else class="empty-state inset-panel">
      <p>Select a device to view properties.</p>
    </div>
  </div>
</template>

<style scoped>
/* Re-affirming scope styles for the new layout */
.detail-panel { height: 100%; font-size: 11px; }
.content { padding: 4px; display: flex; flex-direction: column; flex: 1; }

/* Tabs */
.tabs { display: flex; gap: 2px; padding-left: 2px; transform: translateY(1px); }
.tab {
  padding: 3px 8px;
  border: 1px solid white;
  border-right-color: #404040;
  border-bottom: none;
  border-radius: 3px 3px 0 0;
  background: var(--win-bg);
  cursor: pointer;
  position: relative;
  user-select: none;
}
.tab.active {
  z-index: 5;
  height: 20px;
  margin-top: -2px; /* Grow up */
  border-bottom: 2px solid var(--win-bg); /* Mask the pane border */
}

.tab-content {
  flex: 1;
  padding: 12px;
  background: var(--win-bg);
  border: 2px solid;
  border-color: white #404040 #404040 white;
  z-index: 1;
  overflow-y: auto;
}

/* General Tab Layout */
.general-header { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
.icon-box { 
    width: 32px; height: 32px; 
}
.ident-info { flex: 1; display: flex; flex-direction: column; justify-content: space-around; }
.field-row { margin-bottom: 2px; }

.separator { height: 2px; border-top: 1px solid #808080; border-bottom: 1px solid white; margin: 8px 0; }

.flex-row { display: flex; gap: 10px; }
.gauge-wrapper { width: 100px; }
.driver-status { flex: 1; padding: 4px; background: white; height: 100px; overflow-y: auto; }
.list-header { background: #000080; color: white; padding: 2px; margin-bottom: 2px; }
ul { list-style: none; padding: 0; margin: 0; }
li { display: flex; justify-content: space-between; border-bottom: 1px dotted #ccc; }

.warning { color: #800000; }
.danger { color: #ff0000; }

/* Telemetry & Resources */
fieldset { border: 1px solid; border-color: white #404040 #404040 white; padding: 6px; margin-bottom: 6px; }
legend { margin-left: 6px; padding: 0 2px; }
.data-row { display: flex; justify-content: space-between; margin-bottom: 2px; }

.resource-list { padding: 4px; background: white; height: 120px; color: black; }

.dialog-buttons { display: flex; justify-content: flex-end; gap: 6px; padding: 6px 2px 2px 2px; }
.win-btn-large { min-width: 70px; height: 22px; }

.empty-state {
  margin: 4px; flex: 1; display: flex; align-items: center; justify-content: center; background: white;
}
</style>
