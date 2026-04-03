# 🚗 JeepBot — Triton AI | Team 01

> A small autonomous ground vehicle built on a modified electric jeep platform, designed for environmental data collection and development of an automated garden system (AI-AGE / AGS).

---

## ⚠️ Current Status: Non-Operational

The robot is **fully assembled mechanically** but not yet operational due to hardware and software integration issues.

| Area | Status |
|---|---|
| Mechanical assembly | ✅ Complete |
| Drive VESCs (×4) | ✅ Configured & tested |
| CAN bus (VESC-to-VESC) | ✅ Working |
| Raspberry Pi mounted | ✅ Installed |
| Robot movement | ❌ Not working |
| CAN (Pi ↔ VESC) | ❌ Not implemented |
| Steering encoder | ❌ Not connected / incompatible |
| Antispark switch | ❌ Broken (unsafe) |
| Emergency stop | ❌ Not connected |
| LiDAR power | ❌ PDB fuse issue |
| Cameras (USB) | ❌ Not connected to hub |
| GPS | ❌ Not installed |
| Software (Pi) | ❌ Incomplete / reflashed |

### 🔴 Blocking Issues
1. Broken antispark switch → system powers on unsafely
2. No emergency stop connected → no safe shutdown
3. No CAN communication from Raspberry Pi to VESCs
4. Steering encoder not connected / incompatible with VESC
5. LiDAR power failure (PDB fuse / connector)
6. Critical 5V and USB connections incomplete

---

## 🏗️ System Architecture

```
User (RC Controller)
  → Radio Receiver
    → Raspberry Pi 5
      → CAN Bus (via CAN HAT)
        → VESC 1–4 (drive motors)
        → VESC 5 (steering)

Sensors (Cameras, LiDAR, GPS, Encoders)
  → Raspberry Pi 5
    → Data Processing / Logging
```

**Three main subsystems:**
- **Brain** → Raspberry Pi 5
- **Actuation** → 5× VESC motor controllers + motors
- **Perception** → 2× OAK-D cameras, LiDAR, GPS, encoders

---

## ⚡ Power System

```
24V Lead-Acid Battery (7Ah)
  → Antispark Switch  ⚠️ BROKEN
    → Power Distribution Board (PDB)
      ├── VESC 1–5 (24V direct)
      ├── 24V→5V DC-DC → Raspberry Pi, USB Hub, Radio Receiver, Cameras
      └── 24V→12V DC-DC → LiDAR  ⚠️ FUSE ISSUE
```

| Wire Gauge | Used For |
|---|---|
| 10 AWG | Battery & high-current lines |
| 12 AWG | Motor wiring |
| 14–16 AWG | 5V electronics |
| 24 AWG | CAN bus |

**Connectors:** XT90 (battery), XT60 (distribution / DC-DC)

---

## 🔧 Motor & Control System

| VESC | Assignment |
|---|---|
| VESC 1 | Back Left wheel |
| VESC 2 | Back Right wheel |
| VESC 3 | Front Left wheel |
| VESC 4 | Front Right wheel |
| VESC 5 | Steering motor |

- **CAN bus** daisy-chains all VESCs → CAN HAT on Raspberry Pi
- CAN High = Yellow wire, CAN Low = Green wire
- Each drive motor has a **Hall-effect encoder** (8-pin, 4 active pins)
- Steering uses **AS5600 Magnetic Absolute Encoder** (I2C) — *not yet integrated*
- Steering PID: P/I/D = TBD (tuning phase)

---

## 📡 Sensors

| Sensor | Interface | Status |
|---|---|---|
| OAK-D Camera (front) | USB | Mounted, not connected |
| OAK-D Camera (rear) | USB | Mounted, not connected |
| LiDAR | Ethernet (12V power) | Installed, no power |
| GPS module | USB | Not installed |
| Hall encoders (×4) | VESC direct | ✅ Working |
| AS5600 Steering encoder | I2C | Not connected |

---

## 🖥️ Software & Control

**Platform:** Raspberry Pi 5 running Linux  
**Access:** SSH or NoMachine

**Control flow (planned):**
```
RC Controller → Receiver → Raspberry Pi → CAN → VESCs → Motors
```

**Teleoperation methods:**

| Method | Path | Status |
|---|---|---|
| RC Controller | RC → Receiver → Pi → CAN → VESC | Primary (incomplete) |
| ROS2 | Laptop → WiFi → Pi → CAN → VESC | Planned |
| Web Dashboard | Browser → WiFi → Pi | Optional |

**Future development:** autonomous navigation, sensor fusion, obstacle detection, path planning.

---

## 🔩 Mechanical Mounts

All mounts are custom 3D-printed. Full CAD + installation guide:  
📄 [Complete Mounts Documentation (PDF)](https://drive.google.com/file/d/1jBLu-lDB1_-cbu3ugVZViqdFXvc3JRHq/view?usp=sharing)

| Mount | Description |
|---|---|
| Front camera mount | Forward-facing OAK-D, aligned to drive direction |
| Rear camera (bar mount) | Clamp-based attachment to structural bar |
| Rear camera (ridge mount) | Higher position on trunk for rear perception |
| LiDAR mount | Top-mounted for 360° scanning |

---

## 🛠️ Setup Guide *(Work in Progress)*

> ⚠️ The system is not fully operational. These steps reflect the current partial workflow.

**Before anything:** the antispark switch is broken — the system powers on immediately when the battery is connected. Use extreme caution.

**Steps needed before full operation:**
- [ ] Replace antispark switch
- [ ] Fix PDB fuse, restore LiDAR power line
- [ ] Connect 5V DC-DC output to Raspberry Pi and USB hub
- [ ] Finish CAN wiring to Raspberry Pi CAN HAT terminal
- [ ] Connect cameras to powered USB hub (front needs longer cable)
- [ ] Integrate steering encoder (may need different encoder or adapter)
- [ ] Install and verify software on Raspberry Pi
- [ ] Implement RC → Pi → VESC control scripts

**Connecting to the Pi:**
```bash
ssh <user>@<pi-ip>       # or use NoMachine
```

---

## 🧯 Troubleshooting

<details>
<summary><strong>Robot not moving</strong></summary>

- Verify Raspberry Pi is powered and accessible
- Confirm CAN wiring is connected to CAN HAT
- Check VESCs are receiving 24V from PDB
- Verify RC controller/receiver are paired and connected
- Confirm control software is running

</details>

<details>
<summary><strong>No power / inconsistent power</strong></summary>

- Antispark switch is broken — system always powers on
- Inspect PDB fuse status (especially LiDAR line)
- Verify XT90/XT60 connectors are secure
- Confirm 5V output is wired to Raspberry Pi and USB hub

</details>

<details>
<summary><strong>Cannot connect to Raspberry Pi</strong></summary>

- Verify Pi is receiving 5V (wiring is currently incomplete)
- Confirm network/WiFi settings
- Check SSH or NoMachine configuration
- Note: Pi was reflashed — environment may need reconfiguration

</details>

<details>
<summary><strong>Sensors not working</strong></summary>

- Cameras: verify USB connections to powered hub
- LiDAR: check PDB fuse and 12V power line
- GPS: not installed yet
- Confirm USB hub itself is powered

</details>

<details>
<summary><strong>Steering not working</strong></summary>

- AS5600 encoder is not connected to VESC 5
- Encoder uses I2C (designed for microcontrollers, not direct VESC input)
- May require adapter circuit or replacement encoder
- Steering VESC config cannot be completed without encoder feedback

</details>

<details>
<summary><strong>CAN communication issues</strong></summary>

- Verify daisy-chain wiring between all VESCs
- Connect CAN lines to CAN HAT terminal block on Raspberry Pi
- Yellow = CAN High, Green = CAN Low
- CAN between VESCs works; Pi↔VESC CAN not yet implemented

</details>

<details>
<summary><strong>Safety / emergency</strong></summary>

⚠️ Emergency stop system is **not connected**.  
If unexpected movement, overheating, sparks, or noise occur:  
**Physically disconnect the XT90 battery connector immediately.**  
Do not rely on the antispark switch.

</details>

---

## 📷 Media

> Images are stored in `docs/media/`. Add the image files to that folder and they will render here.

| Preview | Description |
|---|---|
| ![OAK-D Depth Map](docs/media/oakd_depth_map.jpg) | OAK-D camera generating a real-time depth map |
| ![OAK-D RGB Output](docs/media/oakd_rgb.jpg) | OAK-D camera standard RGB image output |
| ![Hardware Components](docs/media/hardware_components.jpg) | Packaged Raspberry Pi units and protective enclosures |
| ![VESC Connectors](docs/media/vesc_connectors.jpg) | VESC controller with labeled CAN, SENSE, COMM, SWD, USB interfaces |
| ![Power Wiring](docs/media/power_wiring.jpg) | Red high-current power cable spool |
| ![PDB & DC-DC Converters](docs/media/pdb_dcdc.jpg) | PDB and DC-DC converters installed inside chassis |
| ![Fuse Block & XT Connectors](docs/media/fuse_block.jpg) | Internal fuse block, XT connectors, and battery power wiring |
| ![Steering Encoder](docs/media/steering_encoder.jpg) | Steering encoder mounted inside chassis |
| ![AS5600 Encoder](docs/media/as5600_encoder.jpg) | AS5600 magnetic encoder in custom 3D-printed holder |
| ![Motors & Hall Encoders](docs/media/motors_encoders.jpg) | Underside view — motors, Hall encoders, and VESC wiring |
| ![Internal Wiring](docs/media/internal_wiring.jpg) | VESC controllers, power connections, and encoder wiring inside chassis |
| ![Rear Structure](docs/media/rear_structure.jpg) | Rear of Jeep with mounted camera and electronics bay |
| ![Front Assembly](docs/media/front_assembly.jpg) | Fully assembled front — LiDAR and front OAK-D camera |

**Videos:**
- 🎥 [Both Cameras Demo](https://drive.google.com/file/d/1gASmeuNE30h5Eg7waWI6OVzTFIr_cnO4/view?usp=sharing) — Dual OAK-D camera setup with front and rear perception

---

## 📎 Resources

| Resource | Link |
|---|---|
| System Schematic | [View Schematic](https://ucsdcloud-my.sharepoint.com/:u:/g/personal/kebraun_ucsd_edu/IQCRasxiZergSodErnQQG6UNAVxrW2Y3mB9if8TZqUndJ9E?e=tebVNc) |
| Mounts Documentation | [Google Drive PDF](https://drive.google.com/file/d/1jBLu-lDB1_-cbu3ugVZViqdFXvc3JRHq/view?usp=sharing) |
| Dual Camera Demo | [Google Drive Video](https://drive.google.com/file/d/1gASmeuNE30h5Eg7waWI6OVzTFIr_cnO4/view?usp=sharing) |

---

## 🎓 About

This project is part of **Triton AI** at UC San Diego. It is designed to be educational and accessible, giving students hands-on experience with robotics, electronics, and AI systems.
