# MIDI LED Visualizer

A MIDI-driven LED strip visualizer for piano input, using Python and Arduino to map real-time note events to configurable color patterns.

---

## Parts List

* WS2812 (NeoPixel) LED strip
* Arduino (tested with Arduino Uno; similar models should also work)
* MIDI keyboard / digital piano
* Desktop machine running Python
* Power supply capable of driving the LED strip

### Power Requirements

For a full 88-key setup:

* WS2812 LEDs can draw up to **~60mA per LED at full brightness (white)**
* For 88 LEDs, plan for **~5A at 5V** as a safe upper bound

In practice, typical usage (colored output, not full white) will draw significantly less, but your power supply should be sized conservatively.

---

## Overview

This project listens to MIDI input and maps active notes to LED colors in real time.

* Notes played on the keyboard light up corresponding LEDs
* Color mappings are configurable
* The **sostenuto pedal** can be used to cycle between different color modes

The system is designed to be simple, responsive, and easy to extend.

---

## Demo (Click to Play)

[![MIDI LED Visualizer Demo](screenshots/demo_thumbnail.jpg)](https://www.youtube.com/watch?v=XFutyCQXSFY)

---

## Repository Structure

```text id="3m5u4w"
3d_printing/
  screenshots/      Example assembly steps
  stl/              Printable components

arduino/
  midi_led_receiver/
    midi_led_receiver.ino

python/
  midi_led_visualizer.py
  config.example.json
  requirements.txt
```

---

## Setup

### 1. Install Python dependencies

```bash id="0c2fye"
pip install -r python/requirements.txt
```

---

### 2. Configure the application

Copy the example config:

```bash id="k0r6wp"
cp python/config.example.json python/config.json
```

Then edit `config.json` to match your setup:

* MIDI input device name
* Serial port (e.g. `COM4`)
* Optional MIDI forwarding

---

### 3. Upload Arduino code

Open:

```text id="txr0zw"
arduino/midi_led_receiver/midi_led_receiver.ino
```

Upload it to your Arduino.

---

### 4. Run the visualizer

```bash id="3k1j4g"
python python/midi_led_visualizer.py --config python/config.json
```

---

## Wiring

### LED Strip → Arduino

* **Data line** → Arduino **Pin 6**
* **5V** → External power supply (recommended for larger strips)
* **GND** → Shared between:

  * Arduino
  * LED strip
  * power supply

⚠️ Important:

* Always ensure **common ground** between all components
* Do not power large LED strips directly from the Arduino

---

## Physical Layout

* The LED strip is oriented so that **lower LED indices correspond to keys on the left side of the keyboard**
* For this reason, it is recommended to position the **Arduino on the left side** of the keyboard

This keeps wiring simple and avoids reversing LED indexing in software.

---

## 3D Printed Mount System

The `3d_printing/` directory contains a modular system for mounting LEDs:

* **Base rails** – main structure with mounting track
* **Bridge rails** – connect segments in a staggered pattern
* **LED holders** – position individual LEDs
* **LED retainers** – secure LEDs in place

See `3d_printing/README.md` for full assembly instructions.

---

## Notes

* This project focuses on **real-time MIDI → LED mapping**, not expressive rendering or advanced visual effects
* Designed to be simple, modular, and easy to modify
* Compatible with most MIDI keyboards and WS2812-style LED strips

---

## Summary

This project demonstrates:

* Real-time MIDI processing in Python
* Serial communication with embedded hardware
* LED control using WS2812 strips
* A modular physical mounting system

---

## Closing

Have fun building!
