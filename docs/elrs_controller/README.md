# JeepBot ELRS Controller

Turn a RadioMaster **ExpressLRS** radio into a plug-and-play **USB joystick** for
DonkeyCar. An Arduino Leonardo reads the ELRS receiver's serial stream, filters and
decodes every stick / switch / button, and re-presents the whole thing to a Raspberry
Pi as a standard USB HID game controller at `/dev/input/js0`.

```
RadioMaster TX  ──2.4GHz──▶  RP4TD RX  ──serial @115200──▶  Arduino Leonardo  ──USB HID──▶  Raspberry Pi / DonkeyCar
```

## 📖 Setup guide

**Full step-by-step documentation:**
👉 **https://<your-username>.github.io/JeepBot-ELRS-Controller/**

It covers flashing the transmitter and receiver (ELRS Configurator v4.0.1, binding
phrase `JEEPBOT`), wiring the receiver to the Leonardo, building the firmware, the
DonkeyCar integration, the full channel map, and troubleshooting.

## Quick start

```bash
git clone https://github.com/<your-username>/JeepBot-ELRS-Controller.git
cd JeepBot-ELRS-Controller

pio run                      # build for the Arduino Leonardo
pio run --target upload      # flash it (board connected over USB)
```

All required libraries (`Joystick`, `FUTABA_SBUS`, `Streaming`) are vendored in
`lib/`, so there is nothing else to install beyond [PlatformIO](https://platformio.org/).

## Repo layout

| Path | What it is |
|------|------------|
| `src/main.cpp` | Firmware: SBUS → filtered USB-HID joystick |
| `src/utils/` | Rolling-average `SBusTracker` helper |
| `lib/` | Bundled Arduino libraries (Joystick, FUTABA_SBUS, Streaming) |
| `donkeycar_joystick/my_joystick.py` | DonkeyCar controller part that maps the joystick to driving actions |
| `platformio.ini` | Build config (targets `leonardo`) |
| `docs/` | The setup-guide website (served by GitHub Pages) |

## Debug logging

Serial output is **off by default**, because on the Leonardo the debug Serial can
conflict with the USB-HID interface. To watch raw channel values while testing,
enable the build flag — then turn it back off for normal use:

```ini
[env:leonardo]
build_flags = -DDEBUG_LOG
```

## Hardware

- RadioMaster Pocket (internal 2.4 GHz, EdgeTX) — transmitter
- RadioMaster RP4TD True-Diversity 2.4 GHz — receiver
- Arduino Leonardo (ATmega32U4; USB-HID capable — an Uno will **not** work)
- Raspberry Pi running DonkeyCar
