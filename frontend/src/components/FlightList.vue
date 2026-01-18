<script setup>
defineProps({
  flights: {
    type: Array,
    default: () => []
  },
  selectedId: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['select-flight']);

const getDisplayName = (flight) => {
  if (flight.callsign && flight.callsign.trim().length > 0) {
    return flight.callsign;
  }
  return flight.icao24 ? flight.icao24.toUpperCase() : 'UNKNOWN';
};
</script>

<template>
  <div class="flight-list">
    <div 
      v-for="flight in flights" 
      :key="flight.icao24"
      class="flight-item"
      :class="{ 
        'selected': flight.icao24 === selectedId,
        'critical': flight.efficiency_score < 70, 
        'warning': flight.efficiency_score >= 70 && flight.efficiency_score < 90 
      }"
      @click="emit('select-flight', flight)"
    >
      <div class="flight-info">
        <span class="callsign">{{ getDisplayName(flight) }}</span>
        <span class="route">{{ flight.origin_country }}</span>
      </div>
      <div class="flight-score">
        {{ Math.round(flight.efficiency_score) }}%
      </div>
    </div>
  </div>
</template>

<style scoped>
.flight-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 5px;
  overflow-y: auto; /* Allow scroll within this panel only */
  flex: 1; /* Fill height */
  height: 100%;
}

.flight-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.flight-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-left-color: var(--accent);
}

.flight-item.selected {
  background-color: #000080;
  color: white;
}

.flight-item.selected .callsign,
.flight-item.selected .route,
.flight-item.selected .flight-score {
  color: white;
}

.flight-item.critical {
  border-left: 3px solid var(--danger);
}
.flight-item.critical .flight-score {
  color: var(--danger);
  text-shadow: 0 0 5px var(--danger);
}

.flight-item.warning {
  border-left: 3px solid var(--warning);
}

.callsign {
  display: block;
  font-family: var(--font-tech);
  font-weight: bold;
  color: var(--text-main);
}

.route {
  font-size: 0.8rem;
  color: var(--text-dim);
}

.flight-score {
  font-family: var(--font-tech);
  font-size: 1.2rem;
  font-weight: bold;
}
</style>
