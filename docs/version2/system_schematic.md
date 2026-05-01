# System Schematic

## Power Path

Battery (24V Lead Acid)
→ EMO (Emergency Stop)
→ Antispark Switch
→ PDB (Power Distribution Board)

From PDB:
- VESC Motor Controller (Drive motors)
- VESC Steering Controller
- DC-DC 24V → 12V (LiDAR)
- DC-DC 24V → 5V (Logic + Compute)

## Compute and Control

- Raspberry Pi 5:
  - Central processing unit
  - Receives sensor data
  - Sends control signals

- Arduino:
  - Handles emergency stop logic
  - Controls relay shutdown

## Sensors

- OAK-D Cameras (x2)
- LiDAR
- GPS

Connected via:
- USB (through powered hub)
- Serial / signal interfaces
