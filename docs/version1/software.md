## 1. Software Overview

The robot uses a Raspberry Pi 5 as the main computer responsible for system control, communication, and data processing.

The software system handles:

- Receiving user input (RC controller / teleoperation)  
- Sending commands to motor controllers (VESCs)  
- Reading and processing sensor data  
- Managing communication between system components  

This architecture enables centralized control while remaining modular for future upgrades.

---

## 2. Control Flow

**Primary control path:**

User Input → Radio Receiver → Raspberry Pi → CAN Bus → VESC → Motors

**Sensor data flow:**

Sensors → Raspberry Pi → Data Processing / Logging

The Raspberry Pi translates inputs into motor commands and collects sensor data.

---

## 3. Teleoperation

Teleoperation enables manual control during development.

### RC Controller (Primary Method)
RC → Receiver → Raspberry Pi → CAN → VESC → Motors

- Low latency  
- High reliability  
- No internet required  

### ROS2 Teleoperation (Future)
Laptop → WiFi → Raspberry Pi → CAN → VESC

- Integrates sensor data  
- Enables autonomy development  

### Web Dashboard (Optional)
Web → WiFi → Raspberry Pi → Motors

- Simple control interface  
- Displays sensor data  

### Strategy

- RC Controller → primary control  
- ROS2 → advanced/autonomous control  
- Web dashboard → visualization  

---

## 4. Sensor Data Handling

Connected sensors:

- OAK-D cameras  
- LiDAR  
- GPS (pending)  
- Motor encoders  

Used for:

- System monitoring  
- Data collection  
- Future autonomy  

Processing is done locally on the Raspberry Pi.

---

## 5. Running the System (Basic)

- Power on system  
- Connect to Raspberry Pi (SSH / NoMachine)  
- Run control software  
- Drive using RC controller  

*Commands will be added once finalized.*

---

## 6. Future Development

Planned improvements:

- Autonomous navigation  
- Sensor fusion  
- Obstacle detection  
- Path planning  
- Improved CAN control  
- Full Pi ↔ VESC integration  
