
from __future__ import annotations

__app_name__ = "QSnap"
__version__ = "1.1.0"
__author__ = "QwejayHuang"
__company__ = "Qwesoft"
__description__ = "Modern Cross-Platform Python Snipping Tool Powered by RapidOCR"

import ctypes
import json
import logging
import math
import os
import struct
import sys
import time
import wave
from ctypes import wintypes
from pathlib import Path

os.environ["QT_LOGGING_RULES"] = "qt.text.font.db=false;qt.multimedia*=false;qt.qpa.window=false"

if os.name == "nt":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

try:
    from rapidocr_onnxruntime import RapidOCR
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

from PySide6.QtCore import (
    QByteArray,
    QBuffer,
    QIODevice,
    QObject,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    Qt,
    QThread,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QFont,
    QGuiApplication,
    QIcon,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QKeySequenceEdit,
    QScrollArea,
)

logger = logging.getLogger(__app_name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

_APP_DIR = Path(sys.argv[0]).parent if getattr(sys.argv, 'frozen', False) else Path(__file__).parent
_PORTABLE_CONFIG = _APP_DIR / "config.json"

if _PORTABLE_CONFIG.exists():
    _CONFIG_DIR = _APP_DIR
    _CONFIG_FILE = _PORTABLE_CONFIG
    logger.info("Running in Portable Mode.")
else:
    _CONFIG_DIR = Path.home() / f".{__app_name__.lower()}"
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE = _CONFIG_DIR / "config.json"

_GLOBAL_OCR_ENGINE = None
def get_ocr_engine():
    global _GLOBAL_OCR_ENGINE
    if _GLOBAL_OCR_ENGINE is None and HAS_OCR:
        _GLOBAL_OCR_ENGINE = RapidOCR()
    return _GLOBAL_OCR_ENGINE


MATERIAL_ICONS = {
    "rect": "M3 3h18v18H3V3zm16 16V5H5v14h14z",
    "circle": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z",
    "arrow": "M19 12l-7-7v4H5v6h7v4z",
    "line": "M3 13h18v-2H3v2z M21 5L3 19l1.4 1.4L22.4 6.4z",
    "pencil": "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z",
    "marker": "M15.5 2.5l6 6-12 12H3.5v-6l12-12zm-2 4L5.5 14.5v4h4L17.5 10.5l-4-4z",
    "text": "M5 4v3h5.5v12h3V7H19V4H5z",
    "mosaic": "M3 3h4v4H3zm7 0h4v4h-4zm7 0h4v4h-4zM3 10h4v4H3zm7 0h4v4h-4zm7 0h4v4h-4zM3 17h4v4H3zm7 0h4v4h-4zm7 0h4v4h-4z",
    "badge": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15v-6h2v6h-2zm0-8V7h2v2h-2z",
    "undo": "M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z",
    "pin": "M16 9V4l1 0V2H7v2l1 0v5c0 1.66-1.34 3-3 3v2h5.97v7l1 1 1-1v-7H19v-2c-1.66 0-3-1.34-3-3z",
    "save": "M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z",
    "close": "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z",
    "check": "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z",
    "aspect_ratio": "M19 12h-2v3h-3v2h5v-5zM7 9h3V7H5v5h2V9zm14-6H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z",
    "palette": "M12 22C6.49 22 2 17.51 2 12S6.49 2 12 2s10 4.49 10 10c0 1.38-1.12 2.5-2.5 2.5-.59 0-1.13-.21-1.55-.59-.36-.33-.86-.56-1.45-.56-1.38 0-2.5 1.12-2.5 2.5v.65C14 19.54 11.54 22 12 22z",
    "picker": "M20.71 5.63l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-3.12 3.12-1.93-1.91-1.41 1.41 1.42 1.42L3 16.25V21h4.75l8.92-8.92 1.42 1.42 1.41-1.41-1.92-1.92 3.12-3.12c.4-.4.4-1.03.01-1.42zM6.92 19L5 17.08l8.06-8.06 1.92 1.92L6.92 19z",
    "ocr": "M3 4v4h2V6h4V4H3zm18 0h-6v2h4v2h2V4zM3 20v-4H1v6h6v-2H3zm18-4h-2v4h-4v2h6v-6zm-4-9H7v10h10V7z",
    "settings": "M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.06-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.73,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.06,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.43-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.49-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z",
}

def get_svg_icon(name: str, color: str = "#475569", size: int = 24) -> QIcon:
    path_data = MATERIAL_ICONS.get(name, MATERIAL_ICONS["rect"])
    svg_str = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="{color}" d="{path_data}"/></svg>'
    renderer = QSvgRenderer()
    renderer.load(svg_str.encode("utf-8"))
    render_size = max(size * 4, 96)
    pixmap = QPixmap(render_size, render_size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

def get_logo_icon(size: int = 24) -> QIcon:
    """渲染具有大厂风格的现代渐变专属 Logo"""
    svg_str = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <defs>
            <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#3b82f6" />
                <stop offset="100%" stop-color="#1d4ed8" />
            </linearGradient>
        </defs>
        <rect width="22" height="22" x="1" y="1" rx="6" fill="url(#bg)"/>
        <path d="M7 10V7h3M14 7h3v3M17 14v3h-3M10 17H7v-3" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="12" r="2.2" fill="#ffffff"/>
    </svg>
    """
    renderer = QSvgRenderer()
    renderer.load(svg_str.encode("utf-8"))
    render_size = max(size * 4, 96)
    pixmap = QPixmap(render_size, render_size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

class Config:
    def __init__(self):
        self.data = {
            "last_save_dir": str(Path.home() / "Pictures"),
            "enable_sound": True,
            "auto_copy": True,
            "show_magnifier": True,
            "auto_detect_window": True,
            "pen_width": 3,
            "default_color": "#ea4335",
            "custom_color": "#8ab4f8",
            "hotkey": "Ctrl+Alt+A",
        }
        self.load()

    def load(self):
        if _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
            except Exception as e:
                logger.warning(f"Failed to load configuration: {e}")

    def save(self):
        try:
            temp_file = _CONFIG_FILE.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            temp_file.replace(_CONFIG_FILE)
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value
        self.save()

_config = Config()

def _parse_hotkey(hk_str: str) -> tuple[int, int]:
    hk_str = hk_str.split(',')[0].strip().upper().replace(' ', '')
    modifiers = 0
    vk = 0
    if "CTRL" in hk_str: modifiers |= 0x0002
    if "ALT" in hk_str: modifiers |= 0x0001
    if "SHIFT" in hk_str: modifiers |= 0x0004
    if "WIN" in hk_str or "META" in hk_str: modifiers |= 0x0008
    
    parts = hk_str.split('+')
    if not parts:
        return 0, 0
    last_part = parts[-1]
    
    if len(last_part) == 1:
        vk = ord(last_part)
    elif last_part.startswith('F') and last_part[1:].isdigit():
        num = int(last_part[1:])
        if 1 <= num <= 24:
            vk = 0x6F + num
    return modifiers, vk

def check_hotkey_conflict_win(hk_str: str) -> tuple[bool, str]:
    if os.name != "nt":
        return True, ""
    modifiers, vk = _parse_hotkey(hk_str)
    if vk == 0:
        return False, "无效或不受支持的快捷键组合，请包含字母或功能键。"
    user32 = ctypes.windll.user32
    test_id = 0x1337
    if user32.RegisterHotKey(None, test_id, modifiers, vk):
        user32.UnregisterHotKey(None, test_id)
        return True, ""
    return False, f"快捷键组合 {hk_str} 已被占用，请尝试其他组合。"

def check_autostart_win() -> bool:
    if os.name != "nt":
        return False
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, __app_name__)
        winreg.CloseKey(key)
        return val == sys.argv[0]
    except Exception:
        return False

def set_autostart_win(enable: bool):
    if os.name != "nt":
        return
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, __app_name__, 0, winreg.REG_SZ, sys.argv[0])
        else:
            try:
                winreg.DeleteValue(key, __app_name__)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        logger.error(f"Failed to set autostart: {e}")

def play_shutter_sound():
    if not _config.get("enable_sound", True):
        return
    try:
        shutter_wav = _CONFIG_DIR / "shutter.wav"
        if not shutter_wav.exists():
            sample_rate, duration = 44100, 0.12
            n_samples = int(sample_rate * duration)
            samples = [0.0] * n_samples
            for i in range(n_samples):
                t = i / sample_rate
                click1 = math.sin(2 * math.pi * 1800 * t) * math.exp(-70 * t)
                click2 = (math.sin(2 * math.pi * 1200 * (t - 0.04)) * math.exp(-60 * (t - 0.04)) if t > 0.04 else 0.0)
                samples[i] = (click1 * 0.7 + click2 * 0.5) * 0.35
            with wave.open(shutter_wav.as_posix(), "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                packed = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples)
                wf.writeframes(packed)
        if os.name == "nt":
            import winsound
            winsound.PlaySound(shutter_wav.as_posix(), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    except Exception as e:
        logger.debug(f"Audio playback skipped: {e}")

if os.name == "nt":
    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

    def get_window_rects(virtual_top_left: QPoint, dpr: float) -> list[QRect]:
        rects = []
        user32 = ctypes.windll.user32
        dwmapi = ctypes.windll.dwmapi

        def callback(hwnd, _):
            if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
                return True
            
            cloaked = ctypes.c_int(0)
            DWMWA_CLOAKED = 14
            dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
            if cloaked.value != 0:
                return True

            rect = RECT()
            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                rx = int(rect.left / dpr) - virtual_top_left.x()
                ry = int(rect.top / dpr) - virtual_top_left.y()
                w = int((rect.right - rect.left) / dpr)
                h = int((rect.bottom - rect.top) / dpr)
                if w > 80 and h > 80:
                    rects.append(QRect(rx, ry, w, h))
            return True

        try:
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            user32.EnumWindows(EnumWindowsProc(callback), 0)
        except Exception:
            pass
        return rects
else:
    def get_window_rects(virtual_top_left: QPoint, dpr: float) -> list[QRect]:
        return []

class DrawItem:
    def paint(self, painter: QPainter, base_pixmap: QPixmap = None):
        pass

class RectItem(DrawItem):
    def __init__(self, rect: QRectF, color: QColor, width: int = 2):
        self.rect, self.color, self.width = rect, color, width
    def paint(self, painter: QPainter, base_pixmap: QPixmap = None):
        painter.save()
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect)
        painter.restore()

class CircleItem(DrawItem):
    def __init__(self, rect: QRectF, color: QColor, width: int = 2):
        self.rect, self.color, self.width = rect, color, width
    def paint(self, painter: QPainter, base_pixmap: QPixmap = None):
        painter.save()
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(self.rect)
        painter.restore()

class LineItem(DrawItem):
    def __init__(self, start: QPointF, end: QPointF, color: QColor, width: int = 3):
        self.start, self.end, self.color, self.width = start, end, color, width
    def paint(self, painter: QPainter, base_pixmap: QPixmap = None):
        painter.save()
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(self.start, self.end)
        painter.restore()

class ArrowItem(DrawItem):
    def __init__(self, start: QPointF, end: QPointF, color: QColor, width: int = 3):
        self.start, self.end, self.color, self.width = start, end, color, width
    def paint(self, painter: QPainter, base_pixmap: QPixmap = None):
        painter.save()
        painter.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(QBrush(self.color))
        painter.drawLine(self.start, self.end)
        dx, dy = self.end.x() - self.start.x(), self.end.y() - self.start.y()
        if math.hypot(dx, dy) > 6:
            arrow_size = min(18.0, max(12.0, self.width * 3.6))
            angle = math.atan2(dy, dx)
            p1 = self.end - QPointF(arrow_size * math.cos(angle - math.pi / 6), arrow_size * math.sin(angle - math.pi / 6))
            p2 = self.end - QPointF(arrow_size * math.cos(angle + math.pi / 6), arrow_size * math.sin(angle + math.pi / 6))
            painter.drawPolygon(QPolygonF([self.end, p1, p2]))
        painter.restore()

class PencilItem(DrawItem):
    def __init__(self, points: list[QPointF], color: QColor, width: int = 3, is_marker=False):
        self.points, self.color, self.width, self.is_marker = list(points), color, width, is_marker
    def paint(self, painter: QPainter, base_pixmap: QPixmap = None):
        if len(self.points) < 2:
            return
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        c = QColor(self.color)
        if self.is_marker:
            c.setAlpha(110)
            painter.setPen(QPen(c, self.width * 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.BevelJoin))
        else:
            painter.setPen(QPen(c, self.width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        painter.drawPath(path)
        painter.restore()

class StepBadgeItem(DrawItem):
    def __init__(self, pos: QPointF, step_num: int, color: QColor):
        self.pos, self.step_num, self.color, self.radius = pos, step_num, color, 13.0
    def paint(self, painter: QPainter, base_pixmap: QPixmap = None):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(self.pos, self.radius, self.radius)
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(
            QRectF(self.pos.x() - self.radius, self.pos.y() - self.radius, self.radius * 2, self.radius * 2),
            Qt.AlignmentFlag.AlignCenter,
            str(self.step_num),
        )
        painter.restore()

class TextItem(DrawItem):
    def __init__(self, pos: QPointF, text: str, color: QColor, font_size=13):
        self.pos, self.text, self.color, self.font_size = pos, text, color, font_size
    def paint(self, painter: QPainter, base_pixmap: QPixmap = None):
        if not self.text:
            return
        painter.save()
        painter.setPen(self.color)
        font = QFont("Microsoft YaHei", self.font_size, QFont.Weight.Bold)
        painter.setFont(font)
        fm = painter.fontMetrics()
        lines = self.text.split("\n")
        curr_y = self.pos.y()
        for line in lines:
            painter.drawText(int(self.pos.x()), int(curr_y), line)
            curr_y += fm.height()
        painter.restore()

class MosaicItem(DrawItem):
    def __init__(self, rect: QRectF, block_size: int = 12):
        self.rect, self.block_size = rect, block_size
        self._cached_pixmap: QPixmap | None = None
        self._cached_rect: QRect = QRect()

    def paint(self, painter: QPainter, base_pixmap: QPixmap = None):
        if base_pixmap is None or self.rect.isEmpty():
            return
        r = self.rect.toRect()
        if r != self._cached_rect or self._cached_pixmap is None:
            dpr = base_pixmap.devicePixelRatio()
            phys_rect = QRect(int(r.x() * dpr), int(r.y() * dpr), int(r.width() * dpr), int(r.height() * dpr))
            cropped = base_pixmap.copy(phys_rect)
            
            if not cropped.isNull():
                sw = max(1, phys_rect.width() // self.block_size)
                sh = max(1, phys_rect.height() // self.block_size)
                
                cropped.setDevicePixelRatio(1.0)
                
                scaled_down = cropped.scaled(sw, sh, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
                scaled_up = scaled_down.scaled(phys_rect.width(), phys_rect.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
                
                scaled_up.setDevicePixelRatio(dpr)
                self._cached_pixmap = scaled_up
                self._cached_rect = r
                
        if self._cached_pixmap:
            painter.save()
            painter.drawPixmap(r.topLeft(), self._cached_pixmap)
            painter.restore()

class PinnedImageWidget(QWidget):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.original_pixmap = pixmap
        self.scale_factor = 1.0
        self.opacity = 1.0
        self.drag_pos = QPoint()
        
        dpr = pixmap.devicePixelRatio()
        self.setFixedSize(int(pixmap.width() / dpr), int(pixmap.height() / dpr))
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setOpacity(self.opacity)
        painter.drawPixmap(self.rect(), self.original_pixmap)
        painter.setPen(QPen(QColor(255, 255, 255, 140), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def _show_context_menu(self, global_pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background: #ffffff; border: 1px solid #e8eaed; border-radius: 8px; padding: 4px; }
            QMenu::item { padding: 6px 18px; border-radius: 4px; color: #3c4043; font-size: 12px; }
            QMenu::item:selected { background: #e8f0fe; color: #1a73e8; }
        """)
        menu.addAction("复制图片", lambda: QApplication.clipboard().setPixmap(self.original_pixmap))
        menu.addAction("恢复 100% 大小", lambda: self._reset_scale())
        menu.addSeparator()
        menu.addAction("关闭贴图 (Esc / 双击)", self.close)
        menu.exec(global_pos)

    def _reset_scale(self):
        self.scale_factor = 1.0
        dpr = self.original_pixmap.devicePixelRatio()
        self.setFixedSize(int(self.original_pixmap.width() / dpr), int(self.original_pixmap.height() / dpr))

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(self.mapToGlobal(event.position().toPoint()) - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.opacity = min(1.0, max(0.15, self.opacity + (0.05 if delta > 0 else -0.05)))
            self.update()
        else:
            self.scale_factor = max(0.15, min(5.0, self.scale_factor * (1.1 if delta > 0 else 0.9)))
            dpr = self.original_pixmap.devicePixelRatio()
            base_w = self.original_pixmap.width() / dpr
            base_h = self.original_pixmap.height() / dpr
            new_w = max(30, int(base_w * self.scale_factor))
            new_h = max(30, int(base_h * self.scale_factor))
            self.setFixedSize(new_w, new_h)

    def mouseDoubleClickEvent(self, event):
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

class OCRWorker(QThread):
    finished = Signal(str, bool)

    def __init__(self, img_bytes: bytes):
        super().__init__()
        self.img_bytes = img_bytes
        self._is_cancelled = False

    def run(self):
        try:
            ocr = get_ocr_engine()
            if self._is_cancelled or not ocr:
                return
            result, _ = ocr(self.img_bytes)
            if self._is_cancelled:
                return
            if result:
                lines_data = []
                for res in result:
                    box = res[0]
                    text = res[1]
                    xs = [p[0] for p in box]
                    ys = [p[1] for p in box]
                    lines_data.append({
                        "text": text,
                        "x": min(xs),
                        "y": sum(ys) / 4.0, 
                        "h": max(ys) - min(ys)
                    })
                
                lines_data.sort(key=lambda item: item["y"])
                
                grouped_lines = []
                current_line = []
                
                for item in lines_data:
                    if not current_line:
                        current_line.append(item)
                    else:
                        avg_y = sum(b["y"] for b in current_line) / len(current_line)
                        if abs(item["y"] - avg_y) < item["h"] * 0.6:
                            current_line.append(item)
                        else:
                            current_line.sort(key=lambda b: b["x"])
                            grouped_lines.append(" ".join(b["text"] for b in current_line))
                            current_line = [item]
                
                if current_line:
                    current_line.sort(key=lambda b: b["x"])
                    grouped_lines.append(" ".join(b["text"] for b in current_line))
                    
                final_text = "\n".join(grouped_lines)
                self.finished.emit(final_text, True)
            else:
                self.finished.emit("未识别到文字，请确保选区清晰。", False)
        except Exception as e:
            self.finished.emit(f"OCR 引擎错误:\n{str(e)}", False)

    def cancel(self):
        self._is_cancelled = True

class OCRDialog(QDialog):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{__app_name__} - 文字提取 (OCR)")
        self.resize(520, 360)
        self.worker: OCRWorker | None = None
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QTextEdit { background: #ffffff; border: 1px solid #e8eaed; border-radius: 8px; padding: 10px; font-size: 13px; color: #202124; line-height: 1.5; }
            QPushButton { background: #1a73e8; color: #ffffff; border-radius: 6px; padding: 8px 16px; font-weight: bold; border: none; }
            QPushButton:hover { background: #1557b0; }
            QPushButton:disabled { background: #dadce0; color: #80868b; }
        """)
        lay = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        lay.addWidget(self.text_edit)

        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        self.copy_btn = QPushButton("复制识别结果")
        self.copy_btn.clicked.connect(self._copy_and_close)
        btn_lay.addWidget(self.copy_btn)
        lay.addLayout(btn_lay)

        self._process_ocr(pixmap)

    def _process_ocr(self, pixmap: QPixmap):
        if not HAS_OCR:
            self.text_edit.setHtml(f"""
                <h3 style="color:#ea4335;">未检测到 RapidOCR 识别组件</h3>
                <p>{__app_name__} 支持完全本地化、隐私安全的轻量 OCR 引擎。</p>
                <p>请在终端运行命令安装：</p>
                <pre style="background:#e8eaed; padding:8px; border-radius:4px; font-family:Consolas;">pip install rapidocr-onnxruntime</pre>
            """)
            self.copy_btn.hide()
            return

        self.text_edit.setText("⚡ 正在执行本地 OCR 识别，请稍候...")
        self.copy_btn.setEnabled(False)

        buffer = QByteArray()
        buf_io = QBuffer(buffer)
        buf_io.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buf_io, "PNG")

        self.worker = OCRWorker(bytes(buffer.data()))
        self.worker.finished.connect(self._on_ocr_finished)
        self.worker.start()

    def _on_ocr_finished(self, text: str, success: bool):
        self.text_edit.setText(text)
        if success:
            self.copy_btn.setEnabled(True)
            self.copy_btn.show()
        else:
            self.copy_btn.hide()

    def _copy_and_close(self):
        QApplication.clipboard().setText(self.text_edit.toPlainText())
        self.close()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.quit()
            self.worker.wait(200)
        super().closeEvent(event)

class ShortcutHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QDialog { background: transparent; }
            QFrame#HelpCard { background: rgba(30, 41, 59, 235); border-radius: 12px; padding: 16px; border: 1px solid rgba(255,255,255,40); }
            QLabel { color: #f1f5f9; font-size: 12px; }
            QLabel#Title { font-size: 14px; font-weight: bold; color: #60a5fa; }
            QLabel#Key { background: #334155; padding: 3px 8px; border-radius: 4px; font-family: Consolas; font-weight: bold; }
        """)
        self.card = QFrame()
        self.card.setObjectName("HelpCard")
        lay = QVBoxLayout(self.card)
        lay.setSpacing(8)
        title = QLabel(f"⌨ {__app_name__} 快捷键指南")
        title.setObjectName("Title")
        lay.addWidget(title)
        shortcuts = [
            ("Esc / 右键", "取消 / 返回上一状态"),
            ("Enter / 双击", "完成截图并复制"),
            ("Ctrl + S", "保存图片到本地"),
            ("Ctrl + Z", "撤销上一标注"),
            ("F3", "贴图到屏幕 (可缩放/调透明度)"),
            ("C", "吸管取色 (复制HEX并选中颜色)"),
            ("R / O / L / A", "矩形 / 椭圆 / 直线 / 箭头"),
            ("P / H / T", "画笔 / 荧光笔 / 文本标注"),
            ("B / M", "步骤序号 / 马赛克遮盖"),
            ("1 / 2 / 3", "切换笔刷粗细 (细/中/粗)"),
        ]
        for key, desc in shortcuts:
            row = QHBoxLayout()
            row.setSpacing(8)
            k_label = QLabel(key)
            k_label.setObjectName("Key")
            k_label.setFixedWidth(130)
            row.addWidget(k_label)
            row.addWidget(QLabel(desc))
            row.addStretch()
            lay.addLayout(row)
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.addWidget(self.card)

    def mousePressEvent(self, event):
        self.close()

class FloatingToolBar(QWidget):
    tool_changed = Signal(str)
    color_changed = Signal(QColor)
    width_changed = Signal(int)
    action_triggered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.inner_frame = QFrame(self)
        self.inner_frame.setObjectName("ToolBar")
        self.inner_frame.setStyleSheet("""
            QFrame#ToolBar { background-color: #ffffff; border: 1px solid #e8eaed; border-radius: 12px; }
            QPushButton#ToolBtn, QPushButton#ActionBtn { 
                background-color: transparent; border: none; border-radius: 6px; 
                padding: 4px; min-width: 26px; min-height: 26px; 
            }
            QPushButton#ToolBtn:hover, QPushButton#ActionBtn:hover { background-color: #f1f3f4; }
            QPushButton#ToolBtn:checked { background-color: #e8f0fe; border: 1px solid #d2e3fc; }
            QFrame#Sep { background-color: #dadce0; width: 1px; max-width: 1px; margin: 6px 2px; }
            QPushButton#WidthBtn { 
                background-color: transparent; border: none; border-radius: 6px; 
                min-width: 24px; min-height: 24px; font-size: 11px; font-weight: bold; color: #5f6368; 
            }
            QPushButton#WidthBtn:checked { color: #1a73e8; background-color: #e8f0fe; border: 1px solid #d2e3fc;}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 35))
        shadow.setOffset(0, 3)
        self.inner_frame.setGraphicsEffect(shadow)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(10, 10, 10, 10)
        main_lay.addWidget(self.inner_frame)

        self.init_ui()

    def _color_btn_css(self, hex_color: str):
        border_c = "rgba(0,0,0,0.15)" if hex_color.lower() != "#ffffff" else "rgba(0,0,0,0.35)"
        return f"""
            QPushButton#ColorBtn {{ 
                background-color: {hex_color}; 
                border: 1px solid {border_c}; 
                border-radius: 8px; 
                min-width: 16px; max-width: 16px; 
                min-height: 16px; max-height: 16px;
                margin: 2px; padding: 0px;
            }}
            QPushButton#ColorBtn:hover {{ border: 1px solid rgba(0,0,0,0.6); }}
            QPushButton#ColorBtn:checked {{ border: 2px solid #1a73e8; }}
        """

    def init_ui(self):
        lay = QHBoxLayout(self.inner_frame)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(2)

        self.btn_group = []
        tools = [
            ("rect", "矩形 (R)"),
            ("circle", "椭圆 (O)"),
            ("line", "直线 (L)"),
            ("arrow", "箭头 (A)"),
            ("pencil", "画笔 (P)"),
            ("marker", "荧光笔 (H)"),
            ("text", "文本标注 (T)"),
            ("badge", "步骤序号 (B)"),
            ("mosaic", "马赛克 (M)"),
        ]
        for icon_key, tip in tools:
            btn = QPushButton()
            btn.setObjectName("ToolBtn")
            btn.setIcon(get_svg_icon(icon_key, "#475569", 18))
            btn.setCheckable(True)
            btn.setToolTip(tip)
            btn.clicked.connect(lambda chk, t=icon_key: self._on_tool_btn_clicked(t))
            lay.addWidget(btn)
            self.btn_group.append((icon_key, btn))

        lay.addWidget(QFrame(objectName="Sep"))

        self.width_group = QButtonGroup(self)
        self.current_width = _config.get("pen_width", 3)
        for i, (w, label) in enumerate([(2, "细"), (3, "中"), (5, "粗")]):
            btn = QPushButton(label)
            btn.setObjectName("WidthBtn")
            btn.setCheckable(True)
            btn.setToolTip(f"笔刷粗细: {label} ({i+1})")
            btn.clicked.connect(lambda chk, width=w: self._on_width_changed(width))
            self.width_group.addButton(btn, w)
            lay.addWidget(btn)
            if w == self.current_width:
                btn.setChecked(True)

        lay.addWidget(QFrame(objectName="Sep"))

        self.picker_btn = QPushButton()
        self.picker_btn.setObjectName("ToolBtn")
        self.picker_btn.setIcon(get_svg_icon("picker", "#5f6368", 18))
        self.picker_btn.setToolTip("屏幕吸管取色 (C)")
        self.picker_btn.setCheckable(True)
        self.picker_btn.clicked.connect(lambda chk: self._on_tool_btn_clicked("picker"))
        lay.addWidget(self.picker_btn)
        self.btn_group.append(("picker", self.picker_btn))

        self.color_group = QButtonGroup(self)
        self.preset_hexes = ["#ea4335", "#fbbc04", "#34a853", "#4285f4", "#000000", "#ffffff"]
        self.color_btns = {}

        for i, hx in enumerate(self.preset_hexes):
            btn = QPushButton()
            btn.setObjectName("ColorBtn")
            btn.setCheckable(True)
            btn.setStyleSheet(self._color_btn_css(hx))
            btn.clicked.connect(lambda chk, c=hx: self._set_color(QColor(c)))
            self.color_group.addButton(btn, i)
            lay.addWidget(btn)
            self.color_btns[hx] = btn

        self.custom_hex = _config.get("custom_color", "#8ab4f8").lower()
        self.custom_btn = QPushButton()
        self.custom_btn.setObjectName("ColorBtn")
        self.custom_btn.setCheckable(True)
        self.custom_btn.setToolTip("当前拾取/自定义颜色")
        self.custom_btn.setStyleSheet(self._color_btn_css(self.custom_hex))
        self.custom_btn.clicked.connect(lambda chk: self._set_color(QColor(self.custom_hex)))
        self.color_group.addButton(self.custom_btn, 99)
        lay.addWidget(self.custom_btn)

        self.palette_btn = QPushButton()
        self.palette_btn.setObjectName("ActionBtn")
        self.palette_btn.setIcon(get_svg_icon("palette", "#1a73e8", 18))
        self.palette_btn.setToolTip("选择调色板颜色")
        self.palette_btn.clicked.connect(self._select_custom_color)
        lay.addWidget(self.palette_btn)

        self.current_color = QColor(_config.get("default_color", "#ea4335"))
        self._sync_color_ui(self.current_color.name().lower())

        lay.addWidget(QFrame(objectName="Sep"))

        actions = [
            ("undo", "撤销标注 (Ctrl+Z)", "undo", "#5f6368"),
            ("aspect_ratio", "锁定比例模式", "aspect", "#5f6368"),
            ("ocr", "提取选区文字 (OCR)", "ocr", "#1a73e8"),
            ("pin", "钉在屏幕上 (F3)", "pin", "#5f6368"),
            ("save", "保存至文件 (Ctrl+S)", "save", "#5f6368"),
            ("close", "取消 (Esc)", "close", "#ea4335"),
            ("check", "完成并复制 (Enter / 双击)", "finish", "#34a853"),
        ]
        for icon_key, tip, act, color in actions:
            btn = QPushButton()
            btn.setObjectName("ActionBtn")
            btn.setIcon(get_svg_icon(icon_key, color, 18))
            btn.setToolTip(tip)
            btn.clicked.connect(lambda chk, a=act: self.action_triggered.emit(a))
            lay.addWidget(btn)

    def _sync_color_ui(self, hx: str):
        if hx in self.preset_hexes:
            self.color_btns[hx].setChecked(True)
        else:
            self.custom_hex = hx
            _config.set("custom_color", hx)
            self.custom_btn.setStyleSheet(self._color_btn_css(hx))
            self.custom_btn.setChecked(True)

    def _on_tool_btn_clicked(self, tool_name: str):
        for t_name, btn in self.btn_group:
            if t_name != tool_name:
                btn.setChecked(False)
            elif not btn.isChecked():
                self.tool_changed.emit("none")
                return
        self.tool_changed.emit(tool_name)

    def _on_width_changed(self, width: int):
        self.current_width = width
        _config.set("pen_width", width)
        self.width_changed.emit(width)

    def _set_color(self, color: QColor):
        hx = color.name().lower()
        self._sync_color_ui(hx)
        self.current_color = color
        _config.set("default_color", hx)
        self.color_changed.emit(color)

        for t_name, btn in self.btn_group:
            if t_name == "picker" and btn.isChecked():
                btn.setChecked(False)
                self._on_tool_btn_clicked("pencil")
                break

    def _select_custom_color(self):
        c = QColorDialog.getColor(self.current_color, self, "选取自定义颜色")
        if c.isValid():
            self._set_color(c)

class SnippingOverlay(QWidget):
    STATE_IDLE = 0
    STATE_SELECTING = 1
    STATE_SELECTED = 2
    STATE_EDITING = 3
    STATE_RESIZING = 4
    STATE_MOVING = 5

    def __init__(self, controller: QSnapController):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.controller = controller
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.state = self.STATE_IDLE
        self.active_tool = "none"
        self.current_color = QColor(_config.get("default_color", "#ea4335"))
        self.current_width = _config.get("pen_width", 3)
        self.step_counter = 1
        self.aspect_ratio_locked = False
        self.locked_ratio = 0.0

        self.start_pos = QPoint()
        self.current_mouse_pos = QPoint()
        self.selected_rect = QRect()
        self.active_handle = -1
        self.move_offset = QPoint()

        self.draw_items: list[DrawItem] = []
        self.current_drawing_item: DrawItem | None = None
        self.highlighted_window = QRect()

        self.toolbar = FloatingToolBar(self)
        self.toolbar.hide()
        self.toolbar.tool_changed.connect(self._set_active_tool)
        self.toolbar.color_changed.connect(lambda c: setattr(self, "current_color", c))
        self.toolbar.width_changed.connect(lambda w: setattr(self, "current_width", w))
        self.toolbar.action_triggered.connect(self._handle_action)

        self.help_dialog: ShortcutHelpDialog | None = None
        
        self.max_dpr = 1.0
        self._capture_full_desktop()

    def _capture_full_desktop(self):
        """完全按照屏幕最大 DPR 分配高分屏显存，避免逻辑压缩导致的锯齿和发糊！"""
        screens = QGuiApplication.screens()
        self.virtual_rect = QRect()
        self.max_dpr = 1.0
        for s in screens:
            self.virtual_rect = self.virtual_rect.united(s.geometry())
            self.max_dpr = max(self.max_dpr, s.devicePixelRatio())

        self.setGeometry(self.virtual_rect)
        self.window_rects = get_window_rects(self.virtual_rect.topLeft(), self.max_dpr)

        phys_w = int(self.virtual_rect.width() * self.max_dpr)
        phys_h = int(self.virtual_rect.height() * self.max_dpr)
        self.full_pixmap = QPixmap(phys_w, phys_h)
        self.full_pixmap.setDevicePixelRatio(self.max_dpr)
        self.full_pixmap.fill(Qt.GlobalColor.black)

        painter = QPainter(self.full_pixmap)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        for s in screens:
            grab = s.grabWindow(0)
            local_tl = s.geometry().topLeft() - self.virtual_rect.topLeft()
            painter.drawPixmap(local_tl, grab)
        painter.end()

        self.base_image = self.full_pixmap.toImage()

    def _detect_window(self, pos: QPoint):
        if not _config.get("auto_detect_window", True):
            return
        for rect in self.window_rects:
            if rect.contains(pos):
                if rect != self.highlighted_window:
                    self.highlighted_window = rect
                return
        self.highlighted_window = QRect()

    def _set_active_tool(self, tool: str):
        self.active_tool = tool
        self._update_cursor(self.current_mouse_pos)
        for t_name, btn in self.toolbar.btn_group:
            if t_name == tool:
                btn.setChecked(True)
            elif btn.isChecked():
                btn.setChecked(False)

    def _handle_action(self, action: str):
        if action == "close":
            self.close()
        elif action == "undo" and self.draw_items:
            self.draw_items.pop()
            self.update()
        elif action == "finish":
            self._copy_and_exit()
        elif action == "save":
            self._save_file_dialog()
        elif action == "pin":
            self._pin_to_screen()
        elif action == "aspect":
            self._toggle_aspect_ratio()
        elif action == "ocr":
            self._run_ocr()

    def _run_ocr(self):
        if self.selected_rect.isEmpty():
            return
        pixmap = self._render_final_snipped_pixmap()
        dialog = OCRDialog(pixmap, self)
        dialog.exec()

    def _toggle_aspect_ratio(self):
        if not self.selected_rect.isEmpty():
            if not self.aspect_ratio_locked:
                r = self.selected_rect.normalized()
                self.locked_ratio = r.width() / max(1, r.height())
                self.aspect_ratio_locked = True
                self.update()
            else:
                menu = QMenu(self)
                menu.addAction("自由比例").triggered.connect(lambda: self._set_ratio(0))
                menu.addAction("16 : 9").triggered.connect(lambda: self._set_ratio(16 / 9))
                menu.addAction("4 : 3").triggered.connect(lambda: self._set_ratio(4 / 3))
                menu.addAction("1 : 1").triggered.connect(lambda: self._set_ratio(1.0))
                menu.exec(QCursor.pos())

    def _set_ratio(self, ratio: float):
        if ratio == 0:
            self.aspect_ratio_locked = False
        else:
            self.aspect_ratio_locked = True
            self.locked_ratio = ratio
            if not self.selected_rect.isEmpty():
                r = self.selected_rect.normalized()
                r.setWidth(int(r.height() * ratio))
                self.selected_rect = r
        self.update()

    def _render_final_snipped_pixmap(self) -> QPixmap:
        r = self.selected_rect.normalized()
        
        phys_rect = QRect(
            int(r.x() * self.max_dpr),
            int(r.y() * self.max_dpr),
            int(r.width() * self.max_dpr),
            int(r.height() * self.max_dpr)
        )
        cropped = self.full_pixmap.copy(phys_rect)
        cropped.setDevicePixelRatio(self.max_dpr)
        
        painter = QPainter(cropped)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(-r.topLeft())
        for item in self.draw_items:
            item.paint(painter, self.full_pixmap)
        painter.end()
        return cropped

    def _copy_and_exit(self):
        pixmap = self._render_final_snipped_pixmap()
        if _config.get("auto_copy", True):
            QApplication.clipboard().setPixmap(pixmap)
        play_shutter_sound()
        self.close()

    def _pin_to_screen(self):
        pinned = PinnedImageWidget(self._render_final_snipped_pixmap())
        pinned.move(self.mapToGlobal(self.selected_rect.topLeft()))
        pinned.show()
        self.controller.register_pinned(pinned)
        self.close()

    def _save_file_dialog(self):
        last_dir = _config.get("last_save_dir", str(Path.home() / "Pictures"))
        ts = time.strftime("%Y%m%d_%H%M%S")
        fp, _ = QFileDialog.getSaveFileName(self, "保存截图", str(Path(last_dir) / f"{__app_name__}_{ts}.png"), "PNG (*.png);;JPEG (*.jpg)")
        if fp:
            self._render_final_snipped_pixmap().save(fp)
            _config.set("last_save_dir", str(Path(fp).parent))
            self.close()

    def _get_handle_rects(self, r: QRect) -> list[tuple[int, QRect]]:
        if r.isEmpty():
            return []
        nr = r.normalized()
        sz, half = 8, 4
        pts = [
            (0, nr.left(), nr.top()),
            (1, nr.center().x(), nr.top()),
            (2, nr.right(), nr.top()),
            (3, nr.right(), nr.center().y()),
            (4, nr.right(), nr.bottom()),
            (5, nr.center().x(), nr.bottom()),
            (6, nr.left(), nr.bottom()),
            (7, nr.left(), nr.center().y()),
        ]
        return [(idx, QRect(x - half, y - half, sz, sz)) for idx, x, y in pts]

    def _hit_test(self, pos: QPoint) -> int:
        if self.selected_rect.isEmpty():
            return -1
        for idx, rect in self._get_handle_rects(self.selected_rect):
            if rect.contains(pos):
                return idx
        if self.selected_rect.normalized().contains(pos):
            return 8
        return -1

    def _update_cursor(self, pos: QPoint):
        if self.state in (self.STATE_IDLE, self.STATE_SELECTING):
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif self.state == self.STATE_SELECTED:
            if self.active_tool == "picker":
                self.setCursor(Qt.CursorShape.CrossCursor)
                return
            if self.active_tool != "none":
                self.setCursor(Qt.CursorShape.IBeamCursor if self.active_tool == "text" else Qt.CursorShape.CrossCursor)
                return
            hit = self._hit_test(pos)
            if hit in (0, 4):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif hit in (2, 6):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif hit in (1, 5):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif hit in (3, 7):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif hit == 8:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)

    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        if event.button() == Qt.MouseButton.LeftButton:
            if self.state == self.STATE_SELECTED and self.active_tool == "picker":
                rx, ry = int(pos.x() * self.max_dpr), int(pos.y() * self.max_dpr)
                c = self.base_image.pixelColor(
                    min(max(0, rx), self.base_image.width() - 1),
                    min(max(0, ry), self.base_image.height() - 1),
                )
                self.toolbar._set_color(c)
                QApplication.clipboard().setText(c.name().upper())
                return

            if self.state == self.STATE_IDLE:
                self.start_pos = pos
                self.selected_rect = QRect(pos, pos)
                self.state = self.STATE_SELECTING
                self.update()
            elif self.state == self.STATE_SELECTED:
                if self.active_tool != "none" and self.selected_rect.normalized().contains(pos):
                    self.start_pos = pos
                    self.state = self.STATE_EDITING
                    self._handle_drawing_press(pos)
                else:
                    hit = self._hit_test(pos)
                    if 0 <= hit < 8:
                        self.active_handle = hit
                        self.start_pos = pos
                        self.state = self.STATE_RESIZING
                        self.toolbar.hide()
                    elif hit == 8:
                        self.move_offset = pos - self.selected_rect.topLeft()
                        self.state = self.STATE_MOVING
                        self.toolbar.hide()
                    else:
                        self.start_pos = pos
                        self.selected_rect = QRect(pos, pos)
                        self.state = self.STATE_SELECTING
                        self.toolbar.hide()
                        self.draw_items.clear()
                        self.update()
            elif self.state == self.STATE_EDITING:
                self.start_pos = pos
                self._handle_drawing_press(pos)
        elif event.button() == Qt.MouseButton.RightButton:
            if self.draw_items:
                self.draw_items.pop()
                self.update()
            elif self.state == self.STATE_SELECTED:
                self.selected_rect = QRect()
                self.toolbar.hide()
                self.state = self.STATE_IDLE
                self.update()
            else:
                self.close()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        self.current_mouse_pos = pos

        if self.state == self.STATE_IDLE:
            self._detect_window(pos)
            self.update()

        elif self.state == self.STATE_SELECTING:
            if (pos - self.start_pos).manhattanLength() > 5:
                self.highlighted_window = QRect()
            new_rect = QRect(self.start_pos, pos).normalized()
            if self.aspect_ratio_locked and self.locked_ratio > 0:
                h = int(new_rect.width() / self.locked_ratio)
                if pos.y() < self.start_pos.y():
                    new_rect.setTop(self.start_pos.y() - h)
                else:
                    new_rect.setHeight(h)
            self.selected_rect = new_rect
            self.update()

        elif self.state == self.STATE_RESIZING:
            r = self.selected_rect.normalized()
            if self.active_handle == 0:
                r.setTopLeft(pos)
            elif self.active_handle == 1:
                r.setTop(pos.y())
            elif self.active_handle == 2:
                r.setTopRight(pos)
            elif self.active_handle == 3:
                r.setRight(pos.x())
            elif self.active_handle == 4:
                r.setBottomRight(pos)
            elif self.active_handle == 5:
                r.setBottom(pos.y())
            elif self.active_handle == 6:
                r.setBottomLeft(pos)
            elif self.active_handle == 7:
                r.setLeft(pos.x())

            if self.aspect_ratio_locked and self.locked_ratio > 0 and self.active_handle in (0, 2, 4, 6):
                h = int(r.width() / self.locked_ratio)
                if self.active_handle in (0, 2):
                    r.setHeight(h)
                else:
                    r.setBottom(r.top() + h)
            self.selected_rect = r.normalized()
            self.update()

        elif self.state == self.STATE_MOVING:
            self.selected_rect.moveTopLeft(pos - self.move_offset)
            self.update()

        elif self.state == self.STATE_EDITING:
            self._handle_drawing_move(pos)
            self.update()

        else:
            self._update_cursor(pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.state == self.STATE_SELECTING:
                if self.selected_rect.width() > 8 and self.selected_rect.height() > 8:
                    self.state = self.STATE_SELECTED
                    self._position_toolbar()
                else:
                    if not self.highlighted_window.isEmpty() and self.highlighted_window.contains(event.position().toPoint()):
                        self.selected_rect = self.highlighted_window
                        self.state = self.STATE_SELECTED
                        self.highlighted_window = QRect()
                        self._position_toolbar()
                    else:
                        self.selected_rect = QRect()
                        self.state = self.STATE_IDLE
                self.update()
            elif self.state in (self.STATE_RESIZING, self.STATE_MOVING):
                self.state = self.STATE_SELECTED
                self._position_toolbar()
                self.update()
            elif self.state == self.STATE_EDITING:
                if self.current_drawing_item:
                    self.draw_items.append(self.current_drawing_item)
                    if isinstance(self.current_drawing_item, StepBadgeItem):
                        self.step_counter += 1
                    self.current_drawing_item = None
                self.update()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.state == self.STATE_SELECTED and self.selected_rect.contains(event.position().toPoint()):
                self._copy_and_exit()

    def _handle_drawing_press(self, pos: QPoint):
        w = self.current_width
        if self.active_tool == "rect":
            self.current_drawing_item = RectItem(QRectF(pos, pos), self.current_color, w)
        elif self.active_tool == "circle":
            self.current_drawing_item = CircleItem(QRectF(pos, pos), self.current_color, w)
        elif self.active_tool == "line":
            self.current_drawing_item = LineItem(QPointF(pos), QPointF(pos), self.current_color, w)
        elif self.active_tool == "arrow":
            self.current_drawing_item = ArrowItem(QPointF(pos), QPointF(pos), self.current_color, w)
        elif self.active_tool == "pencil":
            self.current_drawing_item = PencilItem([QPointF(pos)], self.current_color, w, False)
        elif self.active_tool == "marker":
            self.current_drawing_item = PencilItem([QPointF(pos)], self.current_color, w, True)
        elif self.active_tool == "badge":
            self.current_drawing_item = StepBadgeItem(QPointF(pos), self.step_counter, self.current_color)
        elif self.active_tool == "mosaic":
            self.current_drawing_item = MosaicItem(QRectF(pos, pos))
        elif self.active_tool == "text":
            text, ok = QInputDialog.getMultiLineText(self, "添加文字标注", "请输入标注文本:")
            if ok and text.strip():
                self.draw_items.append(TextItem(QPointF(pos), text, self.current_color))
                self.update()

    def _handle_drawing_move(self, pos: QPoint):
        if not self.current_drawing_item:
            return
        if isinstance(self.current_drawing_item, (RectItem, CircleItem, MosaicItem)):
            self.current_drawing_item.rect = QRectF(self.start_pos, pos).normalized()
        elif isinstance(self.current_drawing_item, (ArrowItem, LineItem)):
            self.current_drawing_item.end = QPointF(pos)
        elif isinstance(self.current_drawing_item, PencilItem):
            self.current_drawing_item.points.append(QPointF(pos))

    def _position_toolbar(self):
        if self.selected_rect.isEmpty():
            self.toolbar.hide()
            return
        r = self.selected_rect.normalized()
        tb_w, tb_h = self.toolbar.sizeHint().width(), self.toolbar.sizeHint().height()
        tb_x = r.right() - tb_w + 12
        tb_y = r.bottom() + 6
        if tb_y + tb_h > self.height():
            tb_y = r.top() - tb_h - 6
        if tb_y < 6:
            tb_y = r.bottom() - tb_h - 6
        tb_x = max(6, min(tb_x, self.width() - tb_w - 6))
        self.toolbar.setGeometry(int(tb_x), int(tb_y), int(tb_w), int(tb_h))
        self.toolbar.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        painter.drawPixmap(0, 0, self.full_pixmap)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.state == self.STATE_IDLE and not self.highlighted_window.isEmpty():
            painter.setPen(QPen(QColor("#1a73e8"), 2.5, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(26, 115, 232, 28)))
            painter.drawRect(self.highlighted_window)

        path = QPainterPath()
        path.setFillRule(Qt.FillRule.OddEvenFill)
        path.addRect(QRectF(self.rect()))
        target_rect = self.selected_rect.normalized()
        if not target_rect.isEmpty():
            path.addRect(QRectF(target_rect))

        painter.fillPath(path, QColor(0, 0, 0, 115))

        if not target_rect.isEmpty():
            painter.setPen(QPen(QColor("#1a73e8"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(target_rect)
            if self.state in (self.STATE_SELECTED, self.STATE_EDITING):
                painter.setBrush(QBrush(Qt.GlobalColor.white))
                painter.setPen(QPen(QColor("#1a73e8"), 1.5))
                for _, h_rect in self._get_handle_rects(target_rect):
                    painter.drawRect(h_rect)

            dim_str = f" {target_rect.width()} × {target_rect.height()} "
            if self.aspect_ratio_locked:
                dim_str += f" ({self.locked_ratio:.2f}:1) 🔒"
            painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            fm = painter.fontMetrics()
            tw, th = fm.horizontalAdvance(dim_str) + 12, fm.height() + 6
            bx, by = target_rect.left(), target_rect.top() - th - 6
            if by < 5:
                by = target_rect.top() + 6
            badge_rect = QRectF(bx, by, tw, th)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#202124")))
            painter.drawRoundedRect(badge_rect, 4, 4)
            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, dim_str)

        painter.save()
        if not target_rect.isEmpty():
            painter.setClipRect(target_rect)
        for item in self.draw_items:
            item.paint(painter, self.full_pixmap)
        if self.current_drawing_item:
            self.current_drawing_item.paint(painter, self.full_pixmap)
        painter.restore()

        if _config.get("show_magnifier", True) and (self.state in (self.STATE_IDLE, self.STATE_SELECTING) or self.active_tool == "picker"):
            self._paint_magnifier(painter, self.current_mouse_pos)

    def _paint_magnifier(self, painter: QPainter, pos: QPoint):
        x, y = pos.x(), pos.y()
        rx, ry = int(x * self.max_dpr), int(y * self.max_dpr)
        img_w, img_h = self.base_image.width(), self.base_image.height()
        rgb = self.base_image.pixelColor(min(max(0, rx), img_w - 1), min(max(0, ry), img_h - 1))

        hud_w, hud_h = 136, 154
        hud_x = x + 20 if x + hud_w + 30 < self.width() else x - hud_w - 20
        hud_y = y + 20 if y + hud_h + 30 < self.height() else y - hud_h - 20

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(QPen(QColor("#1a73e8"), 2))
        painter.setBrush(QBrush(QColor("#1e293b")))
        painter.drawRoundedRect(QRect(hud_x - 1, hud_y - 1, 114, 134), 6, 6)

        half = 5
        for gx in range(11):
            for gy in range(11):
                px = min(max(0, rx - half + gx), img_w - 1)
                py = min(max(0, ry - half + gy), img_h - 1)
                painter.fillRect(hud_x + gx * 10, hud_y + gy * 7, 10, 7, QBrush(self.base_image.pixelColor(px, py)))

        painter.setPen(QPen(QColor("#1a73e8"), 2))
        painter.drawRect(hud_x + half * 10, hud_y + half * 7, 10, 7)
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        painter.drawText(hud_x + 6, hud_y + 92, f"#{rgb.red():02X}{rgb.green():02X}{rgb.blue():02X}")
        painter.drawText(hud_x + 6, hud_y + 107, f"RGB:({rgb.red()},{rgb.green()},{rgb.blue()})")
        painter.drawText(hud_x + 6, hud_y + 122, f"POS: {x}, {y}")
        painter.restore()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not self.selected_rect.isEmpty():
                self._copy_and_exit()
        elif key == Qt.Key.Key_F1:
            if not self.help_dialog:
                self.help_dialog = ShortcutHelpDialog(self)
            self.help_dialog.move(self.rect().center() - self.help_dialog.rect().center())
            self.help_dialog.show()
        elif key == Qt.Key.Key_C:
            if event.modifiers() == Qt.KeyboardModifier.NoModifier:
                self._set_active_tool("picker")
        elif key == Qt.Key.Key_F3:
            if not self.selected_rect.isEmpty():
                self._pin_to_screen()
        elif event.matches(QKeySequence.StandardKey.Undo):
            self._handle_action("undo")
        elif key == Qt.Key.Key_R:
            self._set_active_tool("rect")
        elif key == Qt.Key.Key_O:
            self._set_active_tool("circle")
        elif key == Qt.Key.Key_L:
            self._set_active_tool("line")
        elif key == Qt.Key.Key_A:
            self._set_active_tool("arrow")
        elif key == Qt.Key.Key_P:
            self._set_active_tool("pencil")
        elif key == Qt.Key.Key_H:
            self._set_active_tool("marker")
        elif key == Qt.Key.Key_T:
            self._set_active_tool("text")
        elif key == Qt.Key.Key_B:
            self._set_active_tool("badge")
        elif key == Qt.Key.Key_M:
            self._set_active_tool("mosaic")
        elif key == Qt.Key.Key_1:
            self.toolbar._on_width_changed(2)
        elif key == Qt.Key.Key_2:
            self.toolbar._on_width_changed(3)
        elif key == Qt.Key.Key_3:
            self.toolbar._on_width_changed(5)

    def closeEvent(self, event):
        if self.help_dialog:
            self.help_dialog.close()
        self.full_pixmap = None
        self.base_image = None
        super().closeEvent(event)

class GlobalHotkeyThread(QThread):
    hotkey_triggered = Signal()

    def __init__(self, hotkey_str="Ctrl+Alt+A", key_id=101):
        super().__init__()
        self.hotkey_str = hotkey_str
        self.key_id = key_id
        self._running = True

    def run(self):
        if os.name != "nt":
            return
        user32 = ctypes.windll.user32
        modifiers, vk = _parse_hotkey(self.hotkey_str)
        if not user32.RegisterHotKey(None, self.key_id, modifiers | 0x4000, vk):
            logger.warning(f"Global Hotkey {self.hotkey_str} failed to register (may already be occupied).")
            
        msg = wintypes.MSG()
        while self._running:
            if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                if msg.message == 0x0312 and msg.wParam == self.key_id:
                    self.hotkey_triggered.emit()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.05)
        user32.UnregisterHotKey(None, self.key_id)

    def stop(self):
        self._running = False


class SettingsDialog(QDialog):
    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle(f"{__app_name__} 设置")
        self.setMinimumSize(540, 580)
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QLabel { color: #1e293b; font-size: 13px; }
            QLabel#SectionTitle { font-size: 14px; font-weight: bold; color: #1a73e8; margin-bottom: 2px; }
            QFrame#Card { background: #ffffff; border: 1px solid #e8eaed; border-radius: 8px; padding: 14px; margin-bottom: 6px; }
            QPushButton { background: #1a73e8; color: #ffffff; border-radius: 6px; padding: 8px 18px; font-weight: bold; border: none; }
            QPushButton:hover { background: #1557b0; }
            QPushButton#OutlineBtn { background: transparent; color: #1e293b; border: 1px solid #dadce0; }
            QPushButton#OutlineBtn:hover { background: #f1f3f4; }
            QCheckBox { font-size: 13px; color: #3c4043; padding: 2px 0px; }
            QKeySequenceEdit { border: 1px solid #dadce0; border-radius: 6px; padding: 6px; background: #f1f3f4; font-weight: bold;}
            QKeySequenceEdit:focus { border: 1px solid #1a73e8; background: #ffffff; }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 8px; background: transparent; }
            QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; }
        """)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(content_widget)
        lay.setSpacing(10)
        lay.setContentsMargins(20, 20, 20, 10)

        card1 = QFrame(objectName="Card")
        c1_lay = QVBoxLayout(card1)
        c1_lay.addWidget(QLabel("💻 基础行为", objectName="SectionTitle"))
        
        self.chk_autostart = QCheckBox("随系统开机自动启动")
        if os.name != "nt": self.chk_autostart.setEnabled(False)
        else: self.chk_autostart.setChecked(check_autostart_win())
        c1_lay.addWidget(self.chk_autostart)

        self.chk_window = QCheckBox("开启智能窗口吸附检测 (红蓝闪烁框)", checked=_config.get("auto_detect_window", True))
        c1_lay.addWidget(self.chk_window)

        self.chk_mag = QCheckBox("显示鼠标放大镜吸管辅助", checked=_config.get("show_magnifier", True))
        c1_lay.addWidget(self.chk_mag)
        lay.addWidget(card1)

        card2 = QFrame(objectName="Card")
        c2_lay = QVBoxLayout(card2)
        c2_lay.addWidget(QLabel("💾 输出与反馈", objectName="SectionTitle"))
        
        self.chk_sound = QCheckBox("启用照相机快门音效", checked=_config.get("enable_sound", True))
        c2_lay.addWidget(self.chk_sound)
        
        self.chk_copy = QCheckBox("截图完成后自动复制到系统剪贴板", checked=_config.get("auto_copy", True))
        c2_lay.addWidget(self.chk_copy)

        path_lay = QHBoxLayout()
        path_lay.addWidget(QLabel("默认保存路径:"))
        self.lbl_path = QLabel(_config.get("last_save_dir", str(Path.home() / "Pictures")))
        self.lbl_path.setStyleSheet("color: #5f6368;")
        path_lay.addWidget(self.lbl_path, 1)
        btn_browse = QPushButton("更改", objectName="OutlineBtn")
        btn_browse.clicked.connect(self._browse_dir)
        path_lay.addWidget(btn_browse)
        c2_lay.addLayout(path_lay)
        lay.addWidget(card2)

        card3 = QFrame(objectName="Card")
        c3_lay = QVBoxLayout(card3)
        c3_lay.addWidget(QLabel("⌨ 快捷键", objectName="SectionTitle"))
        hk_lay = QHBoxLayout()
        hk_lay.addWidget(QLabel("全局截图热键:"))
        self.hk_edit = QKeySequenceEdit()
        self.hk_edit.setKeySequence(QKeySequence(_config.get("hotkey", "Ctrl+Alt+A")))
        hk_lay.addWidget(self.hk_edit)
        hk_lay.addStretch()
        c3_lay.addLayout(hk_lay)
        c3_lay.addWidget(QLabel("提示：在截图界面按 F1 可随时查看全键盘操作指引。", styleSheet="color: #9aa0a6; margin-top: 4px;"))
        lay.addWidget(card3)

        lay.addStretch()
        scroll.setWidget(content_widget)
        main_lay.addWidget(scroll)

        btn_lay = QHBoxLayout()
        btn_lay.setContentsMargins(20, 0, 20, 16)
        btn_lay.addWidget(QLabel(f"v{__version__} by {__author__}", styleSheet="color: #9aa0a6; font-size: 12px; font-weight: bold;"))
        btn_lay.addStretch()
        btn_cancel = QPushButton("取消", objectName="OutlineBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_lay.addWidget(btn_cancel)
        btn_ok = QPushButton("保存设置")
        btn_ok.clicked.connect(self.accept)
        btn_lay.addWidget(btn_ok)
        main_lay.addLayout(btn_lay)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择默认保存目录", self.lbl_path.text())
        if d: self.lbl_path.setText(d)

    def accept(self):
        new_hk = self.hk_edit.keySequence().toString(QKeySequence.SequenceFormat.PortableText)
        if not new_hk:
            QMessageBox.warning(self, "提示", "截图热键不能为空！")
            return
            
        old_hk = _config.get("hotkey", "Ctrl+Alt+A")
        if new_hk != old_hk:
            if os.name == "nt":
                ok, msg = check_hotkey_conflict_win(new_hk)
                if not ok:
                    QMessageBox.warning(self, "快捷键冲突", msg)
                    self.hk_edit.setKeySequence(QKeySequence(old_hk))
                    return
            _config.set("hotkey", new_hk)
            if self.controller:
                self.controller.update_hotkey(new_hk)

        _config.set("auto_detect_window", self.chk_window.isChecked())
        _config.set("show_magnifier", self.chk_mag.isChecked())
        _config.set("enable_sound", self.chk_sound.isChecked())
        _config.set("auto_copy", self.chk_copy.isChecked())
        _config.set("last_save_dir", self.lbl_path.text())
        
        if os.name == "nt":
            set_autostart_win(self.chk_autostart.isChecked())
            
        super().accept()


class QSnapController(QObject):
    def __init__(self):
        super().__init__()
        self.current_overlay: SnippingOverlay | None = None
        self._pinned_windows: list[PinnedImageWidget] = []
        self._init_tray()
        self._init_hotkey()

    def _init_tray(self):
        self.tray = QSystemTrayIcon(get_logo_icon(24))
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background: #ffffff; border: 1px solid #e8eaed; border-radius: 8px; padding: 6px; }
            QMenu::item { padding: 8px 24px; font-weight: 500; border-radius: 4px; color: #3c4043; }
            QMenu::item:selected { background: #e8f0fe; color: #1a73e8; }
        """)
        self.snip_action = menu.addAction(get_svg_icon("aspect_ratio", "#1a73e8", 16), "开始截图")
        self.snip_action.triggered.connect(self.trigger_snip)
        self._update_tray_ui_texts()
        
        menu.addAction(get_svg_icon("settings", "#5f6368", 16), "设置").triggered.connect(lambda: SettingsDialog(self).exec())
        menu.addSeparator()
        menu.addAction(get_svg_icon("close", "#ea4335", 16), f"退出 {__app_name__}").triggered.connect(QApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda r: self.trigger_snip() if r == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()

    def _update_tray_ui_texts(self):
        hk = _config.get("hotkey", "Ctrl+Alt+A")
        self.tray.setToolTip(f"{__app_name__} - 智能截图与文字识别 ({hk})")
        self.snip_action.setText(f"开始截图 ({hk})")

    def _init_hotkey(self):
        hk = _config.get("hotkey", "Ctrl+Alt+A")
        self.hotkey_thread = GlobalHotkeyThread(hk)
        self.hotkey_thread.hotkey_triggered.connect(self.trigger_snip)
        self.hotkey_thread.start()

    def update_hotkey(self, new_hk: str):
        if hasattr(self, "hotkey_thread") and self.hotkey_thread.isRunning():
            self.hotkey_thread.stop()
            self.hotkey_thread.quit()
            self.hotkey_thread.wait(1000)
            
        self.hotkey_thread = GlobalHotkeyThread(new_hk)
        self.hotkey_thread.hotkey_triggered.connect(self.trigger_snip)
        self.hotkey_thread.start()
        self._update_tray_ui_texts()

    def trigger_snip(self):
        try:
            if self.current_overlay and self.current_overlay.isVisible():
                return
        except RuntimeError:
            self.current_overlay = None

        self.current_overlay = SnippingOverlay(self)
        self.current_overlay.show()

    def register_pinned(self, widget: PinnedImageWidget):
        self._pinned_windows = [w for w in self._pinned_windows if not w.isHidden()]
        self._pinned_windows.append(widget)

    def shutdown(self):
        if hasattr(self, "hotkey_thread") and self.hotkey_thread.isRunning():
            self.hotkey_thread.stop()
            self.hotkey_thread.quit()
            self.hotkey_thread.wait(1000)


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 9))
    
    app.setWindowIcon(get_logo_icon(64))
    
    controller = QSnapController()
    app.aboutToQuit.connect(controller.shutdown)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
