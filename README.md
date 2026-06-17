# 🚗 JeepBot | ECE/MAE 148 — Team 01

PowerWheels Jeep converted into a modular robotics platform for autonomous vehicle development, hardware integration, and controls experimentation.

Developed through UC San Diego ECE/MAE 148 in collaboration with Triton AI.

---

## ⚡ Overview

JeepBot is designed as a scalable and reproducible robotics platform combining:

- Raspberry Pi 5 for onboard computing and control
- VESC motor controllers for vehicle actuation
- OAK-D cameras for computer vision
- LiDAR and additional sensors for autonomous navigation
- ExpressLRS controller integration for manual control and testing

The project combines electrical integration, embedded systems, mechanical design, and software development.

---

## 🔧 Hardware Development

A major focus of this project was creating a clean, organized, and maintainable electronics architecture.

The system went through multiple hardware iterations:

### Version 1

- Initial full-scale architecture
- Designed around 5 VESC motor controllers
- More complex wiring system supporting multiple independent vehicle subsystems

### Version 2

- Simplified architecture using 2 VESC motor controllers
- Reduced wiring complexity
- Improved reliability and maintainability
- Redesigned to make the platform easier for future robotics students to reproduce, debug, and expand

The Version 2 redesign prioritizes accessibility while keeping the system expandable for future development.

Documentation for both versions:

`docs/version1/`

`docs/version2/`

---

## 📡 ELRS Controller Integration

The project includes development of a RadioMaster ExpressLRS controller interface for JeepBot testing and operation.

This allows manual control and testing during the development process while supporting future autonomous features.

Documentation and implementation:

`docs/elrs_controller/`

---

## 🧠 System Architecture

Control pipeline:

ExpressLRS Controller  
↓  
Receiver  
↓  
Raspberry Pi 5  
↓  
VESC Motor Controllers  
↓  
Motors / Steering  

Sensor pipeline:

OAK-D Cameras + LiDAR  
↓  
Raspberry Pi 5  
↓  
Autonomous Processing Stack  

---

## 📂 Repository Structure

CAD/

- electronics/
- mechanical/
- sensors/

docs/

- setup/
- version1/
- version2/
- elrs_controller/

src/

- jeepbot/
- camera/
- tests/

---

## 📚 Documentation

Technical documentation includes:

- Wiring diagrams
- Hardware revisions
- Raspberry Pi setup
- DepthAI/OAK-D setup
- ELRS controller integration
- Mechanical and electrical references

Main documentation:

`docs/`

---

## 🚧 Current Development Status

Completed:

✅ Vehicle hardware assembly  
✅ Electronics mounting and organization  
✅ VESC setup and configuration  
✅ Hardware architecture redesign (Version 1 → Version 2)  
✅ Documentation consolidation  

Ongoing:

- Continued software integration
- Sensor integration and testing
- Autonomous control development
- Future expansion toward the original 5-VESC architecture

---

## 👥 Team

ECE/MAE 148 — UC San Diego  
Triton AI