import time
import logging

logger = logging.getLogger(__name__)

try:
    from gpiozero import DistanceSensor
    GPIO_AVAILABLE = True
    logger.info("gpiozero available.")
except ImportError:
    logger.warning("gpiozero not found — simulation mode.")
    GPIO_AVAILABLE = False

try:
    from picamera2 import Picamera2
    import cv2
    import numpy as np
    CAMERA_AVAILABLE = True
except ImportError:
    logger.warning("picamera2 not found — simulation mode.")
    CAMERA_AVAILABLE = False


class SensorManager:
    def __init__(self, trig_pin, echo_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self._sensor = None
        self._camera = None

        if GPIO_AVAILABLE:
            try:
                self._sensor = DistanceSensor(
                    echo=echo_pin,
                    trigger=trig_pin,
                    max_distance=3.0
                )
                logger.info(f"Ultrasonic sensor initialised (TRIG={trig_pin}, ECHO={echo_pin})")
            except Exception as exc:
                logger.error(f"Ultrasonic init failed: {exc}")
                self._sensor = None

        if CAMERA_AVAILABLE:
            self._init_camera()

    def _init_camera(self):
        try:
            self._camera = Picamera2()
            config = self._camera.create_still_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            self._camera.configure(config)
            logger.info("Pi Camera initialised.")
        except Exception as exc:
            logger.error(f"Camera init failed: {exc}")
            self._camera = None

    def capture_frame(self):
        if not CAMERA_AVAILABLE or self._camera is None:
            import numpy as np
            return np.zeros((480, 640, 3), dtype="uint8")
        try:
            self._camera.start()
            time.sleep(0.3)
            frame = self._camera.capture_array()   # already RGB888
            self._camera.stop()
            import numpy as np
            # keep 3 channels only (drop alpha if present), no color conversion
            if frame.ndim == 3 and frame.shape[2] == 4:
                frame = frame[:, :, :3]
            return np.ascontiguousarray(frame)
        except Exception as exc:
            logger.error(f"Capture error: {exc}")
            return None

    def measure_distance(self):
        if not GPIO_AVAILABLE or self._sensor is None:
            import random
            return random.uniform(20, 100)
        try:
            distance = self._sensor.distance * 100  # 미터 → cm
            return round(distance, 1)
        except Exception as exc:
            logger.error(f"Distance error: {exc}")
            return None

    def cleanup(self):
        if self._camera is not None:
            try:
                self._camera.stop()
            except Exception:
                pass
        if self._sensor is not None:
            try:
                self._sensor.close()
            except Exception:
                pass
