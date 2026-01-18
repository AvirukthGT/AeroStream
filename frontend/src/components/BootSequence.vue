<script setup>
import { ref, onMounted } from 'vue';

const emit = defineEmits(['complete']);
const lines = ref([]);
const bootText = [
  "AEROSTREAM BIOS v1.0.4",
  "Copyright (C) 2026 Deepmind Corp.",
  " ",
  "CPU 0: DETECTED [OK]",
  "CPU 1: DETECTED [OK]",
  "MEMORY TEST: 640K OK",
  "Initializing Video Adapter... DONE",
  "Loading Satellite Link... ESTABLISHED",
  "Connecting to Render Backend... CONNECTED",
  "Decrypting Flight Data Stream...",
  " ",
  "System Ready."
];

onMounted(async () => {
  for (const line of bootText) {
    await new Promise(r => setTimeout(r, Math.random() * 300 + 100));
    lines.value.push(line);
  }
  await new Promise(r => setTimeout(r, 800));
  emit('complete');
});
</script>

<template>
  <div class="boot-screen">
    <div class="boot-content">
      <div v-for="(line, i) in lines" :key="i" class="boot-line">{{ line }}</div>
      <div class="cursor">_</div>
    </div>
  </div>
</template>

<style scoped>
.boot-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: black;
  color: #00ff00;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  padding: 40px;
  z-index: 9999;
  overflow: hidden;
}

.boot-line {
  margin-bottom: 5px;
  text-shadow: 0 0 5px #00ff00;
}

.cursor {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
