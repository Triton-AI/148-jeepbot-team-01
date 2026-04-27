# 🚗 JeepBot | ECE/MAE 148 — Team 01

> PowerWheels Jeep retrofitted with VESCs, Raspberry Pi 5, OAK-D cameras, and LiDAR — built as a platform for autonomous robotics development.  
> **UC San Diego — Jacobs School of Engineering**  

---

## ⚡ Overview

JeepBot is a modular robotics platform designed for:
- Embedded systems development
- Autonomous driving experiments
- Sensor integration (vision, LiDAR, GPS)

The system combines:
- Raspberry Pi (control + processing)
- VESC motor controllers (actuation)
- Multi-sensor perception stack

---

## 🚧 Current Status

- ✅ Fully assembled (hardware + wiring)
- ✅ VESCs configured and tested
- ❌ No full-system control (Pi ↔ VESC not implemented)
- ❌ Robot does not move yet

Main blockers:
- CAN control from Raspberry Pi
- Broken antispark switch (safety issue)
- LiDAR power issue
- Steering encoder integration

---

## 🧠 System Architecture

RC Controller → Receiver → Raspberry Pi → CAN → VESCs → Motors  
Sensors → Raspberry Pi → Processing

---

## 📂 Documentation

Full technical documentation is available in `/docs`:

- Overview → docs/overview.md  
- Hardware → docs/hardware.md  
- Software → docs/software.md  
- Current Status → docs/current_status.md  
- Setup Guide → setup/setup_guide.md  
- Troubleshooting → docs/troubleshooting.md  
- System Schematic → docs/system_schematic.md  

---

## 📸 Media

Images and system visuals are stored in:

docs/media/

---

## 🚀 Next Steps

- Implement CAN control (Pi → VESC)
- Fix power system issues
- Integrate sensors (cameras, LiDAR)
- Enable teleoperation
- Move toward autonomy

---

## 👥 Team

ECE/MAE 148 — UC San Diego  
Triton AI

---

## 📎 Resources

- Final Presentation → docs/ECE_MAE_148_Project_Final_Presentation.pdf  
- System Schematic → https://ucsdcloud-my.sharepoint.com/:u:/g/personal/kebraun_ucsd_edu/IQCRasxiZergSodErnQQG6UNAVxrW2Y3mB9if8TZqUndJ9E?e=tebVNc
