from gpiozero import Button
from time import sleep

hook = Button(17, pull_up=False, bounce_time=0.05)

try:
    while True:
        print("Décroché" if not hook.is_pressed else "Raccroché")
        sleep(0.2)
finally:
    hook.close()