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
