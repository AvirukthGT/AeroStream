<script setup>
import { onMounted, ref, watch } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Props: flights list
const props = defineProps({
  flights: {
    type: Array,
    default: () => []
  },
  selectedFlightId: {
    type: String,
    default: null
  },
  tileUrl: {
    type: String,
    default: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
  }
});

const emit = defineEmits(['select-flight']);

const mapContainer = ref(null);
let map = null;
let markers = L.layerGroup();
let tileLayer = null;

// Custom Icons
const createIcon = (color, rotation) => {
  // ... (same as before) ...
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" width="24" height="24" style="transform: rotate(${rotation}deg); filter: drop-shadow(0 0 5px ${color});">
      <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
    </svg>
  `;
  return L.divIcon({
    html: svg,
    className: 'plane-icon',
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });
};

onMounted(() => {
  // Initialize Map centered on Australia
  map = L.map(mapContainer.value, {
    zoomControl: false,
    attributionControl: false
  }).setView([-25.2744, 133.7751], 4);

  // Initial Tile Layer
  tileLayer = L.tileLayer(props.tileUrl, {
    maxZoom: 19
  }).addTo(map);

  markers.addTo(map);
});

// Watch Tile URL for Theme changes
watch(() => props.tileUrl, (newUrl) => {
  if (map && tileLayer) {
    map.removeLayer(tileLayer);
    tileLayer = L.tileLayer(newUrl, { maxZoom: 19 }).addTo(map);
    tileLayer.bringToBack(); // Ensure markers stay on top
  }
});

// Watch flights prop to update markers
watch(() => props.flights, (newFlights) => {
  if (!map) return;
  
  markers.clearLayers();
  
  newFlights.forEach(flight => {
    // Determine color based on efficiency
    let color;
    if (flight.status === 'Inefficient') {
      color = '#ff2a2a'; // Neon Red
    } else if (flight.status === 'Optimal') {
      color = '#00ff9d'; // Neon Green
    } else {
      color = '#4a4a4a'; // Grey for Raw Data
    }
    
    const heading = flight.plane_heading || 0; 
    
    // Z-Index: Put analyzed flights on top
    const zIndexOffset = flight.status === 'Raw' ? 0 : 1000;

    const marker = L.marker([flight.latitude || -25, flight.longitude || 133], { 
      icon: createIcon(color, heading),
      zIndexOffset: zIndexOffset
    });

    marker.on('click', () => {
      emit('select-flight', flight);
    });

    markers.addLayer(marker);
  });
}, { deep: true });

</script>

<template>
  <div ref="mapContainer" class="map-container"></div>
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  background: #000;
}
</style>
