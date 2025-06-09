// API Configuration
const config = {
  development: {
    API_BASE_URL: "http://localhost:5000",
    WS_BASE_URL: "http://localhost:5000",
  },
  production: {
    API_BASE_URL: "https://fire-smoke-webapp.onrender.com", // Your actual Render URL
    WS_BASE_URL: "https://fire-smoke-webapp.onrender.com", // Your actual Render URL
  },
};

const environment = import.meta.env.MODE || "development";
const currentConfig = config[environment];

export const API_CONFIG = {
  BASE_URL: currentConfig.API_BASE_URL,

  ENDPOINTS: {
    RUN_YOLO: "/run-yolo",
    STOP_YOLO: "/stop-yolo",
    DETECT_FRAME: "/detect-frame",
    MODEL_INFO: "/model-info",
    HEALTH: "/health",
    DETECTIONS: "/detections",
  },

  // WebSocket configuration
  WEBSOCKET: {
    URL: currentConfig.WS_BASE_URL,
    EVENTS: {
      CONNECT: "connect",
      DISCONNECT: "disconnect",
      VIDEO_FRAME: "video_frame",
      DETECTION_RESULTS: "detection_results",
      DETECTION_ERROR: "detection_error",
      STATUS: "status",
    },
  },
};

export const getApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

export const getWebSocketUrl = () => {
  return API_CONFIG.WEBSOCKET.URL;
};
