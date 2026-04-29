# 3D Printing – LED Mount System

This directory contains the printable components used to construct a **modular LED mounting system** for aligning an LED strip with piano keys.

The system allows individual LEDs to be positioned more precisely than their fixed spacing on the strip, while maintaining a clean and stable physical structure.

---

## Components

The system is composed of four parts:

* **Base Rail**
  The primary structural piece. Contains a track for mounting LED holders.

* **Bridge Rail**
  Connects adjacent base rails using a staggered (brick-like) pattern for improved rigidity.

* **LED Holder**
  Slides into the base rail and positions a single LED.

* **LED Retainer**
  A small press-fit piece used to secure the LED strip within the holder.

---

## Assembly Overview

The following steps demonstrate how the system is assembled. These examples are shown independently of a full keyboard setup, but reflect the intended workflow.

---

### 1. Attach Retainer to LED

Snap a **retainer** onto the front of an LED on the strip.

This piece ensures the LED will sit snugly inside the holder.

*(image here)*

---

### 2. Adjust LED Spacing

Introduce a small **kink** in the LED strip between adjacent LEDs.

This allows LEDs to be positioned closer together than their fixed spacing on the strip.

*(image here)*

---

### 3. Insert LED Holder

Slide an **LED holder** into the track on the base rail.

Position it approximately where the LED should align (e.g., corresponding to a key).

*(image here)*

---

### 4. Mount LED into Holder

Insert the LED (with retainer attached) into the holder.

The retainer should hold the LED securely in place.

*(image here)*

---

### 5. Repeat and Extend

Repeat steps 1–4 for each LED.

As you fill a base rail:

* Add additional base rails as needed
* Connect them using **bridge rails**

⚠️ Note:

* Avoid adding bridge rails too early, as they can obstruct access while placing LEDs
* Attach bridges only after the section is mostly complete

---

## Rail Layout

Rails are designed to be assembled in a staggered pattern:

```text
----|----|----|   (Bridge Rail)
--|----|----|--   (Base Rail)
```

This improves structural stability while allowing flexible length construction.

---

## Notes

* This system is intended as a **modular mounting approach**, not a fixed one-size solution
* Exact positioning may vary depending on keyboard geometry and LED strip type
* Demonstration images show isolated assembly steps rather than a full installation

---

## Files

```text
stl/
  base_rail.stl
  bridge_rail.stl
  led_holder.stl
  led_retainer.stl
```

---

## Summary

This mounting system provides:

* Adjustable LED positioning
* Modular, extendable structure
* Secure retention of LED strip segments

It is designed to work alongside the MIDI-driven LED visualizer system in this repository.
