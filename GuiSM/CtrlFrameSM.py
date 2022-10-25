# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

class CtrlFrameSM(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master, background="linen")

        self.createWidgets()
    pass

    def createWidgets(self):
        self.collapseBtn = tk.Button(self, text="C", command=self.master.collapse)
        self.collapseBtn.pack(side='top')
        self.openAllBtn = tk.Button(self, text="A", command=self.master.expandAll)
        self.openAllBtn.pack(side='top')
        self.openCurBtn = tk.Button(self, text="S", command=self.master.expandCurrent)
        self.openCurBtn.pack(side='top')

        self.ctrlTypeDisplay = tk.IntVar()
        self.radioObj = tk.Radiobutton(self, variable=self.ctrlTypeDisplay, value=0, text="Objets", command=self.master.mode)
        self.radioWrd = tk.Radiobutton(self, variable=self.ctrlTypeDisplay, value=1, text="Mots", command=self.master.mode)

        self.ctrlThreads = tk.BooleanVar()
        self.ctrlThreads.set(False)
        self.checkThreads = tk.Checkbutton(self, variable=self.ctrlThreads, text="Multithreadé")

        self.radioObj.pack(side='right')
        self.radioWrd.pack(side='right')
        self.checkThreads.pack(side='right')

        self.fileName = tk.Label(self, text="")
        self.fileName.pack(side='bottom', fill="x")

        self.importBtn = tk.Button(self, text="Import text", command=self.master.importTxt)
        self.importBtn.pack(side='bottom', fill="y")

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.pack(side='left')
    pass

pass