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
      <div id="status" v-if="isProcessing || processComplete || processError">
        <p>{{ outputMessage }}</p>
        <div class="loading-spinner" v-if="isProcessing"></div>

        <!-- Error Display -->
        <div v-if="processError" class="error-container">
          <div class="error-icon">⚠️</div>
          <div class="error-details">
            <h4>{{ errorTitle }}</h4>
            <p>{{ errorMessage }}</p>
            <div class="error-actions">
              <button
                @click="retryConnection"
                class="retry-btn"
                :disabled="isRetrying"
              >
                {{ isRetrying ? "🔄 Retrying..." : "🔄 Retry Connection" }}
              </button>
              <button
                @click="checkBackendStatus"
                class="check-btn"
                :disabled="isCheckingBackend"
              >
                {{ isCheckingBackend ? "🔍 Checking..." : "🔍 Check Backend" }}
              </button>
            </div>
          </div>
        </div>
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
import { API_CONFIG, getApiUrl } from "../config.js";

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
const isRetrying = ref(false);
const isCheckingBackend = ref(false);
const errorTitle = ref("");
const errorMessage = ref("");

const resetState = () => {
  statusMessage.value = "Starting YOLO fire detection...";
  outputMessage.value = "🔄 Initializing camera and loading model...";
  isProcessing.value = false;
  processComplete.value = false;
  processError.value = false;
  isStopping.value = false;
  isRetrying.value = false;
  isCheckingBackend.value = false;
  errorTitle.value = "";
  errorMessage.value = "";
};

const setError = (title, message, output) => {
  errorTitle.value = title;
  errorMessage.value = message;
  outputMessage.value = output;
  processError.value = true;
  isProcessing.value = false;
};

const checkBackendStatus = async () => {
  isCheckingBackend.value = true;

  try {
    const healthCheckUrl = getApiUrl(API_CONFIG.ENDPOINTS.HEALTH);
    const response = await fetch(healthCheckUrl, {
      method: "GET",
      timeout: 5000,
    });

    if (response.ok) {
      const healthData = await response.json();
      outputMessage.value = "✅ Backend is running successfully!";

      if (!healthData.model_available) {
        errorMessage.value =
          "Backend is accessible, but the YOLO model file is missing.";
      } else if (!healthData.camera_accessible) {
        errorMessage.value =
          "Backend is accessible, but camera access is not available.";
      } else {
        errorMessage.value =
          "Backend and all components are accessible. The issue might be temporary.";
      }
    } else {
      setError(
        "Backend Service Error",
        `Backend responded with status ${response.status}. The server might be experiencing issues.`,
        `❌ Backend check failed: HTTP ${response.status}`
      );
    }
  } catch (error) {
    if (error.name === "TypeError" && error.message.includes("fetch")) {
      setError(
        "Backend Connection Failed",
        "Cannot reach the backend server. Please ensure the server is running and accessible.",
        "❌ Backend is not reachable. Check if the server is running."
      );
    } else {
      setError(
        "Network Error",
        `Failed to connect to backend: ${error.message}`,
        `❌ Network error: ${error.message}`
      );
    }
  } finally {
    isCheckingBackend.value = false;
  }
};

const retryConnection = async () => {
  isRetrying.value = true;
  processError.value = false;

  // Wait a moment before retrying
  await new Promise((resolve) => setTimeout(resolve, 1000));

  await runYoloDetection();
  isRetrying.value = false;
};

const runYoloDetection = async () => {
  isProcessing.value = true;
  processComplete.value = false;
  processError.value = false;

  try {
    // First check if camera is available
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        // Stop the test stream immediately
        stream.getTracks().forEach((track) => track.stop());
      } catch (cameraError) {
        setError(
          "Camera Access Denied",
          "Cannot access your camera. Please ensure camera permissions are granted and no other application is using the camera.",
          `❌ Camera Error: ${cameraError.message}`
        );
        return;
      }
    } else {
      setError(
        "Camera Not Supported",
        "Your browser doesn't support camera access or you're not using HTTPS.",
        "❌ Camera access not available in this browser"
      );
      return;
    }

    const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.RUN_YOLO), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "models/best_nano_111.pt",
        source: 0,
        conf: 0.35,
        iou: 0.1,
        show: true,
      }),
      timeout: 10000, // 10 second timeout
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      if (response.status === 503) {
        setError(
          "Service Unavailable",
          "The backend service is temporarily unavailable. This might be due to the model loading or system resources.",
          `❌ Service unavailable: ${errorData.message || response.statusText}`
        );
      } else if (response.status === 500) {
        setError(
          "Server Error",
          "Internal server error occurred. This might be due to YOLO model issues or camera access problems on the server.",
          `❌ Server error: ${errorData.message || response.statusText}`
        );
      } else if (response.status === 404) {
        setError(
          "Endpoint Not Found",
          "The detection endpoint was not found. The backend might be running an older version.",
          `❌ Endpoint not found: ${response.status}`
        );
      } else {
        setError(
          "Backend Error",
          `Backend responded with an error: ${
            errorData.message || response.statusText
          }`,
          `❌ Error: ${errorData.message || response.statusText}`
        );
      }
      return;
    }

    const result = await response.json();
    outputMessage.value = `✅ ${result.message}`;
    statusMessage.value =
      "A new window should open showing your camera feed with fire detection.";
    processComplete.value = true;
  } catch (error) {
    if (error.name === "AbortError" || error.message.includes("timeout")) {
      setError(
        "Connection Timeout",
        "The request timed out. The backend might be slow to respond or not running.",
        "❌ Connection timeout - backend might be starting up or not running"
      );
    } else if (error.name === "TypeError" && error.message.includes("fetch")) {
      setError(
        "Network Connection Failed",
        "Cannot connect to the backend server. Please check if the server is running and your internet connection.",
        "❌ Network error - cannot reach backend server"
      );
    } else {
      setError(
        "Unexpected Error",
        `An unexpected error occurred: ${error.message}`,
        `❌ Unexpected error: ${error.message}`
      );
    }
  } finally {
    isProcessing.value = false;
  }
};

const stopDetection = async () => {
  isStopping.value = true;

  try {
    const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.STOP_YOLO), {
      method: "POST",
      timeout: 5000,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    outputMessage.value = `🛑 ${result.message}`;
    processComplete.value = false;
  } catch (error) {
    if (error.name === "TypeError" && error.message.includes("fetch")) {
      outputMessage.value = "❌ Cannot reach backend to stop detection";
    } else {
      outputMessage.value = `❌ Error stopping detection: ${error.message}`;
    }
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

/* Error handling styles */
.error-container {
  background: #fff5f5;
  border: 2px solid #fed7d7;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  box-shadow: 0 4px 6px rgba(254, 215, 215, 0.25);
}

.error-icon {
  font-size: 2rem;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.error-details {
  flex: 1;
}

.error-details h4 {
  color: #c53030;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.error-details p {
  color: #742a2a;
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.retry-btn,
.check-btn {
  background: #e53e3e;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 36px;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.retry-btn:hover,
.check-btn:hover {
  background: #c53030;
  transform: translateY(-1px);
}

.retry-btn:disabled,
.check-btn:disabled {
  background: #a0aec0;
  cursor: not-allowed;
  transform: none;
}

.check-btn {
  background: #3182ce;
}

.check-btn:hover {
  background: #2b77cb;
}

.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 1rem auto;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .error-container {
    padding: 1rem;
    margin: 0.5rem 0;
    flex-direction: column;
    text-align: center;
  }

  .error-icon {
    font-size: 1.5rem;
    margin: 0;
  }

  .error-actions {
    justify-content: center;
  }

  .retry-btn,
  .check-btn {
    flex: 1;
    min-width: 120px;
    padding: 0.6rem 1rem;
  }
}
</style>
