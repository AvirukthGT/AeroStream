<script setup>
import { computed, ref, watch } from 'vue';

const props = defineProps({
  flights: {
    type: Array,
    default: () => []
  },
  selectedId: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['select-flight', 'filter-update']);

// --- Dictionary: IATA Code (2-letter) -> Airline Name ---
const airlineMap = {
    // 🇦🇺 Domestic / Major Australian
    "QF": "Qantas",
    "VA": "Virgin Australia",
    "JQ": "Jetstar",
    "ZL": "Rex (Regional Express)",
    "QQ": "Alliance Airlines",
    "TL": "Airnorth",
    
    // 🇳🇿 New Zealand & Pacific
    "NZ": "Air New Zealand",
    "FJ": "Fiji Airways",
    "NF": "Air Vanuatu",
    "SB": "Aircalin",
    "PX": "Air Niugini",
    
    // 🌏 Asia
    "SQ": "Singapore Airlines",
    "TR": "Scoot",
    "CX": "Cathay Pacific",
    "MH": "Malaysia Airlines",
    "D7": "AirAsia X",
    "OD": "Batik Air Malaysia",
    "TG": "Thai Airways",
    "GA": "Garuda Indonesia",
    "VN": "Vietnam Airlines",
    "PR": "Philippine Airlines",
    "JL": "Japan Airlines",
    "NH": "All Nippon Airways (ANA)",
    "KE": "Korean Air",
    "OZ": "Asiana Airlines",
    "CI": "China Airlines",
    "BR": "EVA Air",
    "CA": "Air China",
    "CZ": "China Southern",
    "MU": "China Eastern",
    "AI": "Air India",
    "UL": "SriLankan Airlines",
    
    // 🕌 Middle East
    "EK": "Emirates",
    "QR": "Qatar Airways",
    "EY": "Etihad Airways",
    
    // 🇺🇸 North America
    "UA": "United Airlines",
    "AA": "American Airlines",
    "DL": "Delta Air Lines",
    "AC": "Air Canada",
    "HA": "Hawaiian Airlines",
    
    // 🇪🇺 Europe
    "BA": "British Airways",
    
    // 🇨🇱 South America
    "LA": "LATAM Airlines"
};

// --- Filters ---
const searchQuery = ref('');
const filterStatus = ref('ALL'); // ALL, AIR, GND
const filterAirline = ref('');   // 2-letter code

const getDisplayName = (flight) => {
  if (flight.callsign && flight.callsign.trim().length > 0) {
    return flight.callsign;
  }
  return flight.icao24 ? flight.icao24.toUpperCase() : 'UNKNOWN';
};

const getStatusLabel = (flight) => {
  const alt = flight.baro_altitude || 0;
  if (alt <= 100) return ':: GND_MOD ::';
  return ':: AIR_OPS ::';
};

const filteredFlights = computed(() => {
  return props.flights.filter(f => {
    // 1. Status Filter
    const isGround = (f.baro_altitude || 0) <= 100;
    if (filterStatus.value === 'GND' && !isGround) return false;
    if (filterStatus.value === 'AIR' && isGround) return false;

    // 2. Airline Filter (First 2 chars)
    if (filterAirline.value) {
      const cs = f.callsign || '';
      if (!cs.toUpperCase().startsWith(filterAirline.value)) return false;
    }

    // 3. Search Filter
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase();
      const name = (f.callsign || '').toLowerCase();
      const icao = (f.icao24 || '').toLowerCase();
      if (!name.includes(q) && !icao.includes(q)) return false;
    }

    return true;
  });
});

// Emit filtered results back to parent (for Map sync)
watch(filteredFlights, (newVal) => {
  console.log('FlightList emitting filtered flights:', newVal.length);
  emit('filter-update', newVal);
}, { immediate: true });
</script>

<template>
  <div class="flight-list-container">
    <!-- FILTER BAR -->
    <div class="filter-bar inset-panel">
       <div class="filter-row">
          <input type="text" v-model="searchQuery" placeholder="Search Callsign / ID..." class="search-input" />
          <div class="status-toggles">
             <button :class="{ active: filterStatus === 'ALL' }" @click="filterStatus = 'ALL'">ALL</button>
             <button :class="{ active: filterStatus === 'AIR' }" @click="filterStatus = 'AIR'">AIR</button>
             <button :class="{ active: filterStatus === 'GND' }" @click="filterStatus = 'GND'">GND</button>
          </div>
       </div>
       <div class="filter-row">
          <select v-model="filterAirline" class="airline-select">
             <option value="">-- All Airlines --</option>
             <option v-for="(name, code) in airlineMap" :key="code" :value="code">
                {{ code }} - {{ name }}
             </option>
          </select>
       </div>
    </div>

    <div class="flight-list">
      <div 
        v-for="flight in filteredFlights" 
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
          <span class="route">{{ flight.origin_country }} <span style="color:var(--accent); font-size:9px;">{{ getStatusLabel(flight) }}</span></span>
        </div>
        <div class="flight-score">
          {{ Math.round(flight.efficiency_score) }}%
        </div>
      </div>
      <div v-if="filteredFlights.length === 0" class="no-results">
         No flights found matching filters.
      </div>
    </div>
  </div>
</template>

<style scoped>
.flight-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.filter-bar {
  padding: 4px;
  background: var(--win-bg);
  margin-bottom: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-row {
  display: flex;
  gap: 4px;
}

.search-input {
  flex: 1;
  font-family: 'Tahoma', sans-serif;
  font-size: 11px;
  padding: 2px;
  border: 1px inset white;
}

.status-toggles {
  display: flex;
  gap: 0;
}

.status-toggles button {
  font-size: 9px;
  padding: 2px 4px;
  border: 1px outset white;
  background: #c0c0c0;
  cursor: pointer;
  min-width: 30px;
}

.status-toggles button.active {
  background: #000080;
  color: white;
  border-style: inset;
}

.airline-select {
  width: 100%;
  font-family: 'Tahoma', sans-serif;
  font-size: 11px;
}

.flight-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 5px;
  overflow-y: auto; /* Allow scroll within this panel only */
  flex: 1; /* Fill height */
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

.no-results {
  text-align: center;
  color: #808080;
  padding: 10px;
  font-style: italic;
}
</style>
