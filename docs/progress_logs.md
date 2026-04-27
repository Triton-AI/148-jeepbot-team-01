## 1. Overview

This section tracks the progress of the project, including completed work, current status, and next steps.

It documents development over time and helps maintain alignment across the team.

---

## 2. Timeline of Progress

### March 9

- GitHub repository created and organized  
- System schematic work started  
- Initial research on teleoperation solutions  
- Planning for camera streaming on Raspberry Pi  

### March 11

- Focus on documenting hardware system  
- Wiring, connectors, and power system analyzed  
- Internal system components identified  
- Communication with team regarding missing components  

### March 17

- Structured project documentation created  
- Overview, hardware, and system architecture documented  
- Mechanical mounts documentation integrated  
- Setup, troubleshooting, and BOM sections started (WIP)  

### March 18

- Initial full-system test performed  
- Preparation for Phase 1 demo  
- Knowledge transfer initiated  
- RC controller operation documented  
- Codebase migrated to TritonAI repository  
- Future development path identified  

### March 20

**Hardware Integration**

- All major components mounted (Pi, cameras, LiDAR housing)  
- Battery installed under seat (XT90 routing)  

**Power System**

- Antispark switch broken (does not interrupt power)  
- System powers on immediately (unsafe)  
- PDB fuse missing/damaged (LiDAR inactive)  
- 5V DC-DC cables too short  
- Pi and USB hub not properly powered  

**Control & Communication**

- Raspberry Pi mounted with CAN HAT  
- CAN between VESCs functional  
- CAN not connected to Pi yet  
- VESCs tested individually  
- No full-system control implemented  

**Steering System**

- Steering VESC connected  
- Encoder not connected  
- Encoder incompatible with VESC  
- Steering non-functional  

**Sensors**

- Cameras mounted but not connected  
- Front camera needs longer cable  
- LiDAR not powered  
- GPS not available  

**Software**

- Raspberry Pi reflashed  
- Environment not verified  
- Control software not implemented  
- System not operational  

---

### April 16 — Meeting Notes

**Hardware Layout**

- Electronics positioned in front  
- Battery moved to front  
- Steering VESC in front  
- Motor VESC in back  

**System Architecture Change**

- Simplified from 5 VESCs → 2 VESCs  
- 1 for steering  
- 1 for drive  
- CAN multi-VESC system removed  

**Power System**

- Battery → antispark → system  
- Antispark used as main switch  

**Wiring**

- Routed front → back  
- Cable management required  
- Motor polarity must be verified  

**Emergency Stop**

- Placement not finalized  
- Must be accessible  

**Sensors**

- Current LiDAR acceptable  
- Future upgrade planned  

**Mechanical**

- Plan for modular mounting plate  
- Laser-cut design  
- Flexible layout  

---

## 3. Current Status

The project is in the hardware integration and system bring-up phase.

### Completed

- Mechanical system assembled  
- Wiring infrastructure implemented  
- VESCs tested individually  
- Encoders mounted  
- Raspberry Pi installed  
- Sensors mounted  
- Documentation structured  

### In Progress

- Software integration  
- Pi ↔ VESC communication  
- Teleoperation setup  
- Wiring cleanup  
- Sensor connectivity  

---

## 4. Next Steps

- Replace antispark switch  
- Fix PDB fuse (LiDAR power)  
- Complete 5V connections  
- Finish CAN wiring  
- Integrate steering encoder  
- Connect cameras and LiDAR  
- Configure Raspberry Pi software  
- Implement RC control via Pi  
- Validate full system  

---

## 5. Key Challenges

- Broken antispark (safety risk)  
- PDB fuse issue  
- No system movement  
- Steering not working  
- Incomplete wiring  
- No emergency stop  
- Software not ready  

---

## 6. Notes

- This section will be continuously updated  
- Major issues and milestones should be recorded  
