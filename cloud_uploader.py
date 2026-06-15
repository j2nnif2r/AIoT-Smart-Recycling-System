"""
cloud_uploader.py
Sends session data to Firestore and builds a QR code linking to the user's web page.
Install: pip install firebase-admin qrcode pillow
"""
import os, logging, datetime
import numpy as np

logger = logging.getLogger(__name__)

WEB_BASE = "https://iot-team-f-term-project.web.app"
KEY_PATH = os.path.join(os.path.dirname(__file__), "firebase_key.json")

# CO2 saved per item (grams) - keep in sync with lcd_display
CO2_SAVED_G = {"plastic": 80, "can": 9, "paper": 18, "glass": 30, "general": 0}

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    if os.path.exists(KEY_PATH):
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(KEY_PATH))
        _db = firestore.client()
        CLOUD_OK = True
        logger.info("Firestore connected.")
    else:
        _db = None
        CLOUD_OK = False
        logger.warning("firebase_key.json not found - cloud upload disabled.")
except Exception as exc:
    _db = None
    CLOUD_OK = False
    logger.warning(f"firebase init failed - cloud disabled: {exc}")


def upload_session(phone, counts):
    """
    phone: '1234' (last 4 digits, used as doc id)
    counts: dict like {'plastic':2, 'can':1}
    Returns the user's web URL (with ?id=) regardless of upload success.
    """
    url = f"{WEB_BASE}/?id={phone}"
    session_co2 = sum(CO2_SAVED_G.get(k, 0) * v for k, v in counts.items())
    session_items = sum(counts.values())

    if not CLOUD_OK or _db is None:
        logger.warning("Cloud disabled - skipping upload, QR still generated.")
        return url

    try:
        ref = _db.collection("users").document(str(phone))
        snap = ref.get()
        if snap.exists:
            data = snap.to_dict()
        else:
            data = {"total_co2": 0, "total_items": 0, "sessions": []}

        data["total_co2"]   = data.get("total_co2", 0) + session_co2
        data["total_items"] = data.get("total_items", 0) + session_items
        data.setdefault("sessions", []).append({
            "date":  datetime.datetime.now().isoformat(timespec="minutes"),
            "items": dict(counts),
            "co2":   session_co2,
        })
        ref.set(data)
        logger.info(f"Uploaded session for {phone}: +{session_co2}g CO2")
    except Exception as exc:
        logger.error(f"Firestore upload failed: {exc}")

    return url


def make_qr_array(url):
    """Return a BGR ndarray image of the QR code for the given URL."""
    try:
        import qrcode
        qr = qrcode.QRCode(border=2, box_size=10)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        arr = np.array(img)              # RGB
        return arr[:, :, ::-1].copy()    # to BGR for the display pipeline
    except Exception as exc:
        logger.error(f"QR generation failed: {exc}")
        return None
