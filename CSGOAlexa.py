from speech.SpeechProcessor import SpeechProcessor
from interface.BuyInterface import BuyInterface
from commands.CommandController import CommandController
import keyboard

sp = SpeechProcessor(hotword=False, keywords_paths=["speech/csgo_hotword.ppn"])
buy = BuyInterface("T")
cc = CommandController(buy)

while True:
    try:
        output = sp.listen()
        matches = cc.find_match(output)
        if len(matches) == 0:
            print("Unknown command.")
        else:
            print("Commands matched:", matches)
            cc.run(matches[0])

    except KeyboardInterrupt:
        sp.terminate()
        break
