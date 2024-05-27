# code to check if gpio pin in working, pin 14

from gpiozero import Button # type: ignore

button = Button(14, hold_time=0.3, bounce_time=0.05)  # Use the GPIO pin number where your button is connected, and set hold time

button.wait_for_press()

print("Button pressed!")

