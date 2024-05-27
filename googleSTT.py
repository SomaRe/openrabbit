# googleSST.py

from PySide6.QtCore import QObject, Signal
import queue
import re
import sys
import threading
from google.cloud import speech
import pyaudio

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate=RATE, chunk=CHUNK):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True
        self._audio_interface = None
        self._audio_stream = None

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b"".join(data)

def listen_print_loop(responses, callback):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript
        overwrite_chars = " " * (num_chars_printed - len(transcript))
        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)
        else:
            print(transcript + overwrite_chars)
            callback(transcript)
            num_chars_printed = 0

class SpeechToText(QObject):
    transcription_signal = Signal(str)
    
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback
        self.language_code = "en-US"
        self.client = speech.SpeechClient()
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=self.language_code,
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config, interim_results=True
        )
        self.stream = None
        self.audio_generator = None
        self.requests = None
        self.responses = None
        self.listen_thread = None

    def start_listening(self):
        self.stream = MicrophoneStream(RATE, CHUNK)
        self.stream.__enter__()
        self.audio_generator = self.stream.generator()
        self.requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in self.audio_generator
        )
        self.responses = self.client.streaming_recognize(
            self.streaming_config, self.requests
        )
        self.listen_thread = threading.Thread(
            target=listen_print_loop, args=(self.responses, self.emit_transcription)
        )
        self.listen_thread.start()

    def stop_listening(self):
        if self.stream:
            self.stream.__exit__(None, None, None)
            if self.listen_thread:
                self.listen_thread.join()

    def emit_transcription(self, text):
        self.transcription_signal.emit(text)
        if self.callback:
            self.callback(text)
