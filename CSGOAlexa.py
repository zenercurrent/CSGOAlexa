from speech.SpeechProcessor import SpeechProcessor
from interface.BuyInterface import BuyInterface
from commands.CommandController import CommandController

from tkinter import ttk
import tkinter as tk
from tkinter import *

from threading import Thread
import keyboard
import yaml
import os

sp = SpeechProcessor(hotword=False, keywords_paths=["speech/csgo_hotword.ppn"])
buy = BuyInterface("T")
cc = CommandController(buy)


class GUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.resizable(False, False)

        self.nb = ttk.Notebook(self.master)
        self.nb.pack(fill=BOTH, expand=1)

        for F in (Console, Config):
            frame = F(self.nb, self)
            self.nb.add(frame, text=frame.name)
            frame.tkraise()


class Console(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.name = "Console"

        self.modeFrame = Frame(self, borderwidth=3, pady=10, relief="groove")
        self.modeFrame.pack(pady=10, anchor="center")
        self.modeVar = None

        self.setup()

        self.startButton = Button(self, text="Start", pady=5, width=20, command=self.start)
        self.startButton.pack()
        self.RUNNING_FLAG = False
        self.background_thread = None

    def setup(self):
        self.modeVar = IntVar(self.modeFrame, 0)
        for i, m in enumerate(("Keyboard Hotkey", "Hotkey Voice", "Hotword Voice (Experimental)")):
            Radiobutton(self.modeFrame, text=m, padx=10, pady=10, variable=self.modeVar, value=i).pack(side=LEFT)

    def start(self):
        self.RUNNING_FLAG = not self.RUNNING_FLAG
        self.startButton["text"] = "Stop" if self.RUNNING_FLAG else "Start"
        if not self.RUNNING_FLAG:
            print("Stopping Thread")
            self.background_thread.RUNNING_FLAG = False
            return

        mode = self.modeVar.get()
        assert 0 <= mode < 3
        if mode == 0:
            pass
        elif mode == 1 or mode == 2:
            sp.HOTWORD_FLAG = mode == 2

            self.background_thread = self.BackgroundThread(mode)
            self.background_thread.start()

    class BackgroundThread(Thread):
        def __init__(self, mode):
            super().__init__()
            self.mode = mode
            self.RUNNING_FLAG = False

        def run(self):
            assert 0 <= self.mode < 3
            self.RUNNING_FLAG = True
            while True:
                if not self.RUNNING_FLAG:
                    break
                if self.mode == 1:
                    keyboard.wait("=")
                output = sp.listen()
                matches = cc.find_match(output)
                if len(matches) > 0:
                    cc.run(matches[0])


class Config(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.name = "Config"

        self.ctRadio = (
            ("USP-S", "P2000"), ("Five-Seven", "CZ75-Auto"), ("Desert Eagle", "R8 Revolver"), ("MP7", "MP5-SD"),
            ("M4A1-S", "M4A4"))
        self.tRadio = (("Tec-9", "CZ75-Auto"), ("Desert Eagle", "R8 Revolver"), ("MP7", "MP5-SD"))
        self.radioVars = []
        self.ctCheck = ("Always Armour", "Always Defuse Kit", "Always Zeus", "Auto Buy Options")
        self.tCheck = ("Always Armour", "Always Zeus", "Auto Buy Options")
        self.checkVars = []
        self.selected = self.retrieve_from_file()

        self.ctFrame = Frame(self, borderwidth=3, relief="groove")
        self.tFrame = Frame(self, borderwidth=3, relief="groove")
        self.submit = Button(self, text="Apply Changes", command=self.apply_changes)

        self.setup()

        self.ctFrame.grid(row=0, column=0, padx=20, pady=10, sticky="news")
        self.tFrame.grid(row=0, column=1, padx=20, pady=10, sticky="news")
        self.submit.grid(row=1, column=0, columnspan=2, pady=10)

    def setup(self):
        # Radio buttons
        for r in ((self.ctRadio, self.ctFrame, "CT"), (self.tRadio, self.tFrame, "T")):
            Label(r[1], text=r[2] + " Loadout").grid(column=0, columnspan=3)
            for i, c in enumerate(r[0], 1):
                frame = Frame(r[1], borderwidth=1, relief="groove")
                frame.grid(column=1)

                selected = int(self.selected[r[2]][c[0] + "/" + c[1]])
                var = IntVar(r[1], selected)
                self.radioVars.append(var)
                Radiobutton(r[1], text=c[0], padx=10, variable=var, value=0).grid(row=i, column=1,
                                                                                  sticky="w")
                Radiobutton(r[1], text=c[1], padx=10, variable=var, value=1).grid(row=i, column=2,
                                                                                  sticky="w")

            r[1].grid_rowconfigure(len(r[0]) + 1, minsize=20)

        # Checkboxes
        row = max(len(self.ctRadio), len(self.tRadio)) + 1
        for c in ((self.ctCheck, self.ctFrame, "CT"), (self.tCheck, self.tFrame, "T")):
            for i, s in enumerate(c[0], 1):
                frame = Frame(c[1], borderwidth=1, relief="groove")
                frame.grid(column=1)

                selected = bool(self.selected[c[2]][s])
                var = BooleanVar(c[1], selected)
                self.checkVars.append(var)
                Checkbutton(c[1], text=s, padx=10, variable=var).grid(row=row + i, column=1,
                                                                      columnspan=2, sticky="ws")

    def apply_changes(self):
        ct = []
        t = []
        for i, r in enumerate(self.radioVars):
            if i > len(self.ctRadio) - 1:
                t.append(r.get())
            else:
                ct.append(r.get())
        for i, c in enumerate(self.checkVars):
            if i > len(self.ctCheck) - 1:
                t.append(c.get())
            else:
                ct.append(c.get())
        self.save_to_file(ct, t)

    def retrieve_from_file(self):
        if not os.path.exists("config.yaml"):
            self.save_to_file(list("00000") + [False] * 4, list("000") + [False] * 3)  # default parse
            self.retrieve_from_file()

        with open("config.yaml", "r") as file:
            data = yaml.safe_load(file)
            return data

    def save_to_file(self, ct, t):
        data = {"CT": {}, "T": {}}
        [data["CT"].update({c[0] + "/" + c[1]: ct[i]}) for i, c in enumerate(self.ctRadio)]
        [data["T"].update({c[0] + "/" + c[1]: t[i]}) for i, c in enumerate(self.tRadio)]
        [data["CT"].update({c: ct[len(self.ctRadio) + i]}) for i, c in enumerate(self.ctCheck)]
        [data["T"].update({c: t[len(self.tRadio) + i]}) for i, c in enumerate(self.tCheck)]

        with open("config.yaml", "w") as file:
            yaml.dump(data, file)


gui = GUI()
gui.mainloop()
