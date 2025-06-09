// API Configuration
export const API_CONFIG = {
  // Production backend URL (deployed on Render)
  BASE_URL: "https://fire-smoke-detection-api.onrender.com",

  // Development backend URL (uncomment for local development)
  // BASE_URL: "http://localhost:5000",
  ENDPOINTS: {
    RUN_YOLO: "/run-yolo",
    STOP_YOLO: "/stop-yolo",
    DETECT_FRAME: "/detect-frame",
    MODEL_INFO: "/model-info",
  },
};

export const getApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
