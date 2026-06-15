"""
AIoT Smart Recycling System - Main Entry Point
Gachon University, IoT26 Spring 2026
"""
import time, logging, signal, sys, os
from collections import Counter
from sensor_manager import SensorManager
from lcd_display import LCDDisplay
from waste_classifier import WasteClassifier
from env_monitor import EnvMonitor
import cloud_uploader

os.makedirs("logs", exist_ok=True)
os.makedirs("logs/captures", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("logs/system.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

ULTRASONIC_TRIG_PIN = 23
ULTRASONIC_ECHO_PIN = 24
DETECTION_DISTANCE   = 20    # cm
CAPTURE_DELAY        = 3     # s
RESULT_HOLD          = 4     # s
ENV_DISPLAY_INTERVAL = 2     # s


def graceful_exit(sig, frame):
    logger.info("Shutdown signal received.")
    try:
        display.write("Smart Recycling", "Shutting down...")
        time.sleep(1); display.quit()
    except Exception:
        pass
    try:
        sensor.cleanup()
    except Exception:
        pass
    sys.exit(0)


def capture_and_classify(lang):
    """Prompt -> 3s countdown -> capture -> classify. Returns category or None."""
    display.write(_t("place_waste", lang), _t("in_zone", lang))
    time.sleep(1)
    for i in range(CAPTURE_DELAY, 0, -1):
        display.write(_t("get_ready", lang), f"{_t('capturing_in', lang)} {i}")
        time.sleep(1)
    display.write(_t("capturing", lang), _t("hold_still", lang))

    frame = sensor.capture_frame()
    if frame is None:
        display.write("Camera Error", "Please try again")
        time.sleep(2)
        return None
    try:
        import cv2
        cv2.imwrite(f"logs/captures/{time.strftime('%Y%m%d_%H%M%S')}.jpg", frame)
    except Exception:
        pass

    label, conf, annotated = classifier.classify(frame)
    if label is None:
        display.write(_t("no_detect", lang), _t("try_again", lang))
        time.sleep(RESULT_HOLD)
        return None
    logger.info(f"[ACTIVE] Result: {label} ({conf:.1%})")
    display.show_result(label, annotated, lang)
    time.sleep(RESULT_HOLD)
    return label


def _t(key, lang):
    from lcd_display import T
    return T[key][lang]


def get_phone(lang):
    """Touch keypad -> returns 4-digit string, or None if cancelled/timeout."""
    digits = ""
    while True:
        display.show_keypad(lang, digits)
        key = display.wait_touch(timeout=30)
        if key is None:
            return None
        if key == "back":
            digits = digits[:-1]
        elif key == "ok":
            if len(digits) == 4:
                return digits
        elif key.isdigit() and len(digits) < 4:
            digits += key


def run_session():
    """language -> phone -> classify loop -> summary(+QR) -> reset."""
    display.show_language_select()
    lang = display.wait_touch(timeout=30)
    if lang is None:
        return
    logger.info(f"[SESSION] language = {lang}")

    phone = get_phone(lang)
    if phone is None:
        return
    logger.info(f"[SESSION] phone = {phone}")

    CONTINUE_TIMEOUT = 7
    counts = Counter()

    while True:
        category = capture_and_classify(lang)
        if category is None:
            continue
        counts[category] += 1

        display.show_continue(lang)
        choice = display.wait_touch(timeout=CONTINUE_TIMEOUT)
        if choice == "yes":
            continue
        else:
            if choice is None:
                logger.info("[SESSION] no response -> auto end")
            break

    if sum(counts.values()) > 0:
        logger.info(f"[SESSION] summary {dict(counts)}")
        url = cloud_uploader.upload_session(phone, dict(counts))
        qr = cloud_uploader.make_qr_array(url)
        display.show_summary(counts, lang, qr_bgr=qr)
        time.sleep(12)


def main():
    global display, sensor, classifier, env_monitor
    logger.info("=== AIoT Smart Recycling System started ===")

    display     = LCDDisplay(fullscreen=True)
    sensor      = SensorManager(ULTRASONIC_TRIG_PIN, ULTRASONIC_ECHO_PIN)
    classifier  = WasteClassifier()
    env_monitor = EnvMonitor(address=0x45)

    signal.signal(signal.SIGINT,  graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    display.write("Smart Recycling", "System Ready!")
    time.sleep(2)

    last_env_display = 0.0
    while True:
        env_monitor.update()
        distance = sensor.measure_distance()

        if distance is not None and distance < DETECTION_DISTANCE:
            logger.info(f"[DETECT] {distance:.1f} cm -> SESSION START")
            run_session()
            last_env_display = 0.0          # back to idle (English)
        else:
            now = time.time()
            if now - last_env_display >= ENV_DISPLAY_INTERVAL:
                avg_t, avg_h = env_monitor.get_average()
                if avg_t is not None:
                    display.show_env(avg_t, avg_h, "en")   # idle always English
                else:
                    t, h = env_monitor.read()
                    if t is not None:
                        display.show_env(t, h, "en")
                    else:
                        display.write("Sensor Error", "Check SHT30")
                last_env_display = now

        time.sleep(0.1)


if __name__ == "__main__":
    main()
