# Software

## Architecture

The system is structured around a central processing node (Raspberry Pi) and modular subsystems.

## Main Components

- Camera module:
  - Depth sensing
  - RGB capture
  - Dual OAK-D support

## Execution

Entry point:
src/main.py

Modules:
- camera/
- tests/

## Responsibilities

- Raspberry Pi:
  - Sensor processing
  - Decision making

- Arduino:
  - Emergency stop logic
  - Relay control
