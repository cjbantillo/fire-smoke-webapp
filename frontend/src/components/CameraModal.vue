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

      <!-- <p v-if="!useBrowserCamera">
        <strong>Command:</strong>
        <code
          >yolo detect predict model=models/best_nano_111.pt source=0 conf=0.35
          iou=0.1 show=True</code
        >
      </p> -->
      <!-- Browser Camera Section -->
      <div v-if="useBrowserCamera" class="camera-section">
        <div class="camera-container">
          <video
            ref="videoRef"
            autoplay
            muted
            playsinline
            :class="{ 'camera-active': cameraActive }"
          ></video>
          <canvas ref="canvasRef" style="display: none"></canvas>

          <!-- Enhanced Detection Overlays with Color Coding -->
          <div class="detection-overlay" v-if="detections.length > 0">
            <div
              v-for="(detection, index) in detections"
              :key="index"
              class="detection-box"
              :class="getDetectionClass(detection.class)"
              :style="getDetectionBoxStyle(detection.bbox, detection.class)"
            >
              <div
                class="detection-label"
                :class="getDetectionLabelClass(detection.class)"
              >
                {{ detection.class }} ({{
                  Math.round(detection.confidence * 100)
                }}%)
              </div>
            </div>
          </div>

          <!-- Performance Indicator -->
          <div class="performance-indicator" v-if="detectionActive">
            <div class="indicator-dot" :class="getPerformanceClass()"></div>
            <span class="indicator-text">{{ getPerformanceText() }}</span>
          </div>
        </div>

        <div class="camera-controls">
          <div class="primary-controls">
            <button
              @click="toggleCamera"
              class="camera-btn"
              :disabled="isProcessing"
            >
              {{ cameraActive ? "📹 Stop Camera" : "📷 Start Camera" }}
            </button>

            <button
              @click="toggleDetection"
              class="detection-btn"
              :disabled="!cameraActive"
              :class="{ active: detectionActive }"
            >
              {{ detectionActive ? "🛑 Stop Detection" : "🔍 Start Detection" }}
            </button>
          </div>

          <!-- Mobile Camera Controls -->
          <div class="mobile-controls" v-if="isMobile && cameraActive">
            <button
              @click="switchCamera"
              class="switch-camera-btn"
              :disabled="!canSwitchCamera || isProcessing"
            >
              🔄 Switch Camera
            </button>
            <div class="camera-info">
              <span class="camera-facing">{{
                currentFacingMode === "user" ? "🤳 Front" : "📷 Back"
              }}</span>
            </div>
          </div>
          <!-- Quality Controls -->
          <div class="quality-controls" v-if="cameraActive">
            <label>Quality:</label>
            <select
              v-model="selectedQuality"
              @change="adjustQuality"
              class="quality-select"
            >
              <option value="ultra" v-if="supports1080p">Ultra (1080p)</option>
              <option value="high">High (720p)</option>
              <option value="medium">Medium (480p)</option>
              <option value="low">Low (360p)</option>
              <option value="auto">Auto</option>
            </select>
          </div>
        </div>

        <!-- Enhanced Detection Stats -->
        <div v-if="detectionActive" class="detection-stats">
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-icon">🔥</span>
              <span class="stat-label">Fire:</span>
              <span class="stat-value">{{ getDetectionCount("fire") }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-icon">💨</span>
              <span class="stat-label">Smoke:</span>
              <span class="stat-value">{{ getDetectionCount("smoke") }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-icon">📊</span>
              <span class="stat-label">FPS:</span>
              <span class="stat-value">{{ Math.round(fps) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-icon">⏱️</span>
              <span class="stat-label">Latency:</span>
              <span class="stat-value">{{ processingTime }}ms</span>
            </div>
            <div class="stat-item">
              <span class="stat-icon">🔍</span>
              <span class="stat-label">Total:</span>
              <span class="stat-value">{{ totalDetections }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-icon">⚡</span>
              <span class="stat-label">Performance:</span>
              <span class="stat-value">{{ getPerformanceText() }}</span>
            </div>
          </div>
        </div>
      </div>

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

      <div
        class="modal-buttons"
        v-if="processComplete && !processError && !useBrowserCamera"
      >
        <button class="stop-btn" @click="stopDetection" :disabled="isStopping">
          🛑 {{ isStopping ? "Stopping..." : "Stop Detection" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from "vue";
import { API_CONFIG, getApiUrl } from "../config.js";

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close"]);

// Existing state
const statusMessage = ref("Starting YOLO fire detection...");
const outputMessage = ref("🔄 Initializing detection system...");
const isProcessing = ref(false);
const processComplete = ref(false);
const processError = ref(false);
const isStopping = ref(false);
const isRetrying = ref(false);
const isCheckingBackend = ref(false);
const errorTitle = ref("");
const errorMessage = ref("");

const useBrowserCamera = ref(true);
const cameraActive = ref(false);
const detectionActive = ref(false);
const videoRef = ref(null);
const canvasRef = ref(null);
const detections = ref([]);
const fps = ref(0);
const processingTime = ref(0);

// Enhanced state for mobile and advanced features
const isMobileDevice = ref(false);
const currentCameraFacing = ref("environment"); // "user" for front, "environment" for back
const availableCameras = ref([]);
const performanceMode = ref("balanced"); // "high", "balanced", "low"
const detectionStats = ref({
  totalDetections: 0,
  fireDetections: 0,
  smokeDetections: 0,
  avgConfidence: 0,
  maxConfidence: 0,
  sessionsRunning: 0,
});

// Camera stream and detection intervals
let mediaStream = null;
let detectionInterval = null;
let fpsInterval = null;
let frameCount = 0;
let lastTime = Date.now();
let adaptiveFrameSkip = 0;
let performanceCounter = 0;

const resetState = () => {
  statusMessage.value = "Starting YOLO fire detection...";
  outputMessage.value = "🔄 Initializing detection system...";
  isProcessing.value = false;
  processComplete.value = false;
  processError.value = false;
  isStopping.value = false;
  isRetrying.value = false;
  isCheckingBackend.value = false;
  errorTitle.value = "";
  errorMessage.value = "";
  detections.value = [];
  fps.value = 0;
  processingTime.value = 0;
};

const setError = (title, message, output) => {
  errorTitle.value = title;
  errorMessage.value = message;
  outputMessage.value = output;
  processError.value = true;
  isProcessing.value = false;
};

const toggleDetectionMode = () => {
  useBrowserCamera.value = !useBrowserCamera.value;

  // Clean up camera if switching away
  if (!useBrowserCamera.value && cameraActive.value) {
    stopCamera();
  }
};

const toggleCamera = async () => {
  if (cameraActive.value) {
    stopCamera();
  } else {
    await startCamera();
  }
};

const startCamera = async () => {
  try {
    const performanceSettings = getPerformanceSettings();

    const constraints = {
      video: {
        width: { ideal: performanceSettings.width },
        height: { ideal: performanceSettings.height },
        facingMode: currentCameraFacing.value,
        frameRate: { ideal: isMobileDevice.value ? 15 : 30 },
      },
    };

    mediaStream = await navigator.mediaDevices.getUserMedia(constraints);

    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream;
      cameraActive.value = true;
      outputMessage.value = "✅ Camera started successfully";

      // Initialize mobile detection on first camera start
      if (!isMobile.value) {
        isMobile.value = detectMobileDevice();
      }
    }
  } catch (error) {
    setError(
      "Camera Access Failed",
      `Cannot access camera: ${error.message}`,
      "❌ Camera access denied or not available"
    );
  }
};

const stopCamera = () => {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }

  if (detectionActive.value) {
    stopDetection();
  }

  cameraActive.value = false;
  detections.value = [];
  outputMessage.value = "📷 Camera stopped";
};

const toggleDetection = () => {
  if (detectionActive.value) {
    stopFrameDetection();
  } else {
    startFrameDetection();
  }
};

const startFrameDetection = () => {
  if (!cameraActive.value) return;

  detectionActive.value = true;
  frameCount = 0;
  lastTime = Date.now();

  // Reset detection statistics
  detectionStats.value = {
    totalDetections: 0,
    fireDetections: 0,
    smokeDetections: 0,
    avgConfidence: 0,
    maxConfidence: 0,
    sessionsRunning: detectionStats.value.sessionsRunning + 1,
  };

  // Get adaptive performance settings
  const performanceSettings = getPerformanceSettings();

  // Start detection interval with adaptive timing
  detectionInterval = setInterval(
    processCurrentFrame,
    performanceSettings.interval
  );

  // Start FPS counter
  fpsInterval = setInterval(() => {
    const currentTime = Date.now();
    const elapsed = (currentTime - lastTime) / 1000;
    fps.value = frameCount / elapsed;
    frameCount = 0;
    lastTime = currentTime;
  }, 1000);

  outputMessage.value =
    "🔍 Real-time detection started with adaptive performance";
};

const stopFrameDetection = () => {
  if (detectionInterval) {
    clearInterval(detectionInterval);
    detectionInterval = null;
  }

  if (fpsInterval) {
    clearInterval(fpsInterval);
    fpsInterval = null;
  }

  detectionActive.value = false;
  detections.value = [];
  fps.value = 0;
  outputMessage.value = "🛑 Detection stopped";
};

const processCurrentFrame = async () => {
  if (!cameraActive.value || !videoRef.value || !canvasRef.value) return;

  // Adaptive frame skipping for performance
  if (adaptiveFrameSkip > 0 && frameCount % (adaptiveFrameSkip + 1) !== 0) {
    frameCount++;
    return;
  }

  const startTime = Date.now();

  try {
    // Capture frame from video
    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    const video = videoRef.value;

    const performanceSettings = getPerformanceSettings();
    canvas.width = performanceSettings.width;
    canvas.height = performanceSettings.height;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to PNG for better quality
    const imageData = canvas.toDataURL("image/png");

    // Send to backend for detection
    const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.DETECT_FRAME), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageData }),
    });

    if (response.ok) {
      const result = await response.json();
      const newDetections = result.detections || [];

      detections.value = newDetections;
      frameCount++;

      // Update detection statistics
      updateDetectionStats(newDetections);
      totalDetections.value = detectionStats.value.totalDetections;

      // Calculate processing time
      processingTime.value = Date.now() - startTime;

      // Adaptive performance adjustment
      adjustPerformanceMode();
    }
  } catch (error) {
    console.error("Frame processing error:", error);
    // Don't show error for every frame, just log it
  }
};

const getDetectionBoxStyle = (bbox) => {
  const video = videoRef.value;
  if (!video) return {};

  const videoRect = video.getBoundingClientRect();
  const scaleX = videoRect.width / video.videoWidth;
  const scaleY = videoRect.height / video.videoHeight;

  return {
    position: "absolute",
    left: `${bbox.x1 * scaleX}px`,
    top: `${bbox.y1 * scaleY}px`,
    width: `${(bbox.x2 - bbox.x1) * scaleX}px`,
    height: `${(bbox.y2 - bbox.y1) * scaleY}px`,
    border: "2px solid #ff4444",
    backgroundColor: "rgba(255, 68, 68, 0.1)",
  };
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
    setError(
      "Backend Connection Failed",
      "Cannot reach the backend server. Please ensure the server is running and accessible.",
      "❌ Backend is not reachable. Check if the server is running."
    );
  } finally {
    isCheckingBackend.value = false;
  }
};

const retryConnection = async () => {
  isRetrying.value = true;
  processError.value = false;
  await new Promise((resolve) => setTimeout(resolve, 1000));

  if (useBrowserCamera.value) {
    if (!cameraActive.value) {
      await startCamera();
    }
  } else {
    await runYoloDetection();
  }

  isRetrying.value = false;
};

const runYoloDetection = async () => {
  isProcessing.value = true;
  processComplete.value = false;
  processError.value = false;

  try {
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
      timeout: 10000,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      setError(
        "Backend Error",
        `Backend responded with an error: ${
          errorData.message || response.statusText
        }`,
        `❌ Error: ${errorData.message || response.statusText}`
      );
      return;
    }

    const result = await response.json();
    outputMessage.value = `✅ ${result.message}`;
    statusMessage.value =
      "A new window should open showing your camera feed with fire detection on desktop. For mobile, detection will run in background.";
    processComplete.value = true;
  } catch (error) {
    setError(
      "Network Connection Failed",
      "Cannot connect to the backend server. Please check if the server is running and your internet connection.",
      "❌ Network error - cannot reach backend server"
    );
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

// Mobile device detection
function detectMobileDevice() {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  const mobileRegex =
    /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i;
  const touchDevice = "ontouchstart" in window || navigator.maxTouchPoints > 0;
  const screenWidth = window.innerWidth <= 768;

  isMobileDevice.value =
    mobileRegex.test(userAgent) || touchDevice || screenWidth;
  // Adjust performance mode based on device
  if (isMobileDevice.value) {
    performanceMode.value = "balanced";
    // Don't allow ultra mode on mobile devices by default
    if (selectedQuality.value === "ultra") {
      selectedQuality.value = "high";
    }
  }

  return isMobileDevice.value;
}

// Get available cameras
async function getAvailableCameras() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const cameras = devices.filter((device) => device.kind === "videoinput");
    availableCameras.value = cameras;
    return cameras;
  } catch (error) {
    console.error("Error getting cameras:", error);
    return [];
  }
}

// Switch camera (front/back on mobile)
async function switchCamera() {
  if (!isMobileDevice.value || availableCameras.value.length < 2) {
    return;
  }

  const newFacing =
    currentCameraFacing.value === "user" ? "environment" : "user";
  currentCameraFacing.value = newFacing;

  if (cameraActive.value) {
    await stopCamera();
    await startCamera();
  }
}

// Adaptive performance adjustment
function adjustPerformanceMode() {
  performanceCounter++;

  if (performanceCounter % 30 === 0) {
    // Check every 30 frames
    const currentFps = fps.value;
    const currentProcessingTime = processingTime.value;

    if (currentFps < 10 || currentProcessingTime > 500) {
      // Performance is poor, reduce quality
      if (performanceMode.value === "ultra") {
        performanceMode.value = "high";
        adaptiveFrameSkip = 1;
      } else if (performanceMode.value === "high") {
        performanceMode.value = "balanced";
        adaptiveFrameSkip = 1;
      } else if (performanceMode.value === "balanced") {
        performanceMode.value = "low";
        adaptiveFrameSkip = 2;
      }
    } else if (currentFps > 25 && currentProcessingTime < 150) {
      // Performance is excellent, increase quality if supported
      if (
        performanceMode.value === "high" &&
        supports1080p.value &&
        !isMobileDevice.value
      ) {
        performanceMode.value = "ultra";
        adaptiveFrameSkip = 0;
      } else if (
        performanceMode.value === "balanced" &&
        !isMobileDevice.value
      ) {
        performanceMode.value = "high";
        adaptiveFrameSkip = 0;
      } else if (performanceMode.value === "low") {
        performanceMode.value = "balanced";
        adaptiveFrameSkip = 1;
      }
    } else if (currentFps > 20 && currentProcessingTime < 200) {
      // Performance is good, increase quality
      if (performanceMode.value === "low") {
        performanceMode.value = "balanced";
        adaptiveFrameSkip = 1;
      } else if (
        performanceMode.value === "balanced" &&
        !isMobileDevice.value
      ) {
        performanceMode.value = "high";
        adaptiveFrameSkip = 0;
      }
    }
  }
}

// Get performance settings based on mode
function getPerformanceSettings() {
  const settings = {
    ultra: { width: 1920, height: 1080, interval: 150 },
    high: { width: 1280, height: 720, interval: 100 },
    balanced: { width: 640, height: 480, interval: 200 },
    low: { width: 320, height: 240, interval: 500 },
  };

  return settings[performanceMode.value] || settings.balanced;
}

// Color-coded detection overlay
function drawDetections(ctx, detections, canvasWidth, canvasHeight) {
  ctx.clearRect(0, 0, canvasWidth, canvasHeight);

  detections.forEach((detection) => {
    const { x, y, width, height, confidence, class: className } = detection;

    // Scale coordinates to canvas size
    const scaledX = (x / 640) * canvasWidth;
    const scaledY = (y / 640) * canvasHeight;
    const scaledWidth = (width / 640) * canvasWidth;
    const scaledHeight = (height / 640) * canvasHeight;

    // Color coding: blue for fire, sky blue for smoke
    const colors = {
      fire: { stroke: "#0066CC", fill: "rgba(0, 102, 204, 0.2)" },
      smoke: { stroke: "#87CEEB", fill: "rgba(135, 206, 235, 0.2)" },
    };

    const color = colors[className.toLowerCase()] || colors.fire;

    // Draw bounding box
    ctx.strokeStyle = color.stroke;
    ctx.fillStyle = color.fill;
    ctx.lineWidth = 3;

    ctx.fillRect(scaledX, scaledY, scaledWidth, scaledHeight);
    ctx.strokeRect(scaledX, scaledY, scaledWidth, scaledHeight);

    // Draw label
    const label = `${className}: ${(confidence * 100).toFixed(1)}%`;
    ctx.fillStyle = color.stroke;
    ctx.font = isMobileDevice.value ? "14px Arial" : "16px Arial";
    ctx.fillText(label, scaledX, scaledY - 10);
  });
}

// Update detection statistics
function updateDetectionStats(newDetections) {
  detectionStats.value.totalDetections += newDetections.length;

  newDetections.forEach((detection) => {
    if (detection.class.toLowerCase() === "fire") {
      detectionStats.value.fireDetections++;
    } else if (detection.class.toLowerCase() === "smoke") {
      detectionStats.value.smokeDetections++;
    }

    // Update confidence statistics
    const confidence = detection.confidence;
    if (confidence > detectionStats.value.maxConfidence) {
      detectionStats.value.maxConfidence = confidence;
    }
  });

  // Calculate average confidence
  if (detectionStats.value.totalDetections > 0) {
    const totalConfidence = newDetections.reduce(
      (sum, d) => sum + d.confidence,
      0
    );
    const currentAvg = detectionStats.value.avgConfidence;
    const totalCount = detectionStats.value.totalDetections;
    detectionStats.value.avgConfidence =
      (currentAvg * (totalCount - newDetections.length) + totalConfidence) /
      totalCount;
  }
}

// Template helper methods
const getDetectionClass = (className) => {
  return className.toLowerCase() === "fire"
    ? "detection-fire"
    : "detection-smoke";
};

const getDetectionLabelClass = (className) => {
  return className.toLowerCase() === "fire" ? "label-fire" : "label-smoke";
};

const getPerformanceClass = () => {
  if (fps.value > 20) return "performance-good";
  if (fps.value > 10) return "performance-medium";
  return "performance-poor";
};

const getPerformanceText = () => {
  if (fps.value > 20) return "Excellent";
  if (fps.value > 15) return "Good";
  if (fps.value > 10) return "Fair";
  return "Poor";
};

const getDetectionCount = (type) => {
  return detections.value.filter((d) => d.class.toLowerCase() === type).length;
};

// Computed properties for template
const isMobile = ref(false);
const canSwitchCamera = ref(false);
const currentFacingMode = ref("environment");
const selectedQuality = ref("balanced");
const totalDetections = ref(0);
const supports1080p = ref(false);

// Check if camera supports 1080p resolution
async function check1080pSupport() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { exact: 1920 },
        height: { exact: 1080 },
        facingMode: currentCameraFacing.value,
      },
    });

    // If we get here, 1080p is supported
    supports1080p.value = true;

    // Stop the test stream
    stream.getTracks().forEach((track) => track.stop());

    return true;
  } catch (error) {
    // 1080p not supported
    supports1080p.value = false;
    return false;
  }
}

// Initialize mobile detection and camera enumeration on mount
onMounted(async () => {
  isMobile.value = detectMobileDevice();
  await getAvailableCameras();
  canSwitchCamera.value = availableCameras.value.length > 1;

  // Check for 1080p support
  await check1080pSupport();
});

// Quality adjustment method
const adjustQuality = () => {
  if (selectedQuality.value === "auto") {
    performanceMode.value = "balanced";
  } else if (selectedQuality.value === "ultra" && supports1080p.value) {
    performanceMode.value = "ultra";
  } else {
    performanceMode.value = selectedQuality.value;
  }
};

// Cleanup on component unmount
onUnmounted(() => {
  stopCamera();
});

// Watch for modal visibility changes
watch(
  () => props.isVisible,
  (newValue) => {
    if (newValue) {
      resetState();
      if (!useBrowserCamera.value) {
        runYoloDetection();
      }
    } else {
      // Clean up when modal closes
      if (cameraActive.value) {
        stopCamera();
      }
    }
  }
);
</script>

<style scoped>
/* Enhanced styles for camera integration */
.detection-mode {
  margin: 1rem 0;
  text-align: center;
}

.mode-toggle-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.mode-toggle-btn.active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  transform: scale(1.05);
}

.camera-section {
  margin: 1rem 0;
}

.camera-container {
  position: relative;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  margin: 1rem 0;
  aspect-ratio: 4/3;
  max-width: 100%;
}

.camera-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.camera-container video.camera-active {
  opacity: 1;
}

.detection-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* Color-coded detection boxes */
.detection-box {
  position: absolute;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.detection-box.detection-fire {
  border: 3px solid #0066cc;
  background: rgba(0, 102, 204, 0.15);
  box-shadow: 0 0 15px rgba(0, 102, 204, 0.4);
}

.detection-box.detection-smoke {
  border: 3px solid #87ceeb;
  background: rgba(135, 206, 235, 0.15);
  box-shadow: 0 0 15px rgba(135, 206, 235, 0.4);
}

.detection-label {
  position: absolute;
  top: -30px;
  left: 0;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  white-space: nowrap;
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}

.detection-label.label-fire {
  background: linear-gradient(135deg, #0066cc, #004499);
}

.detection-label.label-smoke {
  background: linear-gradient(135deg, #87ceeb, #5dade2);
}

/* Performance indicator */
.performance-indicator {
  position: absolute;
  top: 15px;
  right: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 12px;
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.indicator-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.indicator-dot.performance-good {
  background: #28a745;
}

.indicator-dot.performance-medium {
  background: #ffc107;
}

.indicator-dot.performance-poor {
  background: #dc3545;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

/* Enhanced camera controls */
.camera-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0;
}

.primary-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.mobile-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.5rem;
  background: rgba(0, 123, 255, 0.1);
  border-radius: 8px;
}

.switch-camera-btn {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.switch-camera-btn:hover {
  background: #138496;
  transform: translateY(-1px);
}

.switch-camera-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.camera-info {
  font-size: 0.9rem;
  color: #495057;
  font-weight: 500;
}

.quality-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.quality-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: white;
}

.camera-btn,
.detection-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 140px;
  font-weight: 500;
}

.camera-btn:hover,
.detection-btn:hover {
  background: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
}

.detection-btn.active {
  background: #28a745;
}

.detection-btn.active:hover {
  background: #218838;
}

.camera-btn:disabled,
.detection-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Enhanced detection stats grid */
.detection-stats {
  background: linear-gradient(
    135deg,
    rgba(0, 123, 255, 0.1),
    rgba(40, 167, 69, 0.1)
  );
  border: 2px solid rgba(0, 123, 255, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: bold;
  color: #2c3e50;
}

/* Existing styles... */
.modal-content {
  position: relative;
  width: 100%;
  max-width: 800px; /* Increased for camera view */
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

/* Mobile responsive */
@media (max-width: 768px) {
  .camera-controls {
    margin: 0.5rem 0;
  }

  .primary-controls {
    flex-direction: column;
    align-items: center;
  }

  .camera-btn,
  .detection-btn {
    width: 90%;
    margin: 0.25rem 0;
    padding: 0.75rem;
  }

  .mobile-controls {
    margin: 0.5rem 0;
  }

  .switch-camera-btn {
    padding: 0.5rem 1rem;
  }

  .modal-content {
    max-width: 95%;
    margin: 0.5rem;
    padding: 1rem;
  }

  .camera-container {
    margin: 0.75rem 0;
    border-radius: 8px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .stat-item {
    padding: 0.5rem;
  }

  .performance-indicator {
    top: 10px;
    right: 10px;
    padding: 6px 10px;
    font-size: 11px;
  }

  .indicator-dot {
    width: 10px;
    height: 10px;
  }

  .detection-label {
    font-size: 12px;
    padding: 2px 8px;
    top: -25px;
  }

  .quality-controls {
    flex-direction: column;
    gap: 0.25rem;
  }
}

/* Error handling styles (existing) */
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
</style>
