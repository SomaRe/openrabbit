# button_handler.py

from PySide6.QtCore import Signal, QObject  # type: ignore
from gpiozero import Button # type: ignore

# Set up the GPIO button
button = Button(14, hold_time=0.3, bounce_time=0.05)  # Use the GPIO pin number where your button is connected, and set hold time

class ButtonHandler(QObject):
    button_pressed_signal = Signal()
    button_released_signal = Signal()
    button_held_signal = Signal()

    def __init__(self):
        super().__init__()
        button.when_pressed = self.emit_button_pressed_signal
        button.when_released = self.emit_button_released_signal
        button.when_held = self.emit_button_held_signal

    def emit_button_pressed_signal(self):
        self.button_pressed_signal.emit()

    def emit_button_released_signal(self):
        self.button_released_signal.emit()

    def emit_button_held_signal(self):
        self.button_held_signal.emit()
