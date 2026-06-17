import os
import time
from dataclasses import dataclass

# -----------------------------------------------------------------------
# CRITICAL: set SDL to dummy video BEFORE importing pygame.
# Without this, pygame.init() tries to open a display/window.
# On a headless Pi that blocks or errors when other USB devices
# (like the OAK-D camera) are active — freezing pygame.event.pump().
# Setting SDL_VIDEODRIVER=dummy skips all display initialisation so
# pygame only handles joystick input, which is all we need.
# -----------------------------------------------------------------------
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


@dataclass
class F710State:
    axes: list[float]
    buttons: list[int]

    def pressed(self, button_id: int) -> bool:
        return button_id < len(self.buttons) and self.buttons[button_id] == 1


class F710DirectInput:
    def __init__(self, joystick_id=None):
        # Only init the subsystems we actually need
        pygame.display.init()   # needed even in dummy mode for event pump
        pygame.joystick.init()

        # Wait up to 3 s for the joystick to enumerate
        # (on Pi it can take a moment after USB detection)
        deadline = time.time() + 3.0
        while pygame.joystick.get_count() == 0 and time.time() < deadline:
            time.sleep(0.1)

        count = pygame.joystick.get_count()
        if count == 0:
            raise RuntimeError(
                "No joystick found. Connect F710 and set it to D mode."
            )

        self.joystick_id = 0 if joystick_id is None else joystick_id
        self.joy = pygame.joystick.Joystick(self.joystick_id)
        self.joy.init()
        self.name = self.joy.get_name()

    def read(self) -> F710State:
        # pump() is safe here — SDL_VIDEODRIVER=dummy means no display
        # blocking, so this always returns instantly
        pygame.event.pump()

        axes    = [self.joy.get_axis(i)   for i in range(self.joy.get_numaxes())]
        buttons = [self.joy.get_button(i) for i in range(self.joy.get_numbuttons())]

        return F710State(axes=axes, buttons=buttons)
