# Fire Smoke Detection - Vue 3 Frontend

This is the Vue 3 frontend for the Fire Smoke Detection application.

## Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:3000`

## Build for Production

To build the application for production:

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── FireSmokeApp.vue      # Main application component
│   │   ├── CurrentTime.vue       # Real-time clock component
│   │   └── CameraModal.vue       # Modal for camera detection
│   ├── App.vue                   # Root component
│   ├── main.js                   # Application entry point
│   └── style.css                 # Global styles
├── index.html                    # HTML template
├── package.json                  # Dependencies and scripts
└── vite.config.js               # Vite configuration
```

## Features

- Real-time clock display
- Modal-based camera detection interface
- API integration with Python backend
- Responsive design with dark theme
- Loading states and error handling

## Backend Integration

The frontend is configured to proxy API requests to the Python backend running on `http://localhost:5000`. Make sure your Python server is running before starting the Vue application.

API endpoints:

- `POST /run-yolo` - Start YOLO detection
- `POST /stop-yolo` - Stop YOLO detection
