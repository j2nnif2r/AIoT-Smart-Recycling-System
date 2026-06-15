"""
env_monitor.py
SHT30 (I2C) temperature/humidity sensor + 10s logging + 1-min average
- I2C address: 0x45 (ADDR=HIGH)
Install: pip install adafruit-circuitpython-sht31d
"""
import logging, time, csv, os
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import board
    import adafruit_sht31d
    SHT_LIB = True
except ImportError:
    SHT_LIB = False
    logger.warning("adafruit_sht31d not found - EnvMonitor in simulation mode.")

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "env_log.csv")


class EnvMonitor:
    def __init__(self, address=0x45, record_interval=10, window_seconds=60):
        self._addr            = address
        self._record_interval = record_interval     # log every 10s
        self._window          = window_seconds       # 1-min (60s) average
        self._sensor          = None
        self._buffer          = deque()              # (ts, temp, hum)
        self._last_record     = 0.0

        if SHT_LIB:
            try:
                i2c = board.I2C()
                self._sensor = adafruit_sht31d.SHT31D(i2c, address=address)
                logger.info(f"SHT30 initialised (address 0x{address:02x})")
            except Exception as exc:
                logger.error(f"SHT30 init failed: {exc}")
                self._sensor = None

        self._ensure_log_header()
        # seed buffer/timer with one reading at startup
        t, h = self.read()
        if t is not None:
            now = time.time()
            self._buffer.append((now, t, h))
            self._last_record = now
            self._log(t, h)

    def read(self):
        """Read once -> (temp, hum) or (None, None)"""
        if self._sensor is not None:
            try:
                t = float(self._sensor.temperature)
                h = float(self._sensor.relative_humidity)
                return round(t, 1), round(h, 1)
            except Exception as exc:
                logger.error(f"SHT30 read error: {exc}")
                return None, None
        import random  # simulation
        return round(random.uniform(20, 30), 1), round(random.uniform(40, 70), 1)

    def update(self):
        """Call frequently from main loop. Logs + updates buffer every record_interval (10s)."""
        now = time.time()
        if now - self._last_record >= self._record_interval:
            t, h = self.read()
            if t is not None:
                self._buffer.append((now, t, h))
                self._log(t, h)
                self._last_record = now
                logger.info(f"[ENV] logged Temp={t:.1f}C Hum={h:.1f}%")
        self._prune(now)

    def get_average(self):
        """Average over last minute -> (avg_t, avg_h) or (None, None)"""
        self._prune(time.time())
        if not self._buffer:
            return None, None
        ts = [x[1] for x in self._buffer]
        hs = [x[2] for x in self._buffer]
        return round(sum(ts) / len(ts), 1), round(sum(hs) / len(hs), 1)

    def _prune(self, now):
        while self._buffer and now - self._buffer[0][0] > self._window:
            self._buffer.popleft()

    def _ensure_log_header(self):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", newline="") as f:
                csv.writer(f).writerow(["timestamp", "temperature_c", "humidity_pct"])

    def _log(self, t, h):
        try:
            with open(LOG_FILE, "a", newline="") as f:
                csv.writer(f).writerow([datetime.now().isoformat(timespec="seconds"), t, h])
        except Exception as exc:
            logger.error(f"env log write error: {exc}")
