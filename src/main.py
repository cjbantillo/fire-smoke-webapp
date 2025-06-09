import cv2
import logging
import sys
from pathlib import Path
from config import Config, setup_logging
from fire_detector import Detector
import time


def main():
    # Initialize logging and configuration
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Fire Detection System")

    try:
        # Validate configuration        # Config.validate()
        logger.debug("Configuration validation successful")

        # Initialize detection components
        detector = Detector(Config.MODEL_PATH, iou_threshold=0.20)
        logger.info(f"Loaded detection model: {Config.MODEL_PATH.name}")

        # Video processing setup
        cap = cv2.VideoCapture(str(Config.VIDEO_SOURCE))
        # cap = cv2.VideoCapture(0) # for webcam
        if not cap.isOpened():
            logger.error(f"Failed to open video source: {Config.VIDEO_SOURCE}")
            sys.exit(1)
        logger.info(f"Processing video source: {Config.VIDEO_SOURCE}")

        # State management
        alert_cooldown = Config.ALERT_COOLDOWN  # Seconds between alerts
        last_alert_time = 0

        next_detection_to_report = "any"  # "Fire" or "Smoke"
        # Main processing loop
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info("✅ Video processing completed")
                break

            # Detection pipeline
            processed_frame, detection = detector.process_frame(frame)            # Alert logic with cooldown
            if detection:
                current_time = time.time()
                if (next_detection_to_report == "any" or detection == next_detection_to_report) \
                        and (current_time - last_alert_time) > alert_cooldown:
                    logger.warning(f"🐦‍🔥 {detection} Detected!")
                    # Save detection frame for reference
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    filename = Config.DETECTED_FIRES_DIR / f'alert_{timestamp}.jpg'
                    cv2.imwrite(str(filename), processed_frame)
                    logger.info(f"Detection saved to: {filename}")
                    last_alert_time = current_time
                    next_detection_to_report = "Smoke" if detection == "Fire" else "Fire"

            # Display output
            cv2.imshow("Fire Detection System", processed_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                logger.info("🛑 User initiated shutdown")
                break

    except Exception as e:
        logger.critical(f"🚨 Critical system failure: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup resources
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()
        logger.info("🛑 System shutdown complete")


if __name__ == "__main__":
    main()
