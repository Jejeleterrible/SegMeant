# -*- coding: utf-8 -*-

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

from EngineSM.TextObjSM import TextObjSM

class TreeSM(ttk.Treeview):

    def __init__(self, master):
        ttk.Treeview.__init__(self, master, columns=('objet', 'type', 'carac', 'tags'))

        self.createWidgets()
    pass

    def createWidgets(self):
        self.column("#0", width="150", minwidth="90", stretch=tk.YES)
        self.heading("objet", text='Objet')
        self.heading("type", text='Type')
        self.heading("carac", text='Caractéristiques')
        self.heading("tags", text="Tags")
        self.bind("<<TreeviewSelect>>", self.master.master.treeSelected)

        self.treeScroll = ttk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.yview)
        self.configure(yscrollcommand=self.treeScroll.set)

        self.tag_configure("sep", foreground="red")
        self.tag_configure("mot", foreground="green")
        self.tag_configure("prop", foreground="darkblue")
        self.tag_configure("modified", foreground="blue")

        self.phraseTreeFont = tkFont.Font()
        self.phraseTreeFont.configure(weight=tkFont.BOLD, size=10)
        self.tag_configure("phrase", font=self.phraseTreeFont)

        self.propTreeFont = tkFont.Font()
        self.propTreeFont.configure(slant="italic", size=10)
        self.tag_configure("prop", font=self.propTreeFont)

        self.modTreeFont = tkFont.Font()
        self.modTreeFont.configure(slant="italic", size=10, weight=tkFont.BOLD)
        self.tag_configure("modified", font=self.modTreeFont)

        self.bind("<Double-1>", lambda e : self.master.master.processPool.submit(self.onDoubleClick, (e,)))
        
    pass

    def onDoubleClick(self, event):
        self.master.master.popupText.start(self, event, self.focus())#self.item(self.focus(), "values")[2])
        #self.item(self.focus(), values=(self.item(self.focus(), "values")[0], self.item(self.focus(), "values")[1], ))
        #foc = self.focus()
        #self.master.master.processPool.submit(self.set, (foc, 'carac', self.master.master.popupText.lastAnswer))
        #self.master.master.processPool.submit(print, (self.item(foc, "values")))
        #self.set(self.focus(), 'carac', self.master.master.popupText.lastAnswer)
        '''item = self.item(self.focus())
        vl = self.item(item, "values")
        self.item(item, values=(vl[0], vl[1], ))
        item.values[2] = self.master.master.popupText.lastAnswer'''
        #self.item(foc).update()
        #print(self.item(foc, "values"))
        #self.update()
        #self.delete()
        #self.add
        
    pass

pass

@dataclass
class TreeRow:
    id: str
    obj: TextObjSM
    parent: str = ""
    ind: int = 0
pass