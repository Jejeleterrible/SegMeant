# -*- coding: utf-8 -*-
'''Module principal de l'application graphique pour SegMeant. Il développe la classe Application, qui représente la fenêtre principale.'''

import os
import threading
import xml.etree.cElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import tkinter.font as tkFont

from EngineSM import *
from .PopUpEnterText import *
from .CtrlFrameSM import *
from .MenuSM import *
from .TextViewSM import *
from .TreeSM import *

from io import open

class Application(tk.Tk):
    def __init__(self, master=None):

        tk.Tk.__init__(self)

        self.processPool: ThreadPoolExecutor = ThreadPoolExecutor()

        self.file: str = None
        self.segmentedText: SegmentedTextSM = None
        self.chunks: list = []
        self.detachedItems: list = []
        self.wordLink: dict = {}
        self.chunk: str = ""
        self.ctrlLoading = tk.IntVar()
        self.treeRows: list = []


        self.createWidgets()
        self.title("SegMeant")

    def createWidgets(self) -> None:
        '''Génère les widgets de la fenêtre principale.'''

        #On crée les objets
        self.panedWindow = ttk.PanedWindow(self)
        self.menu = MenuSM(self)
        self.tree = TreeSM(self.panedWindow)
        self.textView = TextViewSM(self.panedWindow)
        self.ctrlFrame1 = CtrlFrameSM(self)
        self.progressBar = ttk.Progressbar(self)
        self.popupText = PopUpEnterText(self)
        self.listChunks = tk.Listbox(self.ctrlFrame1, selectmode=tk.BROWSE, width=35)

        self.listChunks.bind("<<ListboxSelect>>", self.displayChunk)
        

        #On place les widgets dans la fenêtre
        self.tree.grid(column=0, columnspan=5, row=0, padx=(10,0), pady=5, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.tree.treeScroll.grid(column=5, row=0, sticky=(tk.N,tk.S))
        self.textView.grid(column=6, row=0, columnspan=5, sticky=tk.N+tk.S, padx=(10,0))
        self.textView.textScroll.grid(column=11, row=0, sticky=(tk.N,tk.S))
        self.panedWindow.grid(column=0, row=0, columnspan=10, sticky=(tk.N,tk.W,tk.S,tk.E))
        self.ctrlFrame1.grid(column=0, row=1, columnspan=10, sticky=(tk.N,tk.W,tk.S,tk.E))
        self.listChunks.pack()
        self.progressBar.grid(column=0, row=2, columnspan=10, sticky=(tk.N,tk.W,tk.S,tk.E))
        

    pass

    def searchWord(self, i: int) -> str:
        '''Retourne l'ID de l'objet à la position 'i'.'''
        return self.tree.identify_row(i)
    pass

    pass

    def collapse(self) -> None:
        '''Referme tous les noeuds de l'arbre.'''

        self.collapseChildren('')
    pass

    def collapseChildren(self, parent: str) -> None:
        '''Referme tous les noeuds enfant du parent spécifié.'''

        self.tree.item(parent, open=False)
        for child in self.tree.get_children(parent):
            self.collapseChildren(child)
    pass

    def expandCurrent(self) -> None:
        '''Ouvre tous les noeuds enfant de la sélection.'''

        self.expandAllChildren(self.tree.focus())
    pass

    def expandAll(self) -> None:
        '''Ouvre tous les noeuds de l'arbre'''

        self.expandAllChildren('')
    pass

    def expandAllChildren(self, parent: str) -> None:
        '''Ouvre tous les noeuds enfant du parent spécifié'''

        self.tree.item(parent, open=True)
        for child in self.tree.get_children(parent):
            self.expandAllChildren(child)
    pass

    def mode(self, master: str="") -> None:
        '''Permet de mettre à jour le mode d'affichage de l'arbre selon "ctrlTypeDisplay" : afficher tous les objets ou seulement les mots.'''

        for el in self.treeRows:
            if self.ctrlFrame1.ctrlTypeDisplay.get() == 1: #hide
                if isinstance(el.obj, SepSM):
                    el.parent = self.tree.parent(el.id)
                    self.tree.detach(el.id)

            if self.ctrlFrame1.ctrlTypeDisplay.get() == 0: #show
                if isinstance(el.obj, SepSM):
                    self.tree.reattach(el.id, el.parent, el.ind)

    pass


    def saveData(self) -> None:
        '''Sauvegarde le texte segmenté dans un fichier binaire.'''
        fd = filedialog.asksaveasfilename(filetypes=[("SegMeant files", ".sm")], defaultextension=".sm")

        FilesSM.save(fd, self.segmentedText)
    pass

    def saveXML(self, dict: bool=False) -> None:
        '''Sauvegarde le contenu de l'arbre dans un fichier XML. NOTE : Sera remplacé.'''
        fd = filedialog.asksaveasfilename(filetypes=[("XML Files", ".xml"), ("Text files", ".txt")], defaultextension=".xml")

        top = ET.Element('SegmentedTextSM')
        XMLTree = ET.ElementTree(top)
        for chunk in self.tree.get_children():
            ch = ET.SubElement(top, self.tree.item(chunk, "text"))
            for sentence in self.tree.get_children(chunk):
                if not dict:
                    s = ET.SubElement(ch, self.tree.item(sentence, "text"))
                for prop in self.tree.get_children(sentence):
                    if not dict:
                        p = ET.SubElement(s, self.tree.item(prop, "text"))
                    for child in self.tree.get_children(prop):
                        vals = self.tree.item(child, "values")
                        c = ET.SubElement(p, self.tree.item(child, "text"), {'type' : vals[1], 'characteristics' : vals[2]})
                        if vals[0] == '\n':
                            c.text = '\\n'
                        else:
                            c.text = vals[0]
        
        ET.indent(XMLTree, "    ")
        
        with open(fd, "wb") as objFile:
            XMLTree.write(fd, encoding='utf-8', xml_declaration=True)
                    
    pass

    def loadData(self) -> None:
        '''Charge un fichier contenant un objet "SegmentedTextSM" et met à jour l'arbre et la TextView'''
        fd = filedialog.askopenfilename(filetypes=[("SegMeant files", ".sm")])

        self.segmentedText = FilesSM.load(fd)

        self.listChunks.delete("0", "end")

        if self.ctrlFrame1.ctrlThreads.get():
                    self.processPool.submit(self.insertChunks)
        else:
            self.insertChunks()

        if self.ctrlFrame1.ctrlThreads:
            self.processPool.submit(self.updateTree)
        else:
            self.updateTree()
    pass

    def importTxt(self) -> None:
        '''Importe un fichier texte, en segmente le contenu et appelle "updateTree" pour créer l'arbre et afficher le texte.'''
        
        self.ctrlLoading = tk.IntVar()

        fd = filedialog.askopenfilename(filetypes=[("Text files", ".txt"), ("Python files", ".py")])

        if fd != None:
            with open(mode='r', file=fd, encoding='utf-8')  as entryFile:
                size = os.path.getsize(entryFile.name)

                self.segmentedText = SegmentedTextSM(file=fd)

                self.listChunks.delete("0", "end")


                self.ctrlFrame1.fileName.configure(text=f'Fichier : {entryFile.name}\nTaille : {size} | NbMots : {self.segmentedText.getNbWords()}\n \
                | NbObjs : {len(self.segmentedText)} | Caractères : {len(str(self.segmentedText))}')

                if self.ctrlFrame1.ctrlThreads.get():
                    self.processPool.submit(self.insertChunks)
                else:
                    self.insertChunks()


                #self.segmentedText = SegmentedTextSM(buffer)
                self.ctrlLoading.set(0)
                self.progressBar.stop()

                entryFile.close()
        #print(buffer)
        self.ctrlLoading.set(0)

        if self.ctrlFrame1.ctrlThreads.get():
            #threading.Thread(target=self.updateTree).start()
            self.processPool.submit(self.updateTree)
        else:
            self.updateTree()
        #threading.Thread(target=self.progressBar.start).start()
        #self.updateTree()

    pass

    def insertChunks(self):
        for i in range(0, len(self.segmentedText.masterNode.children)):
            tx = str(self.segmentedText.masterNode[i])
            tx.replace("\n", "")
            tx.replace("\t", "")
            tx.replace("\r", "")
            self.listChunks.insert("end", f"Chunk#{i}: \"{tx[:10]} ... {tx[-10:]}\"")
    pass

    def displayChunk(self, event) -> None:
        #self.refresh()
        
        #self.listChunks.selection_set(tk.ACTIVE, tk.ACTIVE)
        indices = self.listChunks.curselection()

        #for i in indices:
        self.updateTree(indices)
    pass

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.treeRows = []

        self.textView.configure(state=tk.NORMAL)
        self.textView.delete("1.0", "end")
        self.textView.configure(state=tk.DISABLED)
    pass

    def textInsert(self, index, text, tag):
        self.textView.configure(state=tk.NORMAL)

        if tag != "":
            self.textView.insert(index, text, (tag,))
        else:
            self.textView.insert(index, text)
        self.textView.configure(state=tk.DISABLED)
    pass


    def findWord(self, x, index):

        wordCount = 0
        root = self.tree.get_children()
        for sentence in self.tree.get_children(root):
            for prop in self.tree.get_children(sentence):
                for word in self.tree.get_children(prop):
                    if self.tree.item(word, "values")[1].find("Mot") != -1:
                        wordCount += 1
                        if wordCount == index:

                            self.focus_set()
                            self.tree.see(word)
                            self.tree.focus(word)
                            self.tree.selection_set(word)
                            #self.tree.selection_get()
                            break

        #self.tree.selection_set()
    pass

    def updateTree(self, chunk: tuple=(0,)) -> None:
        '''Met à jour l'arbre et la TextView (notamment après un chargement de fichier ou un changement de chunk).'''
        #chunk: str = self.tree.insert(parent='', index="end", text="Chunk#1")

        self.refresh()
        self.textView.indexWord: int = 1

        for ch in chunk:
            self.chunk: str = self.insertTreeLevel('', self.segmentedText.masterNode[ch], len(self.segmentedText.hierarchy)-1, ch)
    pass

    def insertTreeLevel(self, parent: str, node: Node, level: int, index: int) -> str:
        '''Insert dans l'arbre le noeud correspondant et s'appelle récursivement pour insérer les noeuds enfant.'''
        
        if isinstance(node, WordSM):
            p: str = self.tree.insert(parent=parent, index="end", text=f"", values=(str(node), 'Mot', node.struct, node.tags), tags="mot")
            self.treeRows.append(TreeRow(id=p, obj=node, parent="", ind=index))

            self.textInsert("end", " " + str(node), f"{self.textView.indexWord}")
            self.wordLink[f"{self.textView.indexWord}"] = (self.textView.get("current wordstart", "current"), self.textView.indexWord)

            def findCallback(event, self=self, textTag=self.textView.indexWord):
                    return self.findWord(event, textTag)

            self.textView.tag_bind(f"{self.textView.indexWord}", "<ButtonRelease-1>", findCallback)
            self.textView.indexWord += 1

        elif isinstance(node, SepSM) and str(node) != " ":
            self.textInsert("end", str(node), "")
            fin = ''.join(AlphabetSM.seprs['punctuation'][0]).find(str(node)[0])
            weight = AlphabetSM.seprs['punctuation'][1][fin]
            if node.struct == "":
                if  fin != -1:
                    #si le séparateur est une ponctuation :
                    node.struct = "ponc (w:" + str(weight) + ")"
                elif ''.join(AlphabetSM.seprs['delimiters']).find(str(node)) != -1:
                    node.struct = "delim"
                else:
                    node.struct = "autre"

            p: str = self.tree.insert(parent=parent, index="end", text=f"", values=(str(node), 'Séparateur', node.struct, node.tags), tags="sep")
            self.treeRows.append(TreeRow(id=p, obj=node, parent="", ind=index))
        else:
            tx = str(node)
            tx.replace("\n", "")
            tx.replace("\t", "")
            tx.replace("\r", "")
            p: str = self.tree.insert(parent=parent, index="end", text=f"{self.segmentedText.hierarchy[level][0]}#{index}", values=(f"\"{tx[:10]} ... {tx[-10:]}\"","", "", ""))

        if node.children != None:
            for i, el in enumerate(node):
                if el != None and level > -1:
                    self.insertTreeLevel(p, el, level-1, i)
        return p
    pass   


    def treeSelected(self, event) -> None:

        self.textView.tag_remove("mot", "1.0", "end")
        self.textView.tag_remove("phrase", "1.0", "end")
        self.textView.tag_remove("proposition", "1.0", "end")
        
        for item in self.tree.selection():
            parent = self.tree.parent(item)
            text = self.tree.item(item, "text")
            values = self.tree.item(item, "values")


            if parent == self.chunk:
                #si on a sélectionné une phrase :
                #print(f"1.{self.sentences[text][0]}", f"1.{self.sentences[text][1]}")
                self.textView.tag_add("phrase", f"1.{self.sentences[text][0]}", f"1.{self.sentences[text][1]}")

            elif self.tree.item(parent, "text").find('Phrase') != -1:
                #si on a sélectionné une proposition :
                textParent = self.tree.item(parent, "text")
                self.textView.tag_add("phrase", f"1.{self.sentences[textParent][0]}", f"1.{self.sentences[textParent][1]}")
                self.textView.tag_add("proposition", f"1.{self.clauses[text][0]}", f"1.{self.clauses[text][1]}")
            elif parent != '':
                #si on a sélectionné un mot :
                textParent = self.tree.item(parent, "text")
                self.textView.tag_add("proposition", f"1.{self.clauses[textParent][0]}", f"1.{self.clauses[textParent][1]}")
                textParent = self.tree.item(self.tree.parent(parent), "text")
                self.textView.tag_add("phrase", f"1.{self.sentences[textParent][0]}", f"1.{self.sentences[textParent][1]}")
                if len(values) > 1 and values[1] == "Mot":
                    self.textView.tag_add("mot", f"1.{self.words[text][0]}", f"1.{self.words[text][1]}")
  
    pass

pass
