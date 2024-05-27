import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QStackedWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer, Signal, Slot, QObject, Qt, QThread, QMetaObject
from gpiozero import Button
from googleSTT import SpeechToText
from datetime import datetime

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

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.stacked_widget = QStackedWidget()

        self.home_screen = HomeScreen()
        self.chat_screen = ChatScreen()

        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.chat_screen)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing
        self.setLayout(layout)

        self.setWindowTitle("GPIO Button Example")
        self.setFixedSize(480, 640)

        self.button_handler = ButtonHandler()
        self.button_handler.button_pressed_signal.connect(self.handle_button_press)
        self.button_handler.button_released_signal.connect(self.handle_button_release)
        self.button_handler.button_held_signal.connect(self.handle_button_held)

        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.single_click_detected)

        self.double_click_time = 300  # Time window to detect a double click in milliseconds
        self.click_count = 0

        self.long_press_active = False

    @Slot()
    def handle_button_press(self):
        self.click_count += 1
        if not self.long_press_active:
            if self.click_count == 1:
                self.click_timer.start(self.double_click_time)
            elif self.click_count == 2:
                self.double_click_detected()

    @Slot()
    def handle_button_release(self):
        if self.long_press_active:
            self.long_press_active = False
            self.chat_screen.stop_speech_recognition()

    @Slot()
    def handle_button_held(self):
        self.long_press_active = True
        self.click_timer.stop()
        self.stacked_widget.setCurrentWidget(self.chat_screen)
        QMetaObject.invokeMethod(self.chat_screen, "start_speech_recognition", Qt.QueuedConnection)

    @Slot()
    def single_click_detected(self):
        if not self.long_press_active:
            if self.click_count == 1 and self.stacked_widget.currentWidget() == self.chat_screen:
                self.stacked_widget.setCurrentWidget(self.home_screen)
        self.click_count = 0

    @Slot()
    def double_click_detected(self):
        self.click_timer.stop()
        self.click_count = 0

class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.current_time = QLabel(datetime.now().strftime("%I:%M %p"))
        self.current_time.setAlignment(Qt.AlignCenter)
        self.image_label = QLabel()
        self.image_awake = QPixmap("main_screen_img_awake.png").scaledToWidth(240, Qt.SmoothTransformation)  # Scale to half the original size
        self.image_sleep = QPixmap("main_screen_img_sleep.png").scaledToWidth(240, Qt.SmoothTransformation)  # Scale to half the original size
        self.image_label.setPixmap(self.image_sleep)
        self.image_label.setAlignment(Qt.AlignCenter)  # Center the image

        layout = QVBoxLayout()
        layout.addWidget(self.current_time)
        layout.addWidget(self.image_label)
        layout.setAlignment(Qt.AlignCenter)  # Center the contents vertically
        self.setLayout(layout)

        # Set dark mode styles
        self.setStyleSheet("background-color: black; color: white;")
        self.current_time.setStyleSheet("color: white; font-size: 48px;")

class ChatScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Chat Session")
        self.transcription_label = QLabel("Transcription will appear here")
        self.transcription_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.transcription_label)
        layout.setAlignment(Qt.AlignCenter)  # Center the contents vertically
        self.setLayout(layout)

        # Set dark mode styles
        self.setStyleSheet("background-color: black; color: white;")
        self.label.setStyleSheet("color: white; font-size: 24px;")
        self.transcription_label.setStyleSheet("color: white; font-size: 18px;")

        self.speech_to_text = SpeechToText(self.update_transcription)

    @Slot()
    def start_speech_recognition(self):
        self.speech_to_text.start_listening()

    @Slot()
    def stop_speech_recognition(self):
        self.speech_to_text.stop_listening()

    def update_transcription(self, text):
        self.transcription_label.setText(f"Transcription: {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
