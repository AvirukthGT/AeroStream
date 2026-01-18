<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  flights: Array
});

const logs = ref([]);
const maxLogs = 50;
let interval = null;

const addLog = (msg, type = 'INFO') => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false });
  logs.value.unshift({ time, type, msg });
  if (logs.value.length > maxLogs) logs.value.pop();
};

const generateTraffic = () => {
  if (props.flights.length === 0) return;
  const randomFlight = props.flights[Math.floor(Math.random() * props.flights.length)];
  const actions = [
    `Handshake established: ${randomFlight.icao24}`,
    `Telemetry update: ${randomFlight.callsign || 'UNK'} [Alt: ${randomFlight.baro_altitude || 0}]`,
    `Vector check: Heading ${randomFlight.plane_heading || 0}°`,
    `Packet received: ${Math.floor(Math.random() * 9999)} bytes`,
    `Decrypting transponder signal... OK`
  ];
  addLog(actions[Math.floor(Math.random() * actions.length)], 'DATA');
};

onMounted(() => {
  addLog('System Log Service Started', 'SYS');
  interval = setInterval(generateTraffic, 800);
});

onUnmounted(() => {
  clearInterval(interval);
});
</script>

<template>
  <div class="terminal-body">
    <div v-for="(log, i) in logs" :key="i" class="log-line">
      <span class="timestamp">[{{ log.time }}]</span>
      <span class="type" :class="log.type">[{{ log.type }}]</span>
      <span class="msg">{{ log.msg }}</span>
    </div>
  </div>
</template>

<style scoped>
.terminal-body {
  background: black;
  color: #00ff00;
  font-family: 'Courier New', Courier, monospace;
  font-size: 11px;
  padding: 5px;
  height: 100%;
  overflow-y: hidden; /* Auto scroll effect via unshift? User reads top down? */
  /* Actually unshift pushes new to top. So overflow-y hidden fits static view. */
}
.log-line {
  display: flex;
  gap: 5px;
  margin-bottom: 2px;
}
.timestamp { color: #888; }
.type.INFO { color: #00ff00; }
.type.DATA { color: #00ffff; }
.type.SYS { color: #ffff00; }
</style>
