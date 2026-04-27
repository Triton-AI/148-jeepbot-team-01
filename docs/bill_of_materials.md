## 1. Overview

This section lists the main hardware components used in the robot system.

The list includes core components required for:

- Power  
- Control  
- Sensing  
- Communication  

Additional mechanical components (mounts, screws, brackets) are documented in the Mechanical section.

---

## 2. Core Components

**Component — Quantity — Purpose**

- 24V lead-acid battery (7Ah) — 1 — Main power source  
- Antispark switch — 1 — Protects system during power connection (currently not functional)  
- Power Distribution Board (PDB) — 1 — Distributes power to all components  
- VESC motor controllers — 5 — Control drive motors and steering  
- Raspberry Pi 5 — 1 — Main computer and controller  
- CAN interface (CAN HAT) — 1 — Enables CAN communication with VESCs  
- DC-DC converters (24V → 12V, 5V) — 2+ — Regulate voltage  
- Powered USB hub — 1 — Connects and powers USB devices  

---

## 3. Sensors

**Component — Quantity — Purpose**

- OAK-D cameras — 2 — Depth perception and vision  
- LiDAR sensor — 1 — Environment mapping (currently not powered)  
- GPS module — 1 — Location tracking (not yet installed)  
- AS5600 magnetic encoder — 1 — Steering angle measurement  
- Motor encoders (hall-effect) — 4+ — Motor position feedback  

---

## 4. Wiring and Connectors

**Component — Quantity — Purpose**

- Silicone wire (10 AWG) — As needed — High-current battery wiring  
- Silicone wire (12 AWG) — As needed — Motor wiring  
- Silicone wire (14–16 AWG) — As needed — Low-voltage electronics  
- CAN bus wiring (24 AWG) — As needed — Communication between VESCs  
- XT90 connectors — As needed — Battery connections  
- XT60 connectors — As needed — Power distribution and DC-DC connections  

---

## 5. Notes

- Quantities are approximate and may change  
- Some components are not fully integrated or operational  
- Mechanical hardware is documented in the Mechanical section  
- Specific models and links can be added later  
