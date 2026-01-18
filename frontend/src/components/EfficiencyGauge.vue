<script setup>
import { computed } from 'vue';

const props = defineProps({
  flight: {
    type: Object,
    default: null
  }
});

// Bar width calculation
const efficiencyPercent = computed(() => {
  if (!props.flight || !props.flight.efficiency_score) return 0;
  return Math.max(0, Math.min(100, props.flight.efficiency_score));
});

// Windows 98 Colors (Green/Red)
const barColor = computed(() => {
  /* Win98 used standard #008000 for good, #FF0000 for critical */
  return efficiencyPercent.value >= 80 ? '#008000' : '#FF0000';
});

// Status Text Translation
const statusText = computed(() => {
  const score = props.flight?.efficiency_score || 0;
  if (score >= 100) return 'Over-Performing';
  if (score >= 80) return 'Optimal';
  if (score >= 60) return 'Sub-Optimal';
  return 'Critical Waste';
});
</script>

<template>
  <div class="system-monitor">
    <div v-if="flight">
       <!-- Primary 'CPU Usage' style bar -->
       <div class="monitor-group">
          <div class="monitor-label">
             Efficiency: {{ Math.round(efficiencyPercent) }}% - {{ statusText }}
          </div>
          <div class="bar-container inset-panel">
             <div class="segment-bar" :style="{ width: efficiencyPercent + '%', backgroundColor: barColor }"></div>
          </div>
       </div>

       <div class="stats-table">
          <table>
             <thead>
                <tr>
                   <th>Metric</th>
                   <th>Value</th>
                </tr>
             </thead>
             <tbody>
                <tr title="Current ground speed of the aircraft">
                   <td>Velocity</td>
                   <td>{{ Math.round(flight.velocity) }} km/h</td>
                </tr>
                <tr title="Expected velocity based on physics model">
                   <td>Physics Est.</td>
                   <td>{{ flight.predicted_velocity ? Math.round(flight.predicted_velocity) + ' km/h' : 'N/A' }}</td>
                </tr>
                <tr title="Headwind component subtracting from velocity">
                   <td>Headwind</td>
                   <td>{{ flight.wind_speed_kmh ? Math.round(flight.wind_speed_kmh) + ' km/h' : '0' }}</td>
                </tr>
                <tr title="Deviation from optimal flight path">
                   <td>Offset Angle</td>
                   <td>{{ flight.wind_offset_angle ? Math.round(flight.wind_offset_angle) + '°' : '0°' }}</td>
                </tr>
             </tbody>
          </table>
       </div>
       
       <div class="legend-box inset-panel">
          <span class="info-icon">🛈</span> Efficiency &lt; 80% indicates increased fuel consumption due to wind/weather drag.
       </div>
    </div>
    <div v-else class="no-data">
       Waiting for signal...
    </div>
  </div>
</template>

<style scoped>
.system-monitor {
  font-family: 'Tahoma', sans-serif;
  font-size: 11px;
  color: black;
  padding: 4px;
}

.monitor-group {
  margin-bottom: 8px;
}

.monitor-label {
  margin-bottom: 2px;
}

.bar-container {
  height: 16px;
  background: white;
  padding: 1px;
}

.segment-bar {
  height: 100%;
  /* Win98 Progress Bar Color */
  background-color: #000080; 
}

.stats-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border: 1px solid #808080; /* Darker border for table */
}

th {
  text-align: left;
  background: #d4d0c8; /* Button face */
  border-bottom: 1px solid #808080;
  padding: 2px 4px;
  font-weight: normal;
}

td {
  padding: 2px 4px;
  border-bottom: 1px solid #e0e0e0;
}

.no-data {
  text-align: center;
  color: #808080;
  padding: 10px;
}

.legend-box {
  margin-top: 8px;
  padding: 4px;
  font-family: 'Tahoma', sans-serif;
  font-size: 10px;
  background: #ffffe0;
  border: 1px solid #808080;
  color: #404040;
}
.info-icon {
  font-weight: bold;
  color: navy;
  margin-right: 4px;
}
</style>
