import os
import time
from dataclasses import dataclass

# -----------------------------------------------------------------------
# Same headless guard as pygame_f710.py: force SDL to dummy video/audio
# BEFORE importing pygame, so pygame.event.pump() never blocks on a
# display while the OAK-D cameras are busy on USB.
# -----------------------------------------------------------------------
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


@dataclass
class ControllerState:
    axes: list[float]
    buttons: list[int]

    def pressed(self, button_id: int) -> bool:
        return button_id < len(self.buttons) and self.buttons[button_id] == 1


class RadioMasterInput:
    """
    Reads the RadioMaster TX through the Arduino Leonardo, which presents the
    SBUS channels as a standard USB HID joystick.

    Exposes the EXACT same interface as F710DirectInput
    (.joystick_id, .name, .read() -> state with .axes / .buttons / .pressed),
    so jeepbot_drive.py treats both controllers identically. The only real
    difference is device selection: the Leonardo may not enumerate as
    joystick 0 if another HID device is attached, so we match by name and
    fall back to index 0 if no match is found.
    """

    def __init__(self, joystick_id=None, name_match="Arduino"):
        pygame.display.init()   # needed even in dummy mode for the event pump
        pygame.joystick.init()

        # Wait up to 3 s for the joystick to enumerate (USB can be slow on Pi)
        deadline = time.time() + 3.0
        while pygame.joystick.get_count() == 0 and time.time() < deadline:
            time.sleep(0.1)

        count = pygame.joystick.get_count()
        if count == 0:
            raise RuntimeError(
                "No joystick found. Connect the RadioMaster RX + Arduino Leonardo."
            )

        # Explicit id wins; otherwise pick by name; otherwise fall back to 0.
        if joystick_id is not None:
            self.joystick_id = joystick_id
        else:
            self.joystick_id = self._find_by_name(count, name_match)

        self.joy = pygame.joystick.Joystick(self.joystick_id)
        self.joy.init()
        self.name = self.joy.get_name()

    @staticmethod
    def _find_by_name(count, name_match):
        if name_match:
            needle = name_match.lower()
            for i in range(count):
                j = pygame.joystick.Joystick(i)
                j.init()
                if needle in j.get_name().lower():
                    return i
        return 0

    def read(self) -> ControllerState:
        # Safe with SDL_VIDEODRIVER=dummy — returns instantly, never blocks.
        pygame.event.pump()

        axes    = [self.joy.get_axis(i)   for i in range(self.joy.get_numaxes())]
        buttons = [self.joy.get_button(i) for i in range(self.joy.get_numbuttons())]

        return ControllerState(axes=axes, buttons=buttons)
