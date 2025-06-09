<template>
  <div class="time">Current time: {{ formattedTime }}</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const formattedTime = ref("");
let timeInterval = null;

const updateTime = () => {
  const now = new Date();
  const options = {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  };
  formattedTime.value = now.toLocaleTimeString([], options);
};

onMounted(() => {
  updateTime(); // Initial call
  timeInterval = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval);
  }
});
</script>
