# 🔥 Fire & Smoke Detection Web Application

A real-time fire and smoke detection system using YOLO11 and Vue.js, successfully deployed on Render.

## ✅ Live Application

**🔴 [https://fire-smoke-webapp.onrender.com](https://fire-smoke-webapp.onrender.com)**

> The application is now live and fully functional! Try the real-time fire detection system.

## 🚀 Quick Deploy to Render

### Prerequisites

- GitHub account
- Render account (free tier available)

### Deployment Steps

1. **Fork/Clone this repository to your GitHub**

2. **Create new Web Service on Render:**

   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select this repository

3. **Configure Deployment Settings:**

   ```
   Name: fire-detection-app
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main (or Deployment)
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
   ```

4. **Set Environment Variables:**

   ```
   PYTHON_VERSION=3.9.18
   NODE_ENV=production
   PORT=5000
   ```

5. **Advanced Settings:**

   ```
   Auto-Deploy: Yes
   Health Check Path: /health
   ```

6. **Update Frontend Configuration:**
   - After deployment, get your Render URL (e.g., `https://fire-smoke-webapp.onrender.com`)
   - Update `frontend/src/config.js`:
   ```javascript
   production: {
     API_BASE_URL: "https://fire-smoke-webapp.onrender.com",
     WS_BASE_URL: "https://fire-smoke-webapp.onrender.com"
   }
   ```
   - Rebuild frontend: `cd frontend && npm run build`
   - Commit and push changes

## 🏗️ Local Development

### Backend

```bash
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📱 Features

- ✅ Real-time fire and smoke detection
- ✅ Audio alerts with different frequencies
- ✅ Browser notifications
- ✅ Mobile-responsive design
- ✅ Side notification panel
- ✅ Alert history management
- ✅ Webcam integration
- ✅ Production-ready deployment

## 🔧 API Endpoints

- `GET /health` - Health check
- `GET /detections` - Get latest detection results
- `POST /run-yolo` - Start YOLO detection
- `POST /stop-yolo` - Stop YOLO detection
- `POST /detect-frame` - Process single frame

## 🏃‍♂️ Testing Deployment

```bash
# Health check
curl https://fire-smoke-webapp.onrender.com/health

# Frontend
https://fire-smoke-webapp.onrender.com
```

## 📊 Model Information

- **Model:** YOLO11 Nano (best_nano_111.pt)
- **Classes:** Fire, Smoke
- **Input:** Real-time webcam feed
- **Confidence:** 35% threshold
- **IoU:** 0.1 threshold

## 🔒 Security Features

- CORS enabled for cross-origin requests
- Environment-based configuration
- Input validation and error handling
- Secure WebSocket connections

## 🐛 Troubleshooting

### Build Fails

- Check requirements.txt versions
- Verify Python 3.9+ compatibility
- Review build logs for specific errors

### Model Not Loading

- Ensure model file is uploaded (Git LFS)
- Check file permissions
- Verify model path in logs

### Frontend Connection Issues

- Update production URLs in config.js
- Check CORS settings
- Verify WebSocket connections

## 📧 Support

For issues or questions, please create an issue in the GitHub repository.

---

**🌟 Star this repository if it helped you!**
