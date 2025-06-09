// API Configuration
export const API_CONFIG = {
  // Production backend URL (comment out for local development)
  // BASE_URL: "https://fire-smoke-detection-api.onrender.com",

  // Development backend URL (uncomment for local development)
  BASE_URL: "http://localhost:5000",

  ENDPOINTS: {
    RUN_YOLO: "/run-yolo",
    STOP_YOLO: "/stop-yolo",
    DETECT_FRAME: "/detect-frame",
    MODEL_INFO: "/model-info",
    HEALTH: "/health",
  },

  // WebSocket configuration
  WEBSOCKET: {
    URL: "http://localhost:5000",
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
