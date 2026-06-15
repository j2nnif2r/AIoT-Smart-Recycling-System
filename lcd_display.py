import logging, time, os, datetime

os.environ.setdefault("SDL_VIDEODRIVER", "x11")
os.environ.setdefault("DISPLAY", ":0")
logger = logging.getLogger(__name__)

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    logger.warning("pygame not found - console output mode.")
    PYGAME_AVAILABLE = False

# ── Ivory theme ────────────────────────────────────────────────
BG_COLOR    = (244, 241, 232)
PANEL_COLOR = (235, 231, 220)
LINE_COLOR  = (50, 50, 50)
TEXT_DARK   = (30, 30, 30)
TEXT_GRAY   = (110, 105, 95)
BTN_COLOR   = (225, 220, 208)
BTN_BORDER  = (60, 60, 60)
ACCENT      = (40, 130, 90)

CATEGORY_COLORS = {
    "plastic": (30, 90, 170), "can": (185, 95, 20), "paper": (150, 120, 20),
    "glass": (20, 130, 110), "general": (90, 90, 90),
}

# CO2 saved per item by category (grams, approximate)
CO2_SAVED_G = {
    "plastic": 80, "can": 9, "paper": 18, "glass": 30, "general": 0,
}

# ── Multilingual strings ───────────────────────────────────────
LANGS = ["en", "ko", "zh", "ja"]
LANG_LABEL = {"en": "English", "ko": "한국어", "zh": "中文", "ja": "日本語"}

T = {
    "ready_title": {
        "en": "1-Min average statitics.", "ko": "1분 평균 통계",
        "zh": "1分钟平均统计", "ja": "1分間の平均統計",
    },
    "ready_sub": {
        "en": "Bring waste closer to the camera.", "ko": "쓰레기를 카메라 가까이 가져오세요.",
        "zh": "请将垃圾靠近摄像头。", "ja": "ゴミをカメラに近づけてください。",
    },
    "temp": {"en": "TEMP", "ko": "온도", "zh": "温度", "ja": "温度"},
    "humidity": {"en": "HUMIDITY", "ko": "습도", "zh": "湿度", "ja": "湿度"},
    "select_lang": {
        "en": "Select Language", "ko": "언어를 선택하세요",
        "zh": "请选择语言", "ja": "言語を選択してください",
    },
    "place_waste": {
        "en": "Place your waste", "ko": "쓰레기를 놓아주세요",
        "zh": "请放置垃圾", "ja": "ゴミを置いてください",
    },
    "in_zone": {
        "en": "in the scan zone", "ko": "스캔 구역 안에",
        "zh": "放在扫描区域内", "ja": "スキャンエリア内に",
    },
    "get_ready": {"en": "Get ready...", "ko": "준비하세요...", "zh": "准备...", "ja": "準備して..."},
    "capturing_in": {"en": "Capturing in", "ko": "촬영까지", "zh": "拍摄倒计时", "ja": "撮影まで"},
    "capturing": {"en": "Capturing...", "ko": "촬영 중...", "zh": "拍摄中...", "ja": "撮影中..."},
    "hold_still": {"en": "Hold still", "ko": "움직이지 마세요", "zh": "请保持不动", "ja": "動かないでください"},
    "no_detect": {
        "en": "No waste detected", "ko": "쓰레기를 인식하지 못했습니다",
        "zh": "未检测到垃圾", "ja": "ゴミを検出できません",
    },
    "try_again": {
        "en": "Try again with one item", "ko": "물건 하나만 다시 시도하세요",
        "zh": "请用单个物品重试", "ja": "一つの物で再試行してください",
    },
    "continue_q": {
        "en": "Dispose another item?", "ko": "계속 버리시겠습니까?",
        "zh": "继续投放垃圾吗？", "ja": "続けて捨てますか？",
    },
    "yes": {"en": "YES", "ko": "예", "zh": "是", "ja": "はい"},
    "no": {"en": "NO", "ko": "아니오", "zh": "否", "ja": "いいえ"},
    "summary_title": {
        "en": "Your Recycling Impact", "ko": "당신의 재활용 효과",
        "zh": "您的回收成果", "ja": "あなたのリサイクル成果",
    },
    "total_co2": {
        "en": "Total CO2 reduced", "ko": "총 CO2 절감량",
        "zh": "二氧化碳减排总量", "ja": "CO2削減量の合計",
    },
    "thanks": {
        "en": "Thank you for recycling correctly!", "ko": "올바른 분리수거에 동참해주셔서 감사합니다!",
        "zh": "感谢您正确分类回收！", "ja": "正しい分別にご協力ありがとうございます！",
    },
    "scan_qr": {
        "en": "Scan QR for your records", "ko": "QR을 스캔해 내 기록 보기",
        "zh": "扫描二维码查看记录", "ja": "QRをスキャンして記録を見る",
    },
    "enter_phone": {
        "en": "Enter last 4 digits of phone", "ko": "휴대폰 번호 뒷자리 4자리 입력",
        "zh": "请输入手机号后4位", "ja": "電話番号の下4桁を入力",
    },
    "disclaimer": {
        "en": "*this is a prediction with a ai model.", "ko": "*AI 모델의 예측 결과입니다.",
        "zh": "*这是AI模型的预测结果。", "ja": "*これはAIモデルによる予測です。",
    },
}

# Category display name + disposal hint per language
CATEGORY_NAME = {
    "plastic": {"en": "PLASTIC", "ko": "플라스틱", "zh": "塑料", "ja": "プラスチック"},
    "can":     {"en": "CAN / METAL", "ko": "캔 / 금속", "zh": "金属罐", "ja": "缶 / 金属"},
    "paper":   {"en": "PAPER", "ko": "종이", "zh": "纸类", "ja": "紙"},
    "glass":   {"en": "GLASS", "ko": "유리", "zh": "玻璃", "ja": "ガラス"},
    "general": {"en": "GENERAL WASTE", "ko": "일반 쓰레기", "zh": "一般垃圾", "ja": "一般ゴミ"},
}
DISPOSAL_HINT = {
    "plastic": {
        "en": "Empty, rinse, remove cap and label", "ko": "비우고 헹군 뒤 뚜껑과 라벨 제거",
        "zh": "清空冲洗，去除瓶盖和标签", "ja": "空にして洗い、キャップとラベルを外す",
    },
    "can": {
        "en": "Rinse and lightly crush", "ko": "헹군 뒤 가볍게 찌그러뜨리기",
        "zh": "冲洗后轻轻压扁", "ja": "すすいで軽くつぶす",
    },
    "paper": {
        "en": "Keep dry, flatten boxes", "ko": "물기 없이 상자는 펼쳐서",
        "zh": "保持干燥，压平纸箱", "ja": "乾いた状態で箱は平らに",
    },
    "glass": {
        "en": "Rinse, handle with care", "ko": "헹구고 깨지지 않게 주의",
        "zh": "冲洗，小心轻放", "ja": "すすいで割れないよう注意",
    },
    "general": {
        "en": "Use standard waste bag", "ko": "종량제 봉투에 배출",
        "zh": "使用标准垃圾袋", "ja": "標準のゴミ袋を使用",
    },
}
BIN_NAME = {
    "plastic": {"en": "PLASTIC BIN", "ko": "플라스틱 수거함", "zh": "塑料回收箱", "ja": "プラスチック箱"},
    "can":     {"en": "CAN / METAL BIN", "ko": "캔/금속 수거함", "zh": "金属回收箱", "ja": "缶/金属箱"},
    "paper":   {"en": "PAPER BIN", "ko": "종이 수거함", "zh": "纸类回收箱", "ja": "紙箱"},
    "glass":   {"en": "GLASS BIN", "ko": "유리 수거함", "zh": "玻璃回收箱", "ja": "ガラス箱"},
    "general": {"en": "GENERAL WASTE", "ko": "일반 쓰레기", "zh": "一般垃圾", "ja": "一般ゴミ"},
}


class LCDDisplay:
    def __init__(self, width=1024, height=600, fullscreen=True):
        self._w = width
        self._h = height
        self._fullscreen = fullscreen
        self._screen = None
        self._initialized = False
        self._buttons = []   # list of (rect, key) for touch hit-testing
        if PYGAME_AVAILABLE:
            self._init_pygame()

    def _init_pygame(self):
        try:
            pygame.init()
            if self._fullscreen:
                self._screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                self._screen = pygame.display.set_mode((self._w, self._h))
            self._w, self._h = self._screen.get_size()
            pygame.display.set_caption("IoT Team F Term Project")
            pygame.mouse.set_visible(True)   # touch needs visible cursor feedback
            self._init_fonts()
            self._initialized = True
            logger.info(f"pygame display {self._w}x{self._h}")
        except Exception as exc:
            logger.error(f"pygame init failed: {exc}")
            self._screen = None
            self._initialized = False

    def _font(self, size_ratio, bold=False):
        size = int(self._h * size_ratio)
        # Noto Sans CJK covers en/ko/zh/ja; fall back to freesans
        for name in ["notosanscjkkr", "notosanscjk", "notosanscjkjp"]:
            f = pygame.font.match_font(name)
            if f:
                return pygame.font.Font(f, size)
        return pygame.font.SysFont("freesans", size, bold=bold)

    def _init_fonts(self):
        self._f_xl = self._font(0.12, bold=True)
        self._f_l  = self._font(0.085)
        self._f_m  = self._font(0.050)
        self._f_s  = self._font(0.036)
        self._f_xs = self._font(0.028)

    # ── event / touch ────────────────────────────────────────
    def _pump(self):
        if not self._initialized:
            return
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.quit()
            pygame.display.flip()
        except Exception as exc:
            logger.error(f"pump error: {exc}")

    def wait_touch(self, timeout=None):
        """Block until a registered button is touched. Returns its key, or None on timeout."""
        if not self._initialized:
            time.sleep(0.5)
            return self._buttons[0][1] if self._buttons else None
        start = time.time()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit(); return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.quit(); return None
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    if event.type == pygame.FINGERDOWN:
                        pos = (int(event.x * self._w), int(event.y * self._h))
                    else:
                        pos = event.pos
                    for rect, key in self._buttons:
                        if rect.collidepoint(pos):
                            return key
            if timeout and (time.time() - start) > timeout:
                return None
            time.sleep(0.02)

    # ── screens ──────────────────────────────────────────────
    def write(self, line1, line2=""):
        if not self._initialized:
            print(f"[DISPLAY] {line1} | {line2}")
            return
        self._screen.fill(BG_COLOR)
        self._draw_header()
        self._center_text(line1, self._f_l, TEXT_DARK, int(self._h * 0.42))
        if line2:
            self._center_text(line2, self._f_m, TEXT_GRAY, int(self._h * 0.56))
        self._pump()

    def show_env(self, temp, hum, lang="en"):
        if not self._initialized:
            print(f"[ENV] Temp {temp:.1f}C  Humidity {hum:.1f}%")
            return
        self._screen.fill(BG_COLOR)
        self._draw_header()
        self._center_text(T["ready_title"][lang], self._f_m, TEXT_DARK, int(self._h * 0.17))
        self._center_text(T["ready_sub"][lang], self._f_m, TEXT_DARK, int(self._h * 0.24))
        cx = self._w // 2
        pygame.draw.line(self._screen, LINE_COLOR, (cx, int(self._h * 0.44)),
                         (cx, int(self._h * 0.84)), 2)
        self._center_text_x(T["temp"][lang], self._f_s, TEXT_GRAY, self._w // 4, int(self._h * 0.50))
        self._center_text_x(f"{temp:.1f} C", self._f_xl, TEXT_DARK, self._w // 4, int(self._h * 0.58))
        self._center_text_x(T["humidity"][lang], self._f_s, TEXT_GRAY, self._w * 3 // 4, int(self._h * 0.50))
        self._center_text_x(f"{hum:.1f} %", self._f_xl, TEXT_DARK, self._w * 3 // 4, int(self._h * 0.58))
        self._pump()

    def show_language_select(self):
        """Draw 4 language buttons. Returns nothing; call wait_touch() to get choice."""
        self._screen.fill(BG_COLOR)
        self._draw_header()
        self._center_text("Select Language / 언어 선택", self._f_m, TEXT_DARK, int(self._h * 0.16))
        self._buttons = []
        bw, bh = int(self._w * 0.38), int(self._h * 0.22)
        gap_x, gap_y = int(self._w * 0.04), int(self._h * 0.05)
        x0 = (self._w - (bw * 2 + gap_x)) // 2
        y0 = int(self._h * 0.30)
        positions = [(x0, y0), (x0 + bw + gap_x, y0),
                     (x0, y0 + bh + gap_y), (x0 + bw + gap_x, y0 + bh + gap_y)]
        for (bx, by), lang in zip(positions, LANGS):
            rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(self._screen, BTN_COLOR, rect, border_radius=14)
            pygame.draw.rect(self._screen, BTN_BORDER, rect, width=2, border_radius=14)
            self._center_text_x(LANG_LABEL[lang], self._f_l, TEXT_DARK,
                                bx + bw // 2, by + bh // 2 - int(self._h * 0.05))
            self._buttons.append((rect, lang))
        self._pump()

    def show_result(self, category, frame=None, lang="en"):
        bin_name = BIN_NAME.get(category, BIN_NAME["general"])[lang]
        hint     = DISPOSAL_HINT.get(category, DISPOSAL_HINT["general"])[lang]
        cat_name = CATEGORY_NAME.get(category, CATEGORY_NAME["general"])[lang]
        if not self._initialized:
            print(f"[RESULT] {category} -> {bin_name} / {hint}")
            return
        color = CATEGORY_COLORS.get(category, (90, 90, 90))
        self._screen.fill(BG_COLOR)
        self._draw_header()
        margin  = int(self._w * 0.03)
        top     = int(self._h * 0.16)
        photo_w = int(self._w * 0.46)
        photo_h = int(self._h * 0.66)
        px, py = margin, top
        pygame.draw.rect(self._screen, PANEL_COLOR, (px, py, photo_w, photo_h), border_radius=12)
        if frame is not None:
            surf = self._scale_fit(self._frame_to_surface(frame), photo_w - 12, photo_h - 12)
            rect = surf.get_rect(center=(px + photo_w // 2, py + photo_h // 2))
            self._screen.blit(surf, rect)
        pygame.draw.rect(self._screen, color, (px, py, photo_w, photo_h), width=3, border_radius=12)
        ix = px + photo_w + int(self._w * 0.04)
        iw = self._w - ix - margin
        self._screen.blit(self._f_xl.render(cat_name, True, color), (ix, top + int(self._h * 0.02)))
        self._screen.blit(self._f_m.render(f"> {bin_name}", True, TEXT_DARK), (ix, top + int(self._h * 0.26)))
        self._blit_wrapped(hint, self._f_s, TEXT_GRAY, ix, top + int(self._h * 0.40), iw)
        self._center_text(T["disclaimer"][lang], self._f_xs, TEXT_GRAY, int(self._h * 0.93))
        self._pump()

    def show_continue(self, lang="en"):
        """Yes/No screen. Returns nothing; call wait_touch() -> 'yes' or 'no'."""
        self._screen.fill(BG_COLOR)
        self._draw_header()
        self._center_text(T["continue_q"][lang], self._f_l, TEXT_DARK, int(self._h * 0.28))
        self._buttons = []
        bw, bh = int(self._w * 0.30), int(self._h * 0.26)
        gap = int(self._w * 0.08)
        x0 = (self._w - (bw * 2 + gap)) // 2
        y0 = int(self._h * 0.48)
        for i, (key, col) in enumerate([("yes", ACCENT), ("no", (170, 70, 60))]):
            bx = x0 + i * (bw + gap)
            rect = pygame.Rect(bx, y0, bw, bh)
            pygame.draw.rect(self._screen, BTN_COLOR, rect, border_radius=16)
            pygame.draw.rect(self._screen, col, rect, width=3, border_radius=16)
            self._center_text_x(T[key][lang], self._f_l, col, bx + bw // 2, y0 + bh // 2 - int(self._h * 0.05))
            self._buttons.append((rect, key))
        self._pump()

    def show_summary(self, counts, lang="en", qr_bgr=None):
        """Per-item bars + total CO2 + QR code linking to the user's web page."""
        if not self._initialized:
            total = sum(CO2_SAVED_G.get(k, 0) * v for k, v in counts.items())
            print(f"[SUMMARY] {dict(counts)} -> {total} g CO2")
            return
        self._screen.fill(BG_COLOR)
        self._draw_header()
        self._center_text(T["summary_title"][lang], self._f_l, ACCENT, int(self._h * 0.15))

        items = [(k, v) for k, v in counts.items() if v > 0]
        total = sum(CO2_SAVED_G.get(k, 0) * v for k, v in items)
        max_co2 = max([CO2_SAVED_G.get(k, 0) * v for k, v in items] + [1])

        bx = int(self._w * 0.06)
        bw_max = int(self._w * 0.34)
        y = int(self._h * 0.28)
        row_h = int(self._h * 0.095)
        for k, v in items:
            co2 = CO2_SAVED_G.get(k, 0) * v
            color = CATEGORY_COLORS.get(k, (90, 90, 90))
            name = CATEGORY_NAME.get(k, CATEGORY_NAME["general"])[lang]
            self._screen.blit(self._f_s.render(f"{name}  x{v}", True, TEXT_DARK), (bx, y))
            bar_y = y + int(row_h * 0.45)
            bar_len = int(bw_max * (co2 / max_co2))
            pygame.draw.rect(self._screen, color, (bx, bar_y, max(bar_len, 4), int(row_h * 0.30)), border_radius=6)
            self._screen.blit(self._f_s.render(f"{co2} g", True, TEXT_GRAY),
                              (bx + max(bar_len, 4) + 10, bar_y - int(self._h * 0.004)))
            y += row_h

        # total CO2 (middle)
        mx = int(self._w * 0.50)
        self._center_text_x(T["total_co2"][lang], self._f_s, TEXT_GRAY, mx, int(self._h * 0.30))
        self._center_text_x(f"{total} g", self._f_xl, ACCENT, mx, int(self._h * 0.40))
        self._center_text_x("CO2", self._f_m, ACCENT, mx, int(self._h * 0.54))

        # QR code (right side)
        if qr_bgr is not None:
            qx = int(self._w * 0.80)
            qy = int(self._h * 0.40)
            qsize = int(self._h * 0.34)
            self._blit_qr(qr_bgr, qx, qy, qsize)
            self._center_text_x(T["scan_qr"][lang], self._f_xs, TEXT_DARK, qx, qy + qsize // 2 + int(self._h * 0.03))

        self._blit_wrapped_center(T["thanks"][lang], self._f_s, TEXT_DARK,
                                  int(self._h * 0.90), int(self._w * 0.9))
        self._pump()

    def show_keypad(self, lang="en", current=""):
        """Numeric keypad for phone last-4 entry. Registers digit/back/ok buttons."""
        self._screen.fill(BG_COLOR)
        self._draw_header()
        self._center_text(T["enter_phone"][lang], self._f_m, TEXT_DARK, int(self._h * 0.15))
        # current input display
        shown = current + "_" * (4 - len(current))
        self._center_text("  ".join(shown), self._f_xl, ACCENT, int(self._h * 0.24))

        self._buttons = []
        keys = ["1","2","3","4","5","6","7","8","9","back","0","ok"]
        cols, rows = 3, 4
        gw, gh = int(self._w * 0.16), int(self._h * 0.13)
        gap_x, gap_y = int(self._w * 0.03), int(self._h * 0.02)
        total_w = cols * gw + (cols - 1) * gap_x
        x0 = (self._w - total_w) // 2
        y0 = int(self._h * 0.40)
        for i, k in enumerate(keys):
            r, c = divmod(i, cols)
            bx = x0 + c * (gw + gap_x)
            by = y0 + r * (gh + gap_y)
            rect = pygame.Rect(bx, by, gw, gh)
            col = ACCENT if k == "ok" else ((170,70,60) if k == "back" else BTN_BORDER)
            pygame.draw.rect(self._screen, BTN_COLOR, rect, border_radius=12)
            pygame.draw.rect(self._screen, col, rect, width=2, border_radius=12)
            label = {"back": "DEL", "ok": "OK"}.get(k, k)
            self._center_text_x(label, self._f_l, col, bx + gw // 2, by + gh // 2 - int(self._h * 0.045))
            self._buttons.append((rect, k))
        self._pump()

    def _blit_qr(self, qr_bgr, cx, cy, size):
        surf = self._frame_to_surface(qr_bgr)
        surf = pygame.transform.smoothscale(surf, (size, size))
        self._screen.blit(surf, (cx - size // 2, cy - size // 2))

    def clear(self):
        if self._initialized:
            self._screen.fill(BG_COLOR)
            self._pump()

    def quit(self):
        if PYGAME_AVAILABLE:
            pygame.quit()
        self._initialized = False

    # ── helpers ──────────────────────────────────────────────
    def _frame_to_surface(self, frame, swap_rb=True):
        import numpy as np
        arr = np.ascontiguousarray(frame[:, :, ::-1]) if swap_rb else np.ascontiguousarray(frame)
        h, w = arr.shape[:2]
        return pygame.image.frombuffer(arr.tobytes(), (w, h), "RGB")

    def _scale_fit(self, surf, maxw, maxh):
        w, h = surf.get_size()
        s = min(maxw / w, maxh / h)
        return pygame.transform.smoothscale(surf, (int(w * s), int(h * s)))

    def _blit_wrapped(self, text, font, color, x, y, maxw):
        line, yy = "", y
        for word in text.split():
            test = (line + " " + word).strip()
            if font.size(test)[0] <= maxw:
                line = test
            else:
                self._screen.blit(font.render(line, True, color), (x, yy))
                yy += int(font.get_height() * 1.2); line = word
        if line:
            self._screen.blit(font.render(line, True, color), (x, yy))

    def _blit_wrapped_center(self, text, font, color, y, maxw):
        lines, line = [], ""
        for word in text.split():
            test = (line + " " + word).strip()
            if font.size(test)[0] <= maxw:
                line = test
            else:
                lines.append(line); line = word
        if line:
            lines.append(line)
        yy = y
        for ln in lines:
            s = font.render(ln, True, color)
            self._screen.blit(s, ((self._w - s.get_width()) // 2, yy))
            yy += int(font.get_height() * 1.2)

    def _center_text(self, text, font, color, y):
        s = font.render(text, True, color)
        self._screen.blit(s, ((self._w - s.get_width()) // 2, y))

    def _center_text_x(self, text, font, color, cx, y):
        s = font.render(text, True, color)
        self._screen.blit(s, (cx - s.get_width() // 2, y))

    def _draw_header(self):
        bar_h = int(self._h * 0.10)
        pygame.draw.rect(self._screen, PANEL_COLOR, (0, 0, self._w, bar_h))
        pygame.draw.line(self._screen, LINE_COLOR, (0, bar_h), (self._w, bar_h), 2)
        title = self._f_s.render("IoT Team F Term Project", True, TEXT_DARK)
        self._screen.blit(title, (int(self._w * 0.02), (bar_h - title.get_height()) // 2))
        now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        ts = self._f_xs.render(now, True, TEXT_GRAY)
        self._screen.blit(ts, (self._w - ts.get_width() - int(self._w * 0.02),
                               (bar_h - ts.get_height()) // 2))
