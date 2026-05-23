## 1. Overview
This section tracks the progress of the project, including completed work, current status, and next steps.

It documents development over time and helps maintain alignment across the team.

---

## 2. Timeline of Progress

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

### April 29 — Updates

- Schematics updated 
- Wiring requires significant work
- GitHub repository received positive feedback:
  - Past documents will be organized under **Version 1**  
  - A new **Version 2** will be created for updated work and ongoing progress  
- Team was asked to document progress with as many photos as possible this week for presentation purposes  

---

### April 30 — Updates

**Completed Work**
- Final laser cuts for electronics mounting plates completed
- First iteration of mechanical mounts 3D printed
- Feedback provided to MAP mechanical team for improvements
- GitHub repository reorganized:
  - Version 1 (past work)
  - Version 2 (current + ongoing work)
- Initial system documentation created (overview, hardware, software, etc.)
- Schematics updated based on recent discussions

---

### May 1 — Updates (Meeting)

- Emphasized the importance of consistently taking photos and documenting our work
- This will be useful for future classes and for the next group of students

---

### May 6 — Updates (Lab Work)

**System Architecture / PDB Changes**
- System updated from 2 PDBs → 4 PDB configuration
- Front PDB:
  - powers steering VESC
  - sends power to rear PDB
- Rear PDB distributes power to:
  - motor VESC
  - 24V → 5V DC-DC converter
  - 24V → 12V DC-DC converter

**Completed Work**
- Rear XT60 → XT60 PDB completed
- Front XT90 → XT60 PDB partially completed
- Front-to-back 10 AWG XT60M → XT60F power cable assembled
- Significant wire labeling completed

**Documentation**
- System schematic updated to reflect latest architecture
- Editable SharePoint schematic link updated
- GitHub documentation under version2 continues to be updated

**Outstanding Tasks**
- Acquire XT90 connector for front PDB input
- Build XT60 → XT30 PDBs for DC-DC converters
- Finalize EMO integration with the rest of the system
- Locate relay/current-handling component required for EMO implementation
- Continue documentation and progress photos

**Notes**
- Additional schematic review recommended before final wiring implementation

---

### May 8 — Updates (Meeting)

- Prof. Jack suggested checking with Corey for extra XT90 connectors before ordering new ones on Amazon
- Corey may already have pre-soldered XT90 connectors available
- Relay components should already be located in the team workbench according to Prof. Silberman
- Need to confirm the micro PDB splitter setup with Jose
- Current goal is to get the JeepBot physically running by Monday
- Goal for the next meeting is to achieve basic remote control functionality
- Additional support from another ECE/MAE 148 team will assist with the JeepBot project
- Possible meeting with the assisting 148 team planned for next week depending on availability

---

### May 14 — Updates (Lab Work)

- Multiple PDBs soldered and assembled
- Located the small XT60 → XT30 PDBs (green boards)
- Continued progress on wiring organization and power distribution setup
- Waiting for remaining fuses to arrive
- Waiting for 24V → 12V DC-DC converter
- T12 team has been helping significantly with the project

---

### May 22 — Sprint 2 Progress Report

**Completed Work**
- Learned how to use the encoder in VESC Tool and integrated it with PyVESC to control all motors through Python
- Soldered all PDBs and wires
- Set up OAK-D Pro to run with Python
- Completed a test drive
- Created a web documentation site covering the full JeepBot setup guide (VESC, Encoder, F710 Controller & Raspberry Pi)

**Lessons Learned**
- Configured encoder + motor to work as a servo
- Camera setup process
- Controlling 2 VESCs for driving and steering via PyVESC
- Used DonkeyCar as a reference for JeepBot implementation

**Challenges**
- OAK-D Pro camera gray screen issue encountered during setup
- Anti-spark troubleshooting required before finding a working configuration
- JeepBot currently controls correctly via controller but loses control when camera preview is open

**Components Needed**
- *Urgent:*
  - Long USB to Micro USB cable ×1 (to connect front VESC to Raspberry Pi)
  - Long USB to USB-C cable ×2 (to connect front camera data and power to Pi and hub)
- *For future:*
  - 10A Mini Blade Fuse
  - Fuse holder

---

## 3. Current Status

**Mechanical Mounts**
- First iteration completed and evaluated
- Waiting on updated designs from MAP team
- Electrical components not yet permanently mounted

**Wiring**
- All PDBs soldered and assembled
- Wiring cleanup in progress — goal is safe passenger boarding
- Anti-spark working after troubleshooting

**Software / Controls**
- VESC encoder integrated with PyVESC
- Motor control through Python operational
- OAK-D Pro camera set up with Python; gray screen issue under investigation
- Controller-based driving functional; camera preview causes loss of control (active issue)

**Documentation**
- Version 2 structure created and being actively updated
- Web documentation site live with full setup guide
- Schematics and wiring documentation updated

**System Architecture**
- Finalized around 2 VESC setup (drive + steering)
- Updated to 4 PDB power distribution layout

---

## 4. Next Steps

**Wiring & Hardware**
- Clean up all wiring for safe passenger boarding
- Mount all electrical components permanently
- Acquire urgent cables (USB to Micro USB ×1, USB to USB-C ×2)
- Acquire 10A Mini Blade Fuses and fuse holder

**Software & Perception**
- Set up object detection
- Implement obstacle detection and automatic stopping
- Resolve OAK-D Pro camera preview conflict with motor control

**Navigation (Planned)**
- GPS integration and waypoint planning (Week 1–2)
- Heading and motion controller (Week 2)
- OAK-D depth stream setup (Week 1)
- Obstacle detection and avoidance (Week 2)

**Integration & Testing (Planned)**
- System fusion and route definition (Week 3, May 23 – Jun 1)
- Outdoor test runs and tuning (Week 4, Jun 1–5)
- Final demo (Jun 5–7)

**Documentation**
- Continue updating GitHub (version2)
- Upload additional progress photos to GitHub (version2/media)

---

## 5. Key Challenges
*(Continuously updated)*

- OAK-D Pro camera gray screen issue
- JeepBot loses motor control when camera preview is active
- Wiring still needs cleanup and permanent mounting
- Missing urgent cables (USB to Micro USB, USB to USB-C)

---

## 6. Notes
*(Continuously updated)*

- Major issues and milestones should be recorded
- Continue documenting implementation progress with photos
- Web documentation site available — link accessible via QR code in Sprint 2 slides
- DonkeyCar used as implementation reference for PyVESC integration

