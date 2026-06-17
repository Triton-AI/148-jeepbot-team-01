import pygame
import time

pygame.init()
pygame.joystick.init()

joy = pygame.joystick.Joystick(0)
joy.init()

print("Joystick:", joy.get_name())

while True:
    pygame.event.pump()

    axes = [round(joy.get_axis(i), 3) for i in range(joy.get_numaxes())]
    buttons = [joy.get_button(i) for i in range(joy.get_numbuttons())]

    print(f"\rAxes: {axes}  Buttons: {buttons}", end="")
    time.sleep(0.05)
