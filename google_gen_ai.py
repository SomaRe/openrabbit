# google_gen_ai.py
import google.generativeai as genai
import textwrap
from PySide6.QtCore import QObject, Signal
from SECRET import GEMINI_API

class GoogleGenAI(QObject):
    response_received = Signal(str, str)  # Signal to send response text and role back to the main thread

    def __init__(self, api_key):
        super().__init__()
        genai.configure(api_key=GEMINI_API)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

    def to_markdown(self, text):
        text = text.replace('•', '  *')
        return textwrap.indent(text, '> ', predicate=lambda _: True)

    def send_message(self, message, stream=True):
        response = self.chat.send_message(message, stream=stream)
        for chunk in response:
            self.response_received.emit('Assistant', chunk)

