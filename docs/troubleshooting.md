## Troubleshooting

This section provides troubleshooting guidelines based on the current system state. The system is still under development, so additional issues and solutions will be added over time.

---

## 1. Robot Not Moving

**Possible causes:**

- Raspberry Pi not integrated with VESC network  
- CAN communication not implemented  
- RC receiver not fully connected  
- Control software not running  
- Power not properly distributed  

**What to check:**

- Verify Raspberry Pi is powered and accessible  
- Confirm CAN wiring is connected to CAN HAT  
- Check that VESCs are powered  
- Verify RC controller and receiver are connected  
- Confirm control software is running  

---

## 2. No Power or Inconsistent Power

**Possible causes:**

- Antispark switch failure  
- Battery not properly connected  
- Damaged or missing PDB fuse  
- Loose XT connectors or wiring  
- 5V DC-DC not connected to Raspberry Pi  

**What to check:**

- Confirm battery connection  
- Inspect antispark behavior  
- Check PDB fuse status (especially LiDAR line)  
- Verify XT connectors and wiring  
- Confirm 5V output to Raspberry Pi and USB hub  

---

## 3. Cannot Connect to Raspberry Pi

**Possible causes:**

- Raspberry Pi not powered  
- Network configuration issues  
- Pi not properly set up after reflash  

**What to check:**

- Verify power to Raspberry Pi  
- Confirm network connection  
- Check SSH / NoMachine settings  
- Ensure Pi has completed boot  

---

## 4. Sensors Not Working

**Possible causes:**

- Sensors not connected to USB hub  
- USB cables too short or disconnected  
- LiDAR not powered  
- GPS not installed  

**What to check:**

- Verify camera connections  
- Check USB cables  
- Confirm LiDAR power  
- Verify USB hub power  
- Confirm GPS availability  

---

## 5. Steering Not Working

**Possible causes:**

- Steering encoder not connected  
- Encoder not compatible with VESC  
- No feedback signal  

**What to check:**

- Verify encoder wiring  
- Confirm compatibility  
- Check encoder connection  
- Validate steering VESC configuration  

---

## 6. CAN Communication Issues

**Possible causes:**

- CAN not connected to Raspberry Pi  
- Loose connections  
- Incorrect wiring (CAN High / Low)  
- CAN working only between VESCs  

**What to check:**

- Verify CAN wiring  
- Connect to CAN HAT  
- Confirm polarity (yellow = CAN High, green = CAN Low)  
- Check terminals and connections  

---

## 7. Safety Issues

If any of the following occur:

- Unexpected movement  
- Overheating  
- Unusual noise  
- Sparks or instability  

**Action:**

- Immediately disconnect battery  
- Do not rely on antispark switch  
- Emergency stop may not be connected  

---

## 8. Notes

- This guide reflects an incomplete system  
- Issues may change as development continues  
- More solutions will be added over time  
