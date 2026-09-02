<div align="center">

# 📸 QSnap

**Modern, Pixel-Perfect, and Offline-First Screenshot Suite for Power Users.**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Qt Framework](https://img.shields.io/badge/Qt-PySide6-41CD52.svg)](https://pypi.org/project/PySide6/)
[![OCR Engine](https://img.shields.io/badge/OCR-RapidOCR%20(Local)-orange.svg)](https://github.com/RapidAI/RapidOCR)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

*A clean, native, and lightning-fast screenshot application built with modern Google Material Design, featuring multi-monitor DPI stitching, offline OCR text extraction, on-screen pinning, and precision color sampling.*

[English](#features) | [简体中文](#功能特性)

---

</div>

## ✨ Features / 功能特性

- 🎯 **Smart Window Snapping & High-DPI Support**: Automatically detects window boundaries across multiple monitors with arbitrary DPI scalings and handles cloaked Windows 10/11 windows gracefully.
- ⚡ **100% Local Async OCR**: High-speed, offline text extraction powered by `RapidOCR` ONNX runtime. No data leaves your machine.
- 📌 **Pin-to-Screen (F3)**: Pin captures as floating widgets. Freely scale (`Scroll Wheel`), adjust opacity (`Ctrl + Scroll`), or inspect visual assets.
- 🔬 **Sub-pixel Magnifier & Color Picker**: Real-time pixel grid magnifier displaying HEX, RGB, and absolute desktop coordinates.
- 🎨 **Rich Annotations**: Includes smooth anti-aliased freehand pen, highlighter, step badges (`① ② ③`), rectangle/ellipse shapes, arrows, and privacy mosaics.
- 🔒 **Aspect Ratio Lock**: Snips in precise 16:9, 4:3, 1:1, or customized aspect ratios.
- ⌨ **Full Keyboard Navigation**: Every action is reachable via ergonomic hotkeys.

---

## ⌨️ Shortcuts Reference / 快捷键列表

| Shortcut / 快捷键 | Action / 操作说明 |
| :--- | :--- |
| `Ctrl + Alt + A` | **Global Hotkey** / 全局唤醒截图 |
| `Enter` / `Double Click` | Finish capture & Copy to clipboard / 完成并复制 |
| `Esc` / `Right Click` | Cancel current snip / 取消当前操作或退出 |
| `F3` | **Pin to Screen** / 贴图在屏幕上 |
| `C` | **Color Picker** / 启动吸管取色并复制 HEX |
| `Ctrl + S` | Save image to local disk / 保存截图为文件 |
| `Ctrl + Z` | Undo last annotation / 撤销上一条标注 |
| `R` / `O` / `L` / `A` | Rect / Ellipse / Line / Arrow (矩形/椭圆/直线/箭头) |
| `P` / `H` / `T` | Pen / Highlighter / Text Annotation (画笔/荧光笔/文本) |
| `B` / `M` | Step Badge / Mosaic (步骤序号/马赛克) |
| `1` / `2` / `3` | Toggle Brush Stroke Width (切换粗细: 细/中/粗) |
| `F1` | Open Interactive Cheatsheet / 打开快捷键指引 |

---

## 🚀 Quick Start / 快速开始

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/qwejay/qsnap.git
cd qsnap

# Optional: Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Run Application

```bash
python main.py
```

---

## 📦 Build Standalone Executable / 单文件打包

You can package QSnap into a single `.exe` (Windows) using `PyInstaller`:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=icon.ico --name="QSnap" main.py
```

---

## 🛡️ Privacy & Security

- **Zero Telemetry**: QSnap does not communicate with external servers.
- **Local OCR**: OCR inference is computed entirely on-device via ONNX Runtime without cloud dependencies.

---

## 📄 License

This project is licensed under the [GPL-3.0 license](LICENSE).
