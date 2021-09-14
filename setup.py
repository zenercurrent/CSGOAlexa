import sys
import os

import cx_Freeze
import tkinter

root = tkinter.Tk()
base = None

os.environ["TCL_LIBRARY"] = root.tk.exprstring('$tcl_library')
os.environ["TK_LIBRARY"] = root.tk.exprstring('$tk_library')

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("CSGOAlexa.py")]

cx_Freeze.setup(
    name="CSGO Alexa Binds",
    options={"build_exe": {"packages": ["tkinter"],
                           "include_files": ["interface", "speech", "commands", "config.yaml"]}},
    version="0.1",
    executables=executables)
