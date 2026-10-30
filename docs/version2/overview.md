# Overview

This system is a modified PowerWheels Jeep platform designed for robotics development.

The architecture is centered around a 24V power system with distributed control, sensing, and computation. The system integrates motor control (VESC), onboard computing (Raspberry Pi 5), sensor fusion (OAK-D cameras, LiDAR, GPS), and a safety layer with emergency stop functionality.

## High-Level Flow

Battery → EMO → Antispark → PDB → Subsystems

- Power is distributed to:
  - Motor controllers (VESC)
  - DC-DC converters (12V and 5V)
- Raspberry Pi acts as the central compute node
- Arduino handles safety and emergency stop logic
- Sensors feed data through USB and communication interfaces

This modular architecture allows easy debugging, expansion, and subsystem isolation.

## Progress Update
### Till 10/29/2026
- Completely reorganized the whole panel.
- Removed the unnecessary long wires underneath the panel 
- Soldered new wires(Tested with Multi-meter). The board is clean and ready to fit Jeston Orin Nano. (Xuanyu)
- Replaced 5V DC-DC converter with 12V DC-DC converter to support Jeston Orin Nano(Junyang, Xuanyu)
- 3D-printed mounting case for Jeston Orin Nano and placed it on the board.(Junyang, Aidan) Source: https://makerworld.com/zh/models/2152694-jetson-orin-nano-case-now-with-csi-port#profileId-2505964
-Collect the orders of necessary power adaptors and cables to power the Jetson Orin Nano and the additional VESCs, also new parts ordered for 4 VESC implementation
- LED Compartment designed and 3D printed to hold on top of car
- Following tasks once the VESCs arrived: integrate the LFP battery to power up the four additional motor VESCs, enable skid steering



