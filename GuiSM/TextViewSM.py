# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

class TextViewSM(tk.Text):

    def __init__(self, master):
        tk.Text.__init__(self, master)
        self.indexWord = 0
        self.createWidgets()
    pass

    def createWidgets(self):
        self.textScroll = ttk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.yview)
        self.configure(yscrollcommand=self.textScroll.set)

        
        self.tag_add('proposition', 1.0, 1.0)
        self.tag_add('phrase', 1.0, 1.0)
        self.tag_add('mot', 1.0, 1.0)

        self.tag_config("mot", foreground="dark green")
        self.tag_config("mot", font="underlinedbold")
        self.tag_config("proposition", background="khaki")

        self.motFont = tkFont.Font(self, self.cget('font'))
        self.motFont.configure(underline=True, weight=tkFont.BOLD)
        self.tag_config("mot", font=self.motFont)

        self.phraseFont = tkFont.Font(self, self.cget('font'))
        self.phraseFont.configure(underline=True)
        self.tag_config("phrase", font=self.phraseFont)

        self.configure(wrap="word", state=tk.DISABLED)
    pass

pass