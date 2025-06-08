<script setup>
import { ref } from 'vue'
</script>

<template>
  <div>
    <h1>Fire Smoke Web App 🔥</h1>
    <h3>This is a simple web application to demonstrate fire-smoke-detection</h3>
    <br>
    <h>Credits to the creator: Sayed Gamal</h>
    <p>https://github.com/sayedgamal99/Real-Time-Smoke-Fire-Detection-YOLO11</p>
    <br>
    <p>Current time: {{ new Date().toLocaleTimeString() }}</p>
    <button>Click to run Live Camera</button>
  </div>
</template>

<style scoped></style>
