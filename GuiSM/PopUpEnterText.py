# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

from EngineSM.WordSM import WordSM


class PopUpEnterText(tk.Toplevel):
    '''Classe représentant la pop-up qui permet de changer les données.'''

    lastAnswer = ""
    tr: ttk.Treeview = None
    itm: str = None

    def __init__(self, master, title="Modification"):
        tk.Toplevel.__init__(self, master)
        self.title(title)
        self.entry = tk.Entry(self, width=25)
        self.btn = tk.Button(self, text="Ok", command=self.exit)
        self.protocol("WM_DELETE_WINDOW", self.closure)
        self.entry.bind("<KeyPress-Return>", self.exit)
        self.withdraw()

    def exit(self, event=None):
        self.lastAnswer = self.entry.get()
        if self.column == "carac":
            self.tr.set(self.itm, 'carac', self.lastAnswer)
        elif self.column == "tags":
            self.tr.set(self.itm, 'tags', self.lastAnswer)

        self.tr.item(self.itm, tags="modified")

        #if self.master.ctrlFrame1.ctrlTypeDisplay.get() == 0: #si l'on est en mode obj:
        for row in self.master.treeRows:
            if row.id == self.itm:
                if self.column == "carac":
                    row.obj.struct = self.lastAnswer
                elif self.column == "tags":
                    row.obj.tags = self.lastAnswer

        self.withdraw()
    pass

    def closure(self):
        self.withdraw()
    pass

    def start(self, tree: ttk.Treeview, event, itm: str, text: str=""):
        self.tr = tree
        self.itm = itm
        self.wm_deiconify()
        self.lastAnswer = ""
        self.entry.delete(0, "end")

        self.column = self.tr.column(self.tr.identify_column(event[0].x), "id")
        if self.column == "carac":
            self.entry.insert("end", self.tr.item(self.itm, "values")[2])
        elif self.column == "tags":
            self.entry.insert("end", self.tr.item(self.itm, "values")[3])


        #self.entry.insert("end", "bla")#self.tr.identify_element(event.x, event.y))
        
        self.entry.pack()
        self.btn.pack()
        self.entry.focus_set()
        self.mainloop()

pass