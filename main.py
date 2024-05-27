import sys
from PySide6.QtCore import Slot, QMetaObject, Qt, QUrl, QTimer, QObject
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from button_handler import ButtonHandler

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.engine.load(QUrl("main.qml"))
        if not self.engine.rootObjects():
            sys.exit(-1)
        self.root_object = self.engine.rootObjects()[0]
        self.main_rect = self.root_object.findChild(QObject, "mainRect")

        self.button_handler = ButtonHandler()
        self.button_handler.button_pressed_signal.connect(self.handle_button_press)
        self.button_handler.button_released_signal.connect(self.handle_button_release)
        self.button_handler.button_held_signal.connect(self.handle_button_held)

        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.single_click_detected)

        self.double_click_time = 500  # Time window to detect a double click in milliseconds
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
            print("Long press released")

    @Slot()
    def handle_button_held(self):
        self.long_press_active = True
        print("Button held")
        QMetaObject.invokeMethod(self.main_rect, "buttonHeld", Qt.QueuedConnection)

    @Slot()
    def single_click_detected(self):
        if not self.long_press_active:
            if self.click_count == 1:
                print("Single click detected")
        self.click_count = 0

    @Slot()
    def double_click_detected(self):
        print("Double click detected")
        self.click_timer.stop()
        self.click_count = 0

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = MainApp()
    app.run()