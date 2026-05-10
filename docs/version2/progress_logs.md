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

## 3. Current Status

**Mechanical Mounts**
- First iteration completed and evaluated
- Waiting on updated designs from MAP team

**Wiring**
- Significant work still required
- Initial connections made (XT60, MR60F)
- Front and rear PDB architecture updated

**Documentation**
- Version 2 structure created and being actively updated
- Schematics and wiring documentation updated

**System Architecture**
- Finalized around 2 VESC setup (drive + steering)
- Updated to 4 PDB power distribution layout

---

## 4. Next Steps

- Receive and evaluate next iteration of mechanical mounts once available

**Continue Wiring Implementation**
- Prepare and test wiring components
- Finalize front XT90 → XT60 PDB
- Build XT60 → XT30 PDBs for DC-DC converters
- Verify EMO integration and relay implementation

**Acquire Remaining Components**
- XT90 connector
- Relay/current-handling component for EMO
- Remaining PDB/DC-DC related parts

**Documentation**
- Upload additional progress photos to GitHub (version2/media)
- Continue updating documentation in version2
- Integrate updated schematics into implementation
- Prepare progress updates for presentation

---

## 5. Key Challenges
*(Continuously updated)*

- Wiring implementation and power distribution complexity
- Missing XT90 and relay/current-handling components
- EMO integration still undefined

---

## 6. Notes
*(Continuously updated)*

- Major issues and milestones should be recorded
- Continue documenting implementation progress with photos


