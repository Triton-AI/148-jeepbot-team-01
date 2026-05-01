## Setup Guide

This section is a work in progress and will be updated as the system is finalized. The current setup process is incomplete and may not fully result in a working robot.

---

## 1. Current Setup Status

- The system is not fully operational  
- Several hardware connections are incomplete  
- Software setup on the Raspberry Pi is not finalized  
- This reflects the current partial workflow  

---

## 2. Powering the System (Current Behavior)

- Connect the battery (XT90)  
- System powers on immediately (antispark is broken)  
- Antispark switch does not control power  

**Important:**

- No safe way to interrupt power  
- Use caution when connecting the battery  

---

## 3. Power System Limitations

- Raspberry Pi may not receive power  
- USB hub may not be powered  
- LiDAR is not powered (PDB fuse issue)  
- Some components may turn on while others remain off  

---

## 4. Connecting to the Raspberry Pi

Access methods:

- SSH  
- NoMachine  

**Notes:**

- Raspberry Pi was reflashed → environment may not be configured  
- Setup may vary depending on configuration  
- Standard process not yet defined  

---

## 5. Current Operation Method (Partial)

**Expected:**

RC → Receiver → Raspberry Pi → CAN → VESC → Motors  

**Current:**

- RC receiver not fully connected  
- Raspberry Pi not sending commands  
- CAN not implemented  
- Robot does not move  

---

## 6. Sensors and Perception Setup

- Cameras mounted but not connected  
- Front camera needs longer cable  
- LiDAR installed but not powered  
- GPS not available  

---

## 7. Steering System Status

- Steering motor connected  
- Steering encoder not connected  
- Encoder not compatible with VESC  
- Steering not functional  

---

## 8. Required Steps Before Full Operation

- Replace antispark switch  
- Fix PDB fuse (restore LiDAR power)  
- Connect 5V power to Pi and USB hub  
- Complete CAN wiring to Pi (CAN HAT)  
- Connect cameras  
- Integrate steering encoder  
- Install and verify software  
- Implement control scripts  

---

## 9. Notes

- This guide reflects an incomplete system  
- Steps will change as development continues  
- A full operational guide will be added later  
