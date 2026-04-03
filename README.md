# 🚗 JeepBot | ECE/MAE 148 — Team 01

> A PowerWheels Jeep retrofitted with VESCs, a Raspberry Pi 5, dual OAK-D cameras, LiDAR, and GPS — built as a platform for autonomous robotics development.  
> **UC San Diego — Jacobs School of Engineering**  
> *Building on hardware developed by Team 02 (Spring 2026)*

📄 [Final Presentation (PDF)](docs/ECE_MAE_148_Project_Final_Presentation.pdf)

---

## ⚠️ Current Status

The robot is **mechanically complete and wired**, but not yet driving. Hardware integration is largely done — the main gap is software (Pi ↔ VESC CAN control) and a few outstanding hardware issues.

| Area | Status |
|---|---|
| All wiring (CAN, power, DC-DC) | ✅ Complete |
| PDB with fuses | ✅ Working |
| VESCs — CAN addressed & configured with motors | ✅ Done |
| Hall encoders — mounted & plugged into VESCs | ✅ Done |
| Raspberry Pi — flashed with firmware | ✅ Done |
| Sensor mounts (LiDAR, cameras, Pi) | ✅ Done |
| Robot movement | ❌ Not working — no code pushed to run VESCs via CAN |
| CAN (Pi ↔ VESC) | ❌ Not implemented |
| Antispark switch | ❌ Broken — allows power passthrough even when off (fire hazard) |
| LiDAR power | ❌ Pops 5A 24V fuse on PDB when plugged in (cause unknown) |
| Steering encoder | ❌ Not compatible with VESC — needs to connect directly to Pi |
| Emergency stop | ❌ Not connected |
| GPS | ❌ Not installed |
| CAN wires | ⚠️ Fragile — bending at JST connectors causes breaks |
| Battery placement | ⚠️ Needs to be in driver compartment — no space currently |

### 🔴 Remaining Blockers
1. Antispark switch allows power passthrough when off — fire hazard, needs replacement
2. No working emergency stop
3. LiDAR pops the 5A 24V fuse — root cause unknown
4. No CAN communication code from Pi to VESCs
5. Steering encoder (AS5600) is incompatible with VESC — must wire directly to Pi instead
6. Battery needs a dedicated compartment (driver seat area)

---

## 🏗️ System Architecture

```
User (RC Controller)
  → Radio Receiver
    → Raspberry Pi 5
      → CAN Bus (via CAN HAT)
          → VESC 1 (Back Left)
          → VESC 2 (Back Right)
          → VESC 3 (Front Left)
          → VESC 4 (Front Right)
          → VESC 5 (Steering)

Sensors (OAK-D Cameras, LiDAR, GPS, Encoders)
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
  → Antispark Switch  ⚠️ BROKEN — replace before use
    → Power Distribution Board (PDB)
        ├── VESC 1–5 (24V direct)
        ├── 24V→5V DC-DC → Raspberry Pi, USB Hub, Radio Receiver, OAK-D Cameras
        └── 24V→12V DC-DC → LiDAR  ⚠️ POPS FUSE — cause unknown
```

| Wire Gauge | Used For |
|---|---|
| 10 AWG | Battery & high-current power lines |
| 12 AWG | Motor wiring |
| 14–16 AWG | 5V electronics |
| 24 AWG | CAN bus |

**Connectors:** XT90 (battery / antispark / PDB input), XT60 (VESCs / DC-DC converters)

---

## 🔧 Motor & Control System

| VESC | Assignment |
|---|---|
| VESC 1 | Back Left wheel |
| VESC 2 | Back Right wheel |
| VESC 3 | Front Left wheel |
| VESC 4 | Front Right wheel |
| VESC 5 | Steering motor |

- **CAN bus** daisy-chains all VESCs (5-connector JST chain) → CAN HAT on Raspberry Pi
- CAN High = Yellow wire, CAN Low = Green wire
- ⚠️ CAN JST connectors are fragile — avoid sharp bends at the connector
- Each drive motor has a **Hall-effect encoder** plugged directly into its VESC
- Steering uses **AS5600 Magnetic Absolute Encoder** — must plug directly to Pi (not VESC)

---

## 📡 Sensors

| Sensor | Interface | Status |
|---|---|---|
| OAK-D Camera (front) | USB | Mounted — needs longer USB cable to reach hub |
| OAK-D Camera (rear) | USB | Mounted — not connected to hub |
| LiDAR | Ethernet (12V power) | Mounted — pops PDB fuse when plugged in |
| GPS module | USB | Not installed |
| Hall encoders (×4) | VESC direct | ✅ Mounted & working |
| AS5600 Steering encoder | Direct to Pi (I2C) | Mounted — not yet connected to Pi |

---

## 🖥️ Software & Control

**Platform:** Raspberry Pi 5  
**Access:** SSH or NoMachine  
**Pi firmware:** Flashed ✅ — peripherals not yet configured

**Intended control flow:**
```
RC Controller → Receiver → Raspberry Pi → CAN → VESCs → Motors
```

**Next software steps:**
- Interface all VESCs via CAN from the Pi
- Set up OAK-D cameras and LiDAR with the Pi
- Implement RC controller input → motor commands pipeline
- Eventually: DonkeyCar / autonomous navigation

---

## 🔩 Mechanical Mounts

All mounts are custom 3D-printed with heat-set inserts. Full CAD + installation guide:  
📄 [Complete Mounts Documentation (PDF)](https://drive.google.com/file/d/1jBLu-lDB1_-cbu3ugVZViqdFXvc3JRHq/view?usp=sharing)

| Mount | Description |
|---|---|
| Front camera mount | Forward-facing OAK-D, aligned to drive direction |
| Rear camera (bar mount) | Clamp-based attachment to structural bar |
| Rear camera (ridge mount) | Higher trunk position for rear perception |
| LiDAR mount | Top-mounted for 360° scanning |
| Raspberry Pi mount | Custom enclosure for secure chassis mounting |

---

## 🛠️ Setup Guide *(Work in Progress)*

> ⚠️ Do not connect the battery without reading this first. The antispark switch is broken — the system powers on immediately. Treat every connection as live.

**Steps needed before full operation:**
- [ ] Replace antispark switch
- [ ] Diagnose and fix LiDAR fuse issue (5A 24V rail on PDB)
- [ ] Get longer USB cables for front camera, LiDAR, and Pi/USB hub
- [ ] Connect cameras to powered USB hub
- [ ] Wire AS5600 steering encoder directly to Raspberry Pi (I2C)
- [ ] Connect emergency stop system
- [ ] Find battery placement solution (driver compartment area)
- [ ] Implement CAN control code on Pi (Pi → all 5 VESCs)
- [ ] Configure OAK-D cameras and LiDAR in software
- [ ] Install GPS module

**Connecting to the Pi:**
```bash
ssh <user>@<pi-ip>       # or use NoMachine
```

---

## 🔨 Hardware Task Reference *(for students picking this up)*

Complete list of hardware tasks performed by the original team — useful if redoing or extending any part of the build:

- Redo soldering on drive motors using 12 AWG silicone wire
- Create 5-connector CAN daisy chain using JST crimps
- Crimp JST encoder connectors to VESCs
- Solder MR60 connectors to all motors and VESCs
- 3D print mounts and install heat-set inserts
- Solder XT60 connectors to VESCs, PDB, 5V buck, and 12V buck
- Solder XT90 connectors to battery cables, antispark, and PDB input
- Crimp blade connectors to battery cables
- Solder blade fuse sockets to PDB and insert fuses
- Solder cables in/out of 12V and 5V buck converters
- Solder 2× USB-C cables to XT30/60 connector on 5V buck

---

## 🧯 Troubleshooting

<details>
<summary><strong>Robot not moving</strong></summary>

- No CAN control code has been pushed to the Pi — this is the primary blocker
- Verify Pi is powered and accessible via SSH/NoMachine
- Confirm CAN wiring from VESCs reaches the CAN HAT terminal on the Pi
- Check all VESCs are receiving 24V from PDB
- Verify RC controller and receiver are paired

</details>

<details>
<summary><strong>LiDAR pops the fuse</strong></summary>

- The LiDAR pops the 5A 24V fuse on the PDB when plugged in — root cause unknown at handoff
- Check for a short in the 12V DC-DC converter wiring or LiDAR power cable
- Try a higher-rated fuse temporarily to determine if it's a current spike vs. a dead short
- Inspect the LiDAR power connector for damage

</details>

<details>
<summary><strong>No power / inconsistent power</strong></summary>

- Antispark switch is broken — system powers on as soon as the battery is connected
- Do not rely on the switch for any safety function
- Physically disconnect the XT90 to cut power
- Check PDB fuse status for each rail

</details>

<details>
<summary><strong>Cannot connect to Raspberry Pi</strong></summary>

- Verify Pi is receiving 5V
- Confirm WiFi/network configuration
- Check SSH or NoMachine settings
- Pi was reflashed — some environment setup may need to be redone

</details>

<details>
<summary><strong>Steering not working</strong></summary>

- The AS5600 encoder is **not compatible with direct VESC input** — do not try to wire it to VESC 5
- Wire the AS5600 directly to the Raspberry Pi via I2C
- Read steering angle in software and send position commands to VESC 5 from the Pi
- VESC 5 is configured and connected to the steering motor — just needs software-side control loop

</details>

<details>
<summary><strong>CAN communication issues</strong></summary>

- CAN wiring between all 5 VESCs is complete and working
- The CAN lines still need to be connected to the CAN HAT terminal block on the Pi
- Yellow = CAN High, Green = CAN Low
- ⚠️ JST connectors at each VESC are fragile — inspect for wire breaks if CAN is intermittent

</details>

<details>
<summary><strong>Safety / emergency stop</strong></summary>

⚠️ The emergency stop system is **not connected**.  
If anything goes wrong: **physically disconnect the XT90 battery connector**.  
Do not rely on the antispark switch — it passes power even when switched off.

</details>

---

## 📷 Media

> Images are stored in `docs/media/`. Export photos from the original Google Doc or presentation and place them in that folder using the filenames below.

| Preview | Description |
|---|---|
| ![AS5600 Encoder](docs/media/as5600_encoder.jpg) | AS5600 magnetic encoder in custom yellow 3D-printed holder |
| ![Internal Wiring](docs/media/internal_wiring.jpg) | Top-down view of chassis — VESCs, PDB, encoder mounts |
| ![PDB Fuse Block](docs/media/pdb_fuse_block.jpg) | PDB with active fuse block and XT connectors |
| ![Underside Motors](docs/media/underside_motors.jpg) | Underside — motors, Hall encoders, and VESC wiring |
| ![Front Assembly](docs/media/front_assembly.jpg) | Front of jeep — LiDAR on hood, OAK-D camera below |
| ![Full Jeep Side](docs/media/jeep_side_view.jpg) | Full vehicle side view with all hardware mounted |

**Videos:**
- 🎥 [Both Cameras Demo](https://drive.google.com/file/d/1gASmeuNE30h5Eg7waWI6OVzTFIr_cnO4/view?usp=sharing) — Dual OAK-D setup demonstrating depth map and RGB output

---

## 🔮 Advice for Future Teams

**Hardware:**
- Wire the AS5600 absolute encoder directly to the Raspberry Pi via I2C — not to the steering VESC
- Get longer USB cables for the front camera, LiDAR, and Pi/USB hub connections
- Install a GPS module (the original team never received one)
- A game controller is a simpler starting point before setting up the Radiomaster RC system

**Software:**
- First priority: interface all 5 VESCs via CAN from the Pi
- Then configure OAK-D cameras and LiDAR as Pi peripherals
- DonkeyCar is a reasonable starting framework for autonomous behavior

---

## 📎 Resources

| Resource | Link |
|---|---|
| Final Presentation | [PDF](docs/ECE_MAE_148_Project_Final_Presentation.pdf) |
| System Schematic | [View Schematic](https://ucsdcloud-my.sharepoint.com/:u:/g/personal/kebraun_ucsd_edu/IQCRasxiZergSodErnQQG6UNAVxrW2Y3mB9if8TZqUndJ9E?e=tebVNc) |
| Mounts Documentation | [Google Drive PDF](https://drive.google.com/file/d/1jBLu-lDB1_-cbu3ugVZViqdFXvc3JRHq/view?usp=sharing) |
| Dual Camera Demo | [Google Drive Video](https://drive.google.com/file/d/1gASmeuNE30h5Eg7waWI6OVzTFIr_cnO4/view?usp=sharing) |

---

## 👥 Team

All hardware design, fabrication, wiring, and mechanical integration was completed by the original ECE/MAE 148 team. This repo documents their work, with ongoing contributions toward Raspberry Pi software setup.

| Name | Major | Contributions |
|---|---|---|
| **Yves Mojica** | Electrical & Computer Engineering | VESC wiring & setup, Raspberry Pi mount design |
| **Brent Brewster** | Electrical & Computer Engineering | Encoder mounting, Raspberry Pi setup |
| **Dylan Lee** | Mechanical & Aerospace Engineering | Power wiring, CAN wiring |
| **Keenai Braun** | Mechanical & Aerospace Engineering | Camera mounts, LiDAR mount design |

*A strong hardware foundation was laid for future teams to build on — despite challenges including a lab fire, order delays, and hardware compatibility issues discovered late in the quarter.*

---

## 🎓 About

**Course:** ECE/MAE 148 — Autonomous Vehicles  
**Institution:** UC San Diego — Jacobs School of Engineering  
**Organization:** [Triton AI](https://triton-ai.org)  
**Presented:** March 19, 2026
