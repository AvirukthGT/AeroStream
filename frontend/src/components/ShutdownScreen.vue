<script setup>
import { ref, onMounted } from 'vue';

const emit = defineEmits(['reboot']);

const progress = ref(0);
const isPoweredOff = ref(false);

onMounted(() => {
  const duration = 2000; // 2 seconds shutdown
  const intervalTime = 20;
  const step = 100 / (duration / intervalTime);

  const timer = setInterval(() => {
    progress.value += step;
    if (progress.value >= 100) {
      progress.value = 100;
      clearInterval(timer);
      setTimeout(() => {
        isPoweredOff.value = true;
      }, 500);
    }
  }, intervalTime);
});
</script>

<template>
  <div class="shutdown-overlay" :class="{ 'powered-off': isPoweredOff }">
    <!-- Shutting Down State -->
    <div v-if="!isPoweredOff" class="shutdown-content">
       <div class="logo">AEROSTREAM</div>
       <div class="status-text">Shutting Down System Services...</div>
       <div class="progress-bar-frame">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
       </div>
    </div>

    <!-- Powered Off State -->
    <div v-else class="off-content">
       <button class="power-btn" @click="emit('reboot')" title="Power On">
          ⏻
       </button>
       <div class="hint">System Halted. Press Power to Reboot.</div>
    </div>
  </div>
</template>

<style scoped>
.shutdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 10000;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px); /* Blur effect */
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: 'Tahoma', sans-serif;
  transition: background 0.5s;
}

.shutdown-overlay.powered-off {
  background: black;
  backdrop-filter: none;
}

/* Shutdown UI */
.shutdown-content {
  text-align: center;
  background: #d4d0c8;
  color: black;
  padding: 20px;
  border: 2px solid;
  border-color: white #808080 #808080 white;
  box-shadow: 4px 4px 10px rgba(0,0,0,0.5);
  width: 300px;
}

.logo { font-weight: bold; font-size: 18px; margin-bottom: 15px; color: #000080; }
.status-text { font-size: 12px; margin-bottom: 10px; }

.progress-bar-frame {
  height: 20px;
  border: 1px solid #808080;
  background: white;
  padding: 2px;
  display: flex;
  align-items: center;
}
.progress-fill {
  height: 100%;
  background: navy;
  transition: width 0.1s linear;
}

/* Off UI */
.off-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.power-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 2px solid #333;
  background: #111;
  color: #333;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 10px rgba(0,0,0,0.5);
  transition: all 0.2s;
}

.power-btn:hover {
  color: #00ff00;
  border-color: #00ff00;
  box-shadow: 0 0 20px #00ff00;
  text-shadow: 0 0 10px #00ff00;
}

.hint { color: #333; font-size: 10px; font-family: 'Courier New'; }
</style>
