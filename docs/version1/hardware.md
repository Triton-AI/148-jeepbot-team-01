## 1. Hardware Architecture Overview

The robot hardware system is organized into three main layers:

- Power layer → provides energy to all components  
- Control layer → processes commands and controls movement  
- Sensor layer → collects environmental and system data  

Power flows from the battery through the Power Distribution Board (PDB), while the Raspberry Pi acts as the central controller.

---

## 2. Battery and Main Power System

The robot is powered by a 24V lead-acid battery:

- Voltage: 24V  
- Capacity: 7Ah  

**Power path:**  
Battery → Antispark Switch → Power Distribution Board (PDB)

- Antispark switch prevents inrush current  
- PDB distributes power and provides fuse protection  

---

## 3. Power Distribution

Power from the PDB is distributed to:

- VESC motor controllers  
- DC-DC converters  
- Onboard electronics  

**Voltage regulation:**

- 24V → motors (via VESCs)  
- 24V → 12V → LiDAR  
- 24V → 5V → Raspberry Pi, USB hub, sensors  

---

## 4. Wiring

Silicone insulated stranded wire is used for:

- Flexibility  
- Heat resistance  
- Vibration tolerance  

**Wire gauges:**

- 10 AWG → battery / high-current  
- 12 AWG → motors  
- 14–16 AWG → 5V electronics  
- 24 AWG → CAN bus  

---

## 5. Power Connectors

XT-series connectors are used:

- XT90 → battery  
- XT60 → distribution / converters  

Benefits:

- High current support  
- Reverse polarity protection  
- Strong connections  

---

## 6. Battery Power Cable

- 10 AWG silicone wire  
- Handles highest current in system  
- Connects battery → antispark → PDB  

---

## 7. Power Distribution Board (PDB)

The PDB:

- Distributes power to all subsystems  
- Connects VESCs and converters  
- Includes fuse protection  

Mounted inside the chassis.

---

## 8. Internal Wiring Layout

Connects:

- Motor controllers  
- Steering system  
- Encoders  
- Raspberry Pi  
- PDB  

Design goals:

- Minimize cable length  
- Reduce noise  
- Improve debugging access  

---

## 9. Motor Control System (VESC)

Five VESC controllers:

- VESC 1 → Back Left  
- VESC 2 → Back Right  
- VESC 3 → Front Left  
- VESC 4 → Front Right  
- VESC 5 → Steering  

Controls:

- Speed  
- Torque  
- Direction  

---

## 10. Encoder System

### Motor Encoders (Hall-effect)

- Provide rotor position  
- Connected to VESC  
- Enable precise control  

### Steering Encoder

- AS5600 magnetic sensor  
- I2C communication  
- Measures steering angle  

### Additional Encoder

- REV Through Bore Encoder  
- High-resolution rotation sensing  

---

## 11. Communication Interfaces

- CAN Bus → VESC network  
- USB → cameras, GPS (via hub)  
- I2C → steering encoder  
- Radio → RC → Pi  

---

## 12. Raspberry Pi (Main Controller)

Raspberry Pi 5 handles:

- Control logic  
- Communication with VESCs  
- Sensor data processing  

Connected to:

- CAN HAT  
- USB hub  
- Cameras  
- GPS  
- Radio receiver  

---

## 13. Sensors

- 2× OAK-D cameras → vision  
- LiDAR → mapping  
- GPS → localization  
- Encoders → motion + steering  

---

## 14. Physical Layout

- Battery → rear  
- PDB → center  
- Pi → communication hub  
- VESCs → near motors  
- Sensors → external  

Improves:

- Weight distribution  
- Wiring efficiency  
- Accessibility  

---

## 15. Emergency Stop System

- Multiple emergency stop buttons  
- Interrupt motor control signals  
- Immediately stop motion  

---

## 16. Safety and Best Practices

- Disconnect battery before working  
- Verify polarity  
- Avoid shorts on PDB  
- Secure all connections  
- Keep emergency stops accessible  

---

## 17. Current Limitations

- Wiring organization can improve  
- Cable management incomplete  
- Some components exposed  
- Steering encoder not fully integrated  
- Layout may change during development  
