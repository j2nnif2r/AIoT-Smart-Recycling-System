# AIoT Smart Recycling System
**Gachon University · Introduction to IoT (IoT26) · Spring 2026**

---

## Overview

An ultrasonic sensor detects an approaching user → a language selection screen appears →
the camera captures an image and YOLOv8 classifies the waste →
the result (waste type + disposal instructions) is shown in the selected language on the HDMI display.
While idle, an SHT30 sensor continuously monitors temperature and humidity.

---

## Overall Workflow

```
Idle (temperature & humidity displayed)
   ↓ User detected (ultrasonic sensor < 50 cm)
Language selection screen
   ↓ User touches a language (English / 한국어 / 中文 / 日本語)
Camera capture & YOLOv8 classification
   ↓
Result shown in the selected language (waste type + disposal guidance)
   ↓ (after 5 seconds)
Return to idle screen
```

| State | Screen content |
|-------|-----------------|
| IDLE | Temperature / humidity cards (refreshed every 30 s, English) |
| LANG_SELECT | 2×2 language selection buttons (touch / click / number keys 1–4) |
| ACTIVE | "Scanning..." → classification result (selected language) |

> If no language is selected within 15 seconds on the language screen, the system automatically returns to the idle screen.

---

## Hardware Components

| Component | Model | Connection |
|-----------|-------|------------|
| MCU | Raspberry Pi 5 | — |
| Camera | Pi Camera Module 3 | CSI |
| Distance sensor | HC-SR04 Ultrasonic | GPIO BCM 23 (TRIG), 24 (ECHO) |
| Temperature/Humidity sensor | SHT30 | I2C (SDA=GPIO2, SCL=GPIO3), address 0x44 |
| Display | HDMI Touchscreen | HDMI + USB (touch) |

---

## Wiring Diagram

```
HC-SR04
  VCC  -> 5V (Pin 2)
  GND  -> GND (Pin 6)
  TRIG -> GPIO 23 (Pin 16)
  ECHO -> GPIO 24 (Pin 18)  <- Voltage divider required! (1kΩ + 1kΩ in series ≈ 2kΩ)

SHT30 (I2C)
  VCC -> 3.3V (Pin 1)
  GND -> GND (Pin 9)
  SCL -> GPIO 3 / SCL (Pin 5)
  SDA -> GPIO 2 / SDA (Pin 3)

HDMI Touchscreen
  HDMI -> Pi HDMI port
  USB  -> Touch input (registers as mouse clicks)
```

> **Caution**: The HC-SR04 ECHO pin outputs 5V, but the Pi GPIO only tolerates 3.3V.
> A voltage divider (1kΩ + 1kΩ in series, with the GPIO connected at the midpoint) or a logic-level converter is required.

---

## Installation

```bash
# 1. System packages
sudo apt update
sudo apt install -y python3-picamera2 python3-rpi-lgpio python3-libgpiod \
                     fonts-noto-cjk swig i2c-tools

# Enable I2C (raspi-config -> Interface Options -> I2C)
sudo raspi-config

# 2. Python virtual environment (includes system packages)
python3 -m venv venv --system-site-packages
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify SHT30 is detected on I2C (should show 0x44 or 0x45)
sudo i2cdetect -y 1
```

---

## Running the System

```bash
cd ~/Desktop/TeamFTermProject
source venv/bin/activate
python main.py
```

- Press `ESC` or `Ctrl+C` to exit.
- On first run (with internet access), the YOLOv8n model weights (`yolov8n.pt`) are downloaded automatically.

---

## Project Structure

```
TeamFTermProject/
├── main.py                  # Main loop (state machine)
├── requirements.txt
├── README.md
├── models/
│   └── waste_yolo.pt        # (optional) custom-trained model weights
├── logs/
│   ├── system.log           # System log
│   └── env_log.csv          # Temperature/humidity history
└── utils/
    ├── __init__.py
    ├── sensor_manager.py    # HC-SR04 + Pi Camera
    ├── lcd_display.py        # pygame HDMI touch display (incl. language selection)
    ├── translations.py       # Multilingual text (EN/KO/ZH/JA)
    ├── waste_classifier.py   # YOLOv8 classifier
    └── env_monitor.py        # SHT30 temperature/humidity monitor (I2C)
```

---

## Multilingual Support

`utils/translations.py` defines UI text and disposal guidance for four languages.

| Code | Language |
|------|----------|
| en | English |
| ko | Korean |
| zh | Chinese |
| ja | Japanese |

Once a language button is touched (or clicked) on the selection screen, every subsequent screen
(scanning, classification result, disposal guidance) is displayed in that language.
Number keys `1`/`2`/`3`/`4` can also be used for testing (English/Korean/Chinese/Japanese, respectively).

---

## YOLO Model Notes

- **Default**: YOLOv8n (COCO pretrained) — downloads automatically, no training required
- **Custom**: place a fine-tuned `models/waste_yolo.pt` and it will be loaded automatically

Example custom training command:
```bash
yolo train data=waste.yaml model=yolov8n.pt epochs=50 imgsz=640
```

---

## Evaluation Criteria Mapping

| Item | Implementation |
|------|----------------|
| System Core Integration (40%) | Pi 5 + HC-SR04 + SHT30 + Pi Camera + HDMI touch display, all integrated |
| AI Model Performance (25%) | YOLOv8 — Bottle / Can / Paper + 3 additional categories |
| Technical Documentation (15%) | README + code comments + env_log.csv |
| Presentation & Demo (15%) | Immediate demo via `python main.py` |
| Bonus: Advanced Ideas (+25%) | 4-language UI (English/Korean/Chinese/Japanese) |

---

## Troubleshooting

| Symptom | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'utils'` | `touch utils/__init__.py` |
| `Cannot determine SOC peripheral base address` | Use gpiozero/lgpio instead of RPi.GPIO (`sudo apt install python3-rpi-lgpio`) |
| `pygame.error: video system not initialized` | Make sure `os.environ["SDL_VIDEODRIVER"]="x11"` and `DISPLAY=":0"` are set |
| Korean/Chinese/Japanese text shows as boxes | `sudo apt install -y fonts-noto-cjk` |
| `no echo received` (ultrasonic sensor) | Check the ECHO pin voltage divider (1kΩ + 1kΩ) wiring |
| `externally-managed-environment` (pip error) | Use `python3 -m venv venv --system-site-packages` then `source venv/bin/activate` |
