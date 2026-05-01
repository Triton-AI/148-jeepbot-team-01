
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

Completed Work
- Final laser cuts for electronics mounting plates completed
- First iteration of mechanical mounts 3D printed
- Feedback provided to MAP mechanical team for improvements
- GitHub repository reorganized:
  - Version 1 (past work)
  - Version 2 (current + ongoing work)
- Initial system documentation created (overview, hardware, software, etc.)
- Schematics updated based on recent discussions
---

## 3. Current Status

- Mechanical mounts:
  - First iteration completed and evaluated
  - Waiting on updated designs from MAP team
- Wiring:
  - Significant work still required
  - Initial connections made (XT60, MR60F)
- Documentation:
  - Version 2 structure created and being actively updated
- System architecture:
  - Finalized around 2 VESC setup (drive + steering) 

---

## 4. Next Steps

- Receive and evaluate next iteration of mechanical mounts once available
- Continue wiring implementation:
- Prepare and test wiring components:
  - Create 2 wires (30 cm each) with MR60 male connectors
  - Understand their purpose and confirm design with Jack
- Purchase additional wiring materials:
  - 12 AWG black wire
  - Potentially 12 AWG red wire depending on system needs
- Confirm wiring quality with professor:
  - Verify if XT60 connection is acceptable using 12 GA wire (previously noted as 12AWG)
- Clarify remaining system requirements:
  - Ask what additional components or wiring steps are still needed
- Upload progress photos to GitHub (version2/media)
- Continue updating documentation in version2
- Integrate updated schematics into implementation
- Prepare progress updates for presentation

---

## 5. Key Challenges
*(Continuously updated)*

- To be updated as issues are identified  

---

## 6. Notes
*(Continuously updated)*

- Major issues and milestones should be recorded  



