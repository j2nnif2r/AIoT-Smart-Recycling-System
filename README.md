# Base Code for a Recycling Guidance Device 
(Raspberry Pi 5)

Concept: The system **recognizes waste and guides the user to the correct bin**, while also **monitoring the bin's fill level**.
Since users sort the waste manually, **no servo motor or other motor is used**.
Hardware: HC-SR04 ultrasonic fill-level sensor + I2C LCD 1602 (+ YOLO camera).

## 1. Setup (Raspberry Pi OS Bookworm)

```bash
# Enable I2C: raspi-config -> Interface Options -> I2C -> Enable
sudo raspi-config

# Check the LCD address (usually 0x27 or 0x3F)
sudo apt install -y i2c-tools
i2cdetect -y 1

# Install libraries (gpiozero/lgpio are usually installed by default)
pip install -r requirements.txt --break-system-packages
```

Enter the detected LCD address in `LCD_ADDRESS` inside `config.py`.

## 2. Pin Connection Summary (BCM)

| Component | Pin | GPIO (Physical Pin) |
|---|---|---|
| HC-SR04 TRIG | TRIG_PIN | GPIO23 (16) |
| HC-SR04 ECHO | ECHO_PIN | GPIO24 (18) — **through a 1k/2k voltage divider** |
| LCD SDA / SCL | I2C | GPIO2 (3) / GPIO3 (5) |
| Power | 5V / GND | Breadboard + / - rails |

> Since no servo is used, the **servo (GPIO18) and External 5V block in the wiring diagram do not need to be connected.**

## 3. Run

```bash
python3 main.py
```

- Normal screen: fill level (%) + `Compress needed!` when it exceeds 80%
- When waste is recognized: guides the user to the correct bin, such as `Detected:Plastic` / `-> Plastic bin`.
- Even without an LCD, the same information is printed to the console so the operation can be checked.

## 4. Calibration (Important)

Measure the actual sensor-to-surface distance when the bin is empty and when it is full, then enter the values in `config.py`.

```python
EMPTY_DISTANCE_CM = 30.0   # Empty bin: sensor -> bottom
FULL_DISTANCE_CM  = 5.0    # Full bin: waste -> sensor
```

## 5. Extensions

- **YOLO Recognition**: Complete `classify_frame()` in `camera_yolo.py`, then
  modify `get_detected_category()` in `main.py` so that it calls the function.
  The LCD automatically displays guidance based on the returned category.
  The bin names can be changed in `CATEGORY_GUIDE` inside `config.py`.
- **Multiple Bins**: Create one `FillSensor` for each bin (each with its own TRIG/ECHO pins +
  voltage-divider resistors), store them in a list, and display the fill level of each bin in a loop.
- **Mobile Dashboard**: Send the value from `percent()` to a server using MQTT or HTTP
  and connect it to the previously designed fill-level monitoring screen.

## Troubleshooting

- `lgpio`/permission error: Run `sudo usermod -aG gpio $USER`, then log in again.
- Nothing appears on the LCD: Recheck the address with `i2cdetect -y 1` and adjust the contrast using the potentiometer on the back.
- Distance values are unstable: Check the ECHO voltage-divider wiring and the sensor power supply (5V).
