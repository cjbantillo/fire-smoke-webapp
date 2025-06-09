<template>
  <div
    class="modal"
    :class="{ active: isVisible }"
    @click="handleBackdropClick"
  >
    <div class="modal-content">
      <span class="close-button" @click="$emit('close')">&times;</span>
      <h2>🎥 Live Camera Detection</h2>
      <p>{{ statusMessage }}</p>
      <p>
        <strong>Command:</strong>
        <code
          >yolo detect predict model=models/best_nano_111.pt source=0 conf=0.35
          iou=0.1 show=True</code
        >
      </p>

      <div id="status" v-if="isProcessing || processComplete">
        <p>{{ outputMessage }}</p>
        <div class="loading-spinner" v-if="isProcessing"></div>
      </div>

      <div class="modal-buttons" v-if="processComplete && !processError">
        <button class="stop-btn" @click="stopDetection" :disabled="isStopping">
          🛑 {{ isStopping ? "Stopping..." : "Stop Detection" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close"]);

const statusMessage = ref("Starting YOLO fire detection...");
const outputMessage = ref("🔄 Initializing camera and loading model...");
const isProcessing = ref(false);
const processComplete = ref(false);
const processError = ref(false);
const isStopping = ref(false);

const resetState = () => {
  statusMessage.value = "Starting YOLO fire detection...";
  outputMessage.value = "🔄 Initializing camera and loading model...";
  isProcessing.value = false;
  processComplete.value = false;
  processError.value = false;
  isStopping.value = false;
};

const runYoloDetection = async () => {
  isProcessing.value = true;
  processComplete.value = false;
  processError.value = false;

  try {
    const response = await fetch("/run-yolo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "models/best_nano_111.pt",
        source: 0,
        conf: 0.35,
        iou: 0.1,
        show: true,
      }),
    });

    const result = await response.json();

    if (response.ok) {
      outputMessage.value = `✅ ${result.message}`;
      statusMessage.value =
        "A new window should open showing your camera feed with fire detection.";
      processComplete.value = true;
    } else {
      outputMessage.value = `❌ Error: ${
        result.message || response.statusText
      }`;
      processError.value = true;
    }
  } catch (error) {
    outputMessage.value = `❌ Connection Error: ${error.message}. Make sure the server is running!`;
    processError.value = true;
  } finally {
    isProcessing.value = false;
  }
};

const stopDetection = async () => {
  isStopping.value = true;

  try {
    const response = await fetch("/stop-yolo", { method: "POST" });
    const result = await response.json();
    outputMessage.value = `🛑 ${result.message}`;
    processComplete.value = false;
  } catch (error) {
    outputMessage.value = `❌ Error stopping detection: ${error.message}`;
  } finally {
    isStopping.value = false;
  }
};

const handleBackdropClick = (event) => {
  if (event.target === event.currentTarget) {
    emit("close");
  }
};

// Watch for modal visibility changes
watch(
  () => props.isVisible,
  (newValue) => {
    if (newValue) {
      resetState();
      runYoloDetection();
    }
  }
);
</script>

<style scoped>
/* Mobile-friendly modal styles */
.modal-content {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 1rem;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 15px;
  z-index: 1001;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  color: #aaa;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-button:hover {
  background: rgba(255, 107, 53, 0.2);
  color: #ff6b35;
}

@media (max-width: 768px) {
  .close-button {
    width: 35px;
    height: 35px;
    font-size: 20px;
    top: 5px;
    right: 10px;
  }
}

/* Touch-friendly button styling */
.stop-btn {
  min-height: 44px; /* iOS recommended touch target size */
  min-width: 120px;
  touch-action: manipulation; /* Prevent double-tap zoom */
}

@media (hover: none) {
  .stop-btn:active {
    transform: scale(0.95);
    background-color: #c82333;
  }
}
</style>
