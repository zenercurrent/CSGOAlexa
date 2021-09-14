import speech_recognition as sr
from playsound import playsound

from .HotwordListener import HotwordListener


class SpeechProcessor:

    def __init__(self, hotword=True, keywords_paths=None):
        self.recog = sr.Recognizer()
        self.mic = sr.Microphone()

        self.HOTWORD_FLAG = hotword
        self.hw_listener = None
        self.audio_stream = None
        self.frame_length = None

        if hotword or keywords_paths is None:
            raise ValueError("hotword and keywords_paths must not be None!")

        self.hw_listener = HotwordListener(keywords_paths)
        self.audio_stream = self.hw_listener.audio_stream
        self.frame_length = self.hw_listener.handle.frame_length

    def listen(self):
        if self.HOTWORD_FLAG:
            self.hw_listener.listen()

        playsound("speech/siri.mp3")
        with self.mic as source:
            try:
                print("Listening...")
                audio = self.recog.listen(source)
                output = self.recog.recognize_google(audio)
                print(output, "\n")
                return output

            except sr.UnknownValueError:
                print("Nothing was recognised.")
                return ""

    def terminate(self):
        self.hw_listener.terminate()
