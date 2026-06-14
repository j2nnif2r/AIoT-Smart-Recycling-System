# AIoT Smart Recycling System

An AIoT-based smart recycling assistant built with a Raspberry Pi 5. The system detects when a person approaches, allows the user to select a language, captures an image of the waste, classifies it with YOLO, and displays the correct disposal method in the selected language.

## 1. Project Overview

The system operates in the following sequence:

```text
Standby Screen
    ↓
Person Detected Within 20 cm
    ↓
Language Selection Screen
    ↓
Camera Capture and YOLO Classification
    ↓
Waste Type and Disposal Method Displayed
    ↓
Return to Standby Screen
```

During standby mode, the display shows:

- Current temperature
- Current humidity
- One recycling fact or recycling tip

## 2. Main Features

- Real-time temperature and humidity monitoring using the SHT30 sensor
- Person detection using the HC-SR04 ultrasonic sensor
- Touch-based language selection
- Waste image capture using the Raspberry Pi Camera Module
- Waste classification using a YOLO model
- Disposal instructions in four languages
- Automatic return to the standby screen after displaying the result

## 3. Supported Languages

The user can select one of the following languages:

- English
- Korean
- Chinese
- Japanese

## 4. Hardware Components

- Raspberry Pi 5
- Raspberry Pi Camera Module
- HC-SR04 ultrasonic distance sensor
- SHT30 temperature and humidity sensor
- HDMI touchscreen display
- Breadboard
- Jumper wires
- Resistors for the HC-SR04 ECHO voltage divider

## 5. Hardware Connections

### 5.1 HC-SR04 Ultrasonic Sensor

| HC-SR04 Pin | Raspberry Pi 5 Connection |
|---|---|
| VCC | 3.3V |
| TRIG | GPIO 23 |
| ECHO | GPIO 24 |
| GND | GND |

> **Important:** The HC-SR04 ECHO pin outputs approximately 5V. Raspberry Pi GPIO pins support only 3.3V. A voltage divider must be used between the ECHO pin and GPIO 24.

Example voltage divider:

```text
HC-SR04 ECHO ---- 1 kΩ resistor ---- GPIO 24
                                    |
                                  10 kΩ
                                    |
                                   GND
```

If a 2 kΩ resistor is not available, a suitable resistor combination may be used to create approximately the same ratio.

### 5.2 SHT30 Temperature and Humidity Sensor

| SHT30 Pin | Raspberry Pi 5 Connection |
|---|---|
| VIN / VCC | 3.3V |
| GND | GND |
| SDA | GPIO 2, physical pin 3 |
| SCL | GPIO 3, physical pin 5 |

The SHT30 normally uses the I2C address `0x44`. Some modules may use `0x45`.

### 5.3 Raspberry Pi Camera Module

Connect the camera module to a Raspberry Pi 5 CSI camera connector using the correct camera cable.

The camera is controlled using the `picamera2` library.

### 5.4 HDMI Touchscreen Display

- Connect the display to the Raspberry Pi through HDMI.
- Connect the touchscreen USB cable to the Raspberry Pi for touch input.
- Configure the display resolution according to the screen model.

## 6. Software Requirements

Recommended operating system:

- Raspberry Pi OS Bookworm, 64-bit

Required software and Python libraries:

- Python 3
- Picamera2
- Ultralytics YOLO
- OpenCV
- gpiozero
- lgpio
- smbus2
- pygame
- Adafruit
- gpiod
- numpy
- onnxruntime
- RPi.GPIO

## 7. Suggested Project Structure

```text
AIoT-Smart-Recycling-System/
├── main.py
├── sensor_manager.py
├── env_monitor.py
├── waste_classifier.py
├── camera_manager.py
├── display_ui.py
├── translations.py
├── recycling_tips.py
├── requirements.txt
├── models/
│   └── best.pt
├── captured_images/
└── README.md
```

### File Responsibilities

| File | Description |
|---|---|
| `main.py` | Controls the complete system flow and screen transitions |
| `sensor_manager.py` | Reads distance data from the HC-SR04 sensor |
| `env_monitor.py` | Reads temperature and humidity from the SHT30 sensor |
| `waste_classifier.py` | Runs YOLO inference and returns the detected waste class |
| `camera_manager.py` | Controls image capture using Picamera2 |
| `display_ui.py` | Displays the standby, language, camera, and result screens |
| `translations.py` | Stores multilingual interface text and disposal instructions |
| `recycling_tips.py` | Stores short recycling facts for the standby screen |

## 8. System Operation

### 8.1 Standby Mode

The default screen displays:

- Current temperature
- Current humidity
- A recycling fact
- A message such as `Please approach the device`

Example recycling fact:

```text
Recycling one aluminum can saves enough energy to run a television for several hours.
```

The SHT30 sensor should update the temperature and humidity values at regular intervals.

### 8.2 Person Detection

The HC-SR04 continuously measures the distance in front of the device.

A person is detected when:

```text
Distance < 20 cm
```

To reduce false detection, the program may require two or three consecutive measurements below 20 cm before changing screens.

### 8.3 Language Selection

When a person is detected, the touchscreen displays four buttons:

```text
English | 한국어 | 中文 | 日本語
```

The selected language is stored and used for all following messages.

### 8.4 Camera and Waste Classification

After language selection:

1. The camera screen is displayed.
2. The Raspberry Pi Camera captures an image.
3. The image is passed to the YOLO model.
4. YOLO predicts the waste category.
5. The class name and confidence score are returned.

Example waste categories:

- Plastic
- Paper
- Glass
- Can
- General waste

The exact categories depend on the dataset used to train the lightweight YOLO model.
("https://github.com/yoobright/yolo-onnx/raw/master/yolov8n.onnx")

### 8.5 Result Screen

The result screen displays:

- Detected waste type
- Classification confidence
- Correct disposal method
- A message in the selected language

Example in English:

```text
Detected Waste: Plastic
Disposal Method: Empty the bottle, rinse it, remove the cap, and place it in the plastic recycling bin.
```

Example in Korean:

```text
분류 결과: 플라스틱
배출 방법: 내용물을 비우고 깨끗이 헹군 뒤 뚜껑을 분리하여 플라스틱 수거함에 넣어주세요.
```

After a fixed display time, such as 5 to 10 seconds, the system returns to standby mode.

## 9. Example State Flow

The application can be implemented with the following states:

```python
STANDBY = "standby"
LANGUAGE_SELECTION = "language_selection"
CAMERA = "camera"
RESULT = "result"
```

Example state transition logic:

```text
STANDBY
  └─ If distance is below 20 cm → LANGUAGE_SELECTION

LANGUAGE_SELECTION
  └─ If a language button is touched → CAMERA

CAMERA
  └─ After capture and classification → RESULT

RESULT
  └─ After the result timer ends → STANDBY
```

## 10. Example Multilingual Disposal Data

```python
DISPOSAL_GUIDE = {
    "plastic": {
        "en": "Empty, rinse, remove the cap, and place it in the plastic recycling bin.",
        "ko": "내용물을 비우고 헹군 뒤 뚜껑을 분리하여 플라스틱 수거함에 넣어주세요.",
        "zh": "请倒空并清洗容器，取下瓶盖后投入塑料回收箱。",
        "ja": "中身を空にして洗い、キャップを外してプラスチック回収箱に入れてください。"
    }
}
```

## 11. Example Recycling Tips

```python
RECYCLING_TIPS = [
    "Recycling one glass bottle saves enough energy to light a bulb for ~4 hours.",
    "Recycling one ton of paper can save about 17 trees.",
    "Recycling plastic bottles can cut CO2 emissions by up to 80% vs. new plastic.",
    "Correct sorting greatly reduces landfill waste and carbon emissions.",
    "Recycling one aluminum can saves enough energy to light a bulb for ~4 hours."
]
```

A random tip can be displayed each time the system returns to standby mode.

## 12. Running the Program

Activate the virtual environment:

```bash
cd AIoT-Smart-Recycling-System
source venv/bin/activate
```

Run the main program:

```bash
python3 main.py
```

For fullscreen touchscreen operation, configure the UI program to open in fullscreen mode.

## 13. Error Handling

The application should handle the following cases:

- SHT30 sensor not detected
- Invalid ultrasonic sensor reading
- Camera connection failure
- YOLO model file not found
- No waste detected
- Multiple objects detected
- Low-confidence classification

Example messages:

```text
Detection Failed
try again with one item
```

## 14. License

This project is intended for educational and academic use.
