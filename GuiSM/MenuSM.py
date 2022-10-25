# -*- coding: utf-8 -*-

import tkinter as tk

class MenuSM(tk.Menu):
    def __init__(self, master):
        tk.Menu.__init__(self, master)
        self.createWidgets()
    pass

    def createWidgets(self):
        self.master.config(menu=self)

        self.filesMenu = tk.Menu(self, tearoff=0)
        self.filesMenu.add_command(command=self.master.importTxt, label="Importer", accelerator="Ctrl+O")
        self.filesMenu.add_command(command=self.master.saveData, label="Sauvegarder", accelerator="Ctrl+S")
        self.filesMenu.add_command(command=self.master.saveXML, label="Exporter en XML")
        self.filesMenu.add_command(command=self.master.loadData, label="Charger", accelerator="Ctrl+F")
        self.filesMenu.add_separator()
        self.filesMenu.add_command(command=self.master.quit, label="Quitter", accelerator="Ctrl+Q")

        self.editMenu = tk.Menu(self, tearoff=0)
        self.editMenu.add_command(command=self.master.collapse, label="Replier")
        self.editMenu.add_command(command=self.master.expandCurrent, label="Déplier la sélection")
        self.editMenu.add_command(command=self.master.expandAll, label="Déplier tout")

        #Raccourcis claviers pour les boutons de menu :
        self.bind_all("<Control-o>", lambda x: self.master.importTxt())
        self.bind_all("<Control-q>", lambda x: self.master.quit())

        self.add_cascade(label="Fichiers", menu=self.filesMenu, underline=0)
        self.add_cascade(label="Edition", menu=self.editMenu, underline=0)
    pass
pass