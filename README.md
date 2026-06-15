# AIoT Smart Recycling System

AIoT-based Smart Recycling System for worldwide use — Gachon University, Introduction to IoT (IoT26), Spring 2026, Team F.

## Team

| Member | Role | Participation |
| --- | --- | --- |
| 김건 (202234859) | Code development / YOLO train | 33.3% |
| 김채윤 (202434865) | Prompt Engineering / Hardware development | 33.3% |
| 김현보 (202434751) | Hardware wiring / sensor integration / multilingual | 33.3% |

## Deliverables

- **GitHub repository**: https://github.com/j2nnif2r/AIoT-Smart-Recycling-System
- **Lookup web page (web app)**: https://iot-team-f-term-project.web.app

## Project Overview

Using a Raspberry Pi 5 as the edge-computing hub, the system detects an approaching user, captures the waste item with a camera, classifies its type with YOLO, and displays the correct disposal guidance on a 7-inch LCD. During idle periods, it measures and logs the temperature and humidity around the bin to monitor sanitation.

On top of the basic requirements (sensor fusion / smart UI / environment monitoring), extended features were implemented, including multilingual guidance, touch interaction, carbon-reduction visualization, and cloud integration via QR code.

## System Configuration

| Category | Parts / Technology |
| --- | --- |
| Core | Raspberry Pi 5 (RP1 I/O) |
| Distance sensing | HC-SR04 ultrasonic sensor (TRIG GPIO23, ECHO GPIO24) |
| Vision | Pi Camera (OV5647), libcamera / picamera2 |
| Temp / Humidity | SHT30 (I2C, SDA GPIO2 / SCL GPIO3) |
| Display | 7-inch capacitive touch LCD (pygame GUI) |
| AI | YOLOv8n (ONNX) + onnxruntime |
| Cloud | Firebase Firestore + Hosting, QR integration |

## Code Structure

| File | Description |
| --- | --- |
| `main.py` | State flow control |
| `sensor_manager.py` | Ultrasonic & camera handling |
| `env_monitor.py` | SHT30 temperature/humidity monitoring |
| `waste_classifier.py` | YOLO ONNX-based waste classification |
| `lcd_display.py` | GUI (pygame) |
| `cloud_uploader.py` | Firestore upload & QR code generation |

## Core: Troubleshooting Process

The core value of this project lies in the process of diagnosing and resolving problems at the hardware, platform, model, and environment levels.

### 1. Ultrasonic Sensor Circuit Design — ECHO Voltage Divider

- **Symptom**: Unstable GPIO input and abnormal distance values during HC-SR04 wiring.
- **Cause**: The HC-SR04 ECHO pin outputs 5V, but the Raspberry Pi GPIO only tolerates 3.3V.
- **Solution**: Designed a resistor voltage divider (R1 on ECHO side, R2 on GND side) so the divider node connects to GPIO24, stepping 5V down to ~3.3V (Vout = Vin × R2 / (R1 + R2)). TRIG connects directly to GPIO23; all modules share a common ground.
- **Result**: GPIO protected, distance measurement stabilized.

### 2. Temp/Humidity Sensor — DHT11 Not Working on Raspberry Pi 5

- **Symptom**: Kernel driver repeatedly returned `Only 0 signal edges detected`, even after re-wiring and replacing sensors.
- **Cause**: The Pi 5's RP1 I/O controller is a structural change that prevents the legacy kernel driver from capturing the DHT's microsecond-level single-wire timing — a platform-level limitation.
- **Solution**: Replaced DHT11 with the I2C-based SHT30 sensor, which is natively supported on the Pi 5.

### 3. SHT30 I2C Address Mismatch

- **Symptom**: `No I2C device at address: 0x44`.
- **Cause**: `i2cdetect -y 1` showed the device at `0x45` because the ADDR pin was tied to VDD.
- **Solution**: Explicitly specified `SHT31D(i2c, address=0x45)`.
- **Result**: Temperature/humidity readings restored; implemented 10-second CSV logging plus a 1-minute average display.

### 4. Camera Image Color Inversion (BGR/RGB)

- **Symptom**: Captured photos displayed with inverted colors on the LCD.
- **Cause**: Color conversion was applied twice — at capture and at display — swapping channels.
- **Solution**: Standardized capture to return raw RGB without conversion, applying BGR/RGB conversion only immediately before YOLO input.

### 5. YOLO Classification Accuracy (Biggest Challenge)

1. **General model limitation**: COCO-pretrained yolov8n misclassified bottles as food (no recycling-specific classes). → Fine-tuned yolov8n on a Roboflow recycling dataset and exported to ONNX.
2. **SD-card capacity constraint**: Installing `ultralytics` with PyTorch consumed too much space. → Re-implemented inference using onnxruntime only (manual preprocessing, NMS, box decoding), with class names managed in `class_names.txt`.
3. **Low confidence (30–50%) due to color order**: A redundant BGR→RGB conversion was applied to already-RGB camera output. → Removed the extra conversion, raising confidence.
4. **Over-granular classes**: Training on 42 classes produced very low mAP. → Remapped labels into 5 categories (plastic / glass / can / paper / general) and retrained, raising mAP50 to ~0.71.
5. **Data imbalance**: Per-class instance counts — plastic 3564, glass 1212, can 4605, paper 1920, general 5236. Glass recognition remained poor despite augmentation attempts; acknowledged as a limitation due to time constraints.

### 6. Runtime Environment Issues

- **Symptom**: System ran in `simulation mode` despite a valid model file.
- **Cause**: The required library was installed outside the active venv.
- **Solution**: Reinstalled within the activated venv and verified via an `import` check script.
- **Lesson**: Established a principle of fixing interfaces (class set, input size, return format) and synchronizing call sites whenever return signatures change.

## Advanced Features

### Multilingual + Touch GUI

- Fullscreen pygame GUI on the 7-inch capacitive touch LCD with automatic resolution detection.
- Supports four languages: English, Korean, Chinese, Japanese (Noto Sans CJK font).
- State flow: user detected → language selection (touch) → number entry (touch keypad) → classification → continue/end (yes/no).
- Automatic timeout-based termination when no selection is made.

### Carbon-Reduction Visualization

- Aggregates per-item counts within a session and converts them via approximate per-category CO₂-saving values.
- Displays a per-item bar chart plus total CO₂ saved on the summary screen, in the selected language.

### Cloud Integration (QR-based, Firebase)

- **Architecture**: Raspberry Pi (service account) → Firestore storage → QR code (shown on LCD) → user's mobile web page lookup.
- Uses the last 4 digits of a phone number as a key to accumulate records per user.
- The web page (Firebase Hosting) shows per-session and cumulative CO₂, tree/car equivalents, and a date-wise cumulative chart.
- **Troubleshooting**:
  - Web page failed to load data due to (1) Firestore security rules blocking reads and (2) a `SyntaxError` from a duplicate `initializeApp` import — resolved separately.
  - Confirmed that the service-account key bypasses security rules for writes, but reads require an explicit allow rule.
  - Fixed QR code overlapping guidance text by adjusting summary-screen layout coordinates.

## Results and Limitations

### Achievements

- Integrated operation of Pi 5 + SHT30 + ultrasonic + camera + 7-inch LCD.
- Real-time classification under SD-card constraints via lightweight ONNX inference.
- Classification into 4 categories (+general), with mAP50 around 0.71.
- Completed multilingual touch UI, carbon-reduction visualization, and QR-based cloud integration.

### Limitations

- **Limited classification accuracy**: confidence often stays in the 30–50% range, and the same item may be classified differently across attempts.
- **Data imbalance**: training data skewed (e.g., glass 1,212 vs. general 5,236), so glass is frequently missed or misclassified.
- **Domain gap**: real-world accuracy is sensitive to shooting distance, background, lighting, and hand-holding, and drops below the validation mAP50 of ~0.71.
- **Object-shape dependency**: items with atypical shapes (e.g., a short brown medicine bottle vs. common beverage bottles) are often not recognized.
- **QR-based notification instead of true push**: since the last 4 phone digits cannot identify a device, real SMS/app push was replaced with QR-code scanning.

## Future Improvements

- Augment under-represented categories (especially glass), rebalance the dataset, and retrain with more epochs to improve confidence and consistency.
- Collect and label images from the actual device camera (matching distance, angle, lighting, background) to reduce the domain gap.
- Standardize the capture environment: fix camera distance/angle, control lighting, and guide users to place a single item in the scan zone without holding it.
- Refine the category scheme (e.g., keep "can" focused on beverage cans) to sharpen decision boundaries between visually similar classes.
- Tighten cloud security after the demo by adjusting Firestore rules to "allow read / deny write."
