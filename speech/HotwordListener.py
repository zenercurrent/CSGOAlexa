import pvporcupine
import pyaudio
import struct


class HotwordListener:

    def __init__(self, keywords_paths):
        self.handle = pvporcupine.create(keyword_paths=keywords_paths)
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.handle.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.handle.frame_length
        )

    def listen(self):
        try:
            while True:
                pcm = self.audio_stream.read(self.handle.frame_length)
                pcm = struct.unpack_from("h" * self.handle.frame_length, pcm)

                result = self.handle.process(pcm)
                if result >= 0:
                    print("DETECTED!")

                    return

        except KeyboardInterrupt:
            print("Terminating Hotword Listener...")

    def terminate(self):
        if self.handle is not None:
            self.handle.delete()
        if self.pa is not None:
            self.pa.terminate()
        if self.audio_stream is not None:
            self.audio_stream.close()
