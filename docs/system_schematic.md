# Schematic

[View Full Schematic](https://ucsdcloud-my.sharepoint.com/:u:/g/personal/kebraun_ucsd_edu/IQCRasxiZergSodErnQQG6UNAVxrW2Y3mB9if8TZqUndJ9E?e=tebVNc)

---

## 1. Power System

All system components are powered by a 24V lead-acid battery.

**Main power flow:**
24V Battery → Antispark Switch → Power Distribution Board (PDB)

The antispark switch prevents large inrush currents and allows safe power control.

The PDB distributes 24V power to all subsystems:

### Motor Controllers
- VESC 1 – Back Left wheel  
- VESC 2 – Back Right wheel  
- VESC 3 – Front Left wheel  
- VESC 4 – Front Right wheel  
- VESC 5 – Steering motor  

### Voltage Converters

**24V → 5V DC-DC**
- Raspberry Pi 5  
- Radio Receiver  
- Two OAK-D cameras  

**24V → 12V DC-DC**
- LiDAR sensor  

---

## 2. Computing System

The Raspberry Pi 5 is the main onboard computer.

### USB Devices (via Powered Hub)
- Two OAK-D cameras  
- GPS module  

### Direct Connections
- Radio receiver  

### LiDAR
- Powered by 12V  
- Communicates via Ethernet  

---

## 3. Motor and Steering Control

### Drive System
- 4 VESCs control wheel motors  
- Each motor uses a Hall encoder  

### Steering
- VESC 5 controls steering  
- Absolute encoder provides angle feedback  

---

## 4. System Communication

Uses a **CAN bus network**.

### Enables:
- Command transmission  
- Synchronization  
- Feedback data  

### Wiring
- Yellow → CAN High  
- Green → CAN Low  

Connected via CAN HAT on Raspberry Pi.

---

## 5. Emergency Stop System

Three physical switches:
- Front  
- Rear  
- Central  

+ Remote stop via radio control  

---

## 6. Radio Control System

- Radiomaster transmitter  
- Receiver connected to Raspberry Pi  

Enables:
- Teleoperation  
- Safety override  

---

## 7. Steering PID

PID_P = TBD
PID_I = TBD
PID_D = TBD

---

## 8. System Flow

The 24V battery powers the system through the antispark switch and PDB.

- VESCs control motors  

- DC-DC converters power electronics  

- Raspberry Pi handles control and perception  

- CAN bus connects controllers  

- Sensors provide feedback  

Emergency systems ensure safe shutdown.

## Notes
This schematic is intended as a high-level system overview and should be updated as the hardware integration evolves.
