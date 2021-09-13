from speech.SpeechProcessor import SpeechProcessor
from interface.BuyInterface import BuyInterface
from commands.CommandController import CommandController

from tkinter import ttk
import tkinter as tk
from tkinter import *

import yaml
import os

sp = SpeechProcessor(hotword=False, keywords_paths=["speech/csgo_hotword.ppn"])
buy = BuyInterface("T")
cc = CommandController(buy)


#
# while True:
#     try:
#         # output = sp.listen()
#         output = "Let's go"
#         matches = cc.find_match(output)
#         if len(matches) == 0:
#             print("Unknown command.")
#         else:
#             print("Commands matched:", matches)
#             cc.run(matches[0])
#
#         break
#
#     except KeyboardInterrupt:
#         sp.terminate()
#         break
#


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

        label = Label(self, text="Yo what's up from the Console")
        label.pack()


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
        vi = 0
        for r in ((self.ctRadio, self.ctFrame, "CT"), (self.tRadio, self.tFrame, "T")):
            Label(r[1], text=r[2] + " Loadout").grid(column=0, columnspan=3)
            for i, c in enumerate(r[0], 1):
                frame = Frame(r[1], borderwidth=1, relief="groove")
                frame.grid(column=1)

                selected = int(self.selected[r[2]][c[0] + "/" + c[1]])
                self.radioVars.append(IntVar(r[1], selected))
                Radiobutton(r[1], text=c[0], padx=10, variable=self.radioVars[vi], value=0).grid(row=i, column=1,
                                                                                                 sticky="w")
                Radiobutton(r[1], text=c[1], padx=10, variable=self.radioVars[vi], value=1).grid(row=i, column=2,
                                                                                                 sticky="w")
                vi += 1

            r[1].grid_rowconfigure(len(r[0]) + 1, minsize=20)

        # Checkboxes
        vi = 0
        row = max(len(self.ctRadio), len(self.tRadio)) + 1
        for c in ((self.ctCheck, self.ctFrame, "CT"), (self.tCheck, self.tFrame, "T")):
            for i, s in enumerate(c[0], 1):
                frame = Frame(c[1], borderwidth=1, relief="groove")
                frame.grid(column=1)

                selected = bool(self.selected[c[2]][s])
                self.checkVars.append(BooleanVar(c[1], selected))
                Checkbutton(c[1], text=s, padx=10, variable=self.checkVars[vi]).grid(row=row + i, column=1,
                                                                                     columnspan=2, sticky="ws")
                vi += 1

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
