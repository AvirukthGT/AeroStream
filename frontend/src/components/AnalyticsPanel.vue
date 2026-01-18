<script setup>
import { computed } from 'vue';

const props = defineProps({
  flights: Array
});

const stats = computed(() => {
  const total = props.flights.length;
  const critical = props.flights.filter(f => f.efficiency_score < 70).length;
  const warning = props.flights.filter(f => f.efficiency_score >= 70 && f.efficiency_score < 90).length;
  const optimal = props.flights.filter(f => f.efficiency_score >= 90).length;
  
  // Calculate average altitude (exclude zero/null)
  const airborne = props.flights.filter(f => (f.baro_altitude || 0) > 100);
  const avgAlt = airborne.length ? Math.round(airborne.reduce((acc, f) => acc + f.baro_altitude, 0) / airborne.length) : 0;
  
  return { total, critical, warning, optimal, avgAlt };
});
</script>

<template>
  <div class="analytics-body">
     <div class="stat-block">
        <div class="label">Total Tracked</div>
        <div class="value">{{ stats.total }}</div>
     </div>
     <div class="stat-block">
        <div class="label">Avg Flight Level</div>
        <div class="value">{{ Math.round(stats.avgAlt / 100) }} FL</div>
     </div>
     
     <div class="chart-box">
        <div class="label">Efficiency Class Distribution</div>
        <div class="bar-chart">
           <!-- Green -->
           <div class="bar-group">
              <div class="bar optimal" :style="{ width: (stats.optimal / stats.total * 100) + '%' }"></div>
              <span class="count">{{ stats.optimal }} Optimal</span>
           </div>
           <!-- Yellow -->
           <div class="bar-group">
              <div class="bar warning" :style="{ width: (stats.warning / stats.total * 100) + '%' }"></div>
              <span class="count">{{ stats.warning }} Ineff.</span>
           </div>
           <!-- Red -->
           <div class="bar-group">
              <div class="bar critical" :style="{ width: (stats.critical / stats.total * 100) + '%' }"></div>
              <span class="count">{{ stats.critical }} Crit.</span>
           </div>
        </div>
     </div>
  </div>
</template>

<style scoped>
.analytics-body {
  padding: 10px;
  background: var(--win-bg);
  height: 100%;
  color: black;
  font-family: 'Tahoma', sans-serif;
}
.stat-block {
  margin-bottom: 10px;
  border-bottom: 1px solid white;
  padding-bottom: 5px;
}
.label { font-size: 10px; color: #444; font-weight: bold; }
.value { font-size: 18px; color: black; font-weight: bold; font-family: 'Courier New'; }

.chart-box { margin-top: 10px; }
.bar-chart {
  margin-top: 5px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.bar-group { display: flex; align-items: center; gap: 5px; font-size: 9px; }
.bar { height: 10px; border: 1px solid rgba(0,0,0,0.5); }
.bar.optimal { background: #00ff9d; }
.bar.warning { background: #ffff00; }
.bar.critical { background: #ff0000; }
</style>
