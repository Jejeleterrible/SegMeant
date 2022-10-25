# -*- coding: utf-8 -*-

from .AlphabetSM import *

class Node:
    def __init__(self, label=""):
        self.parent: Node = None
        self.ind: int = 0
        self.children: list = []
        self.tags: str = ""
        self.struct: str = ""
        self.label = label
    pass

    def __iter__(self):
        self.current_index: int = 0
        return self
    pass

    def __len__(self):
        return len(self.children)
    pass

    def __next__(self):
        if self.current_index < len(self.children):
            x = self.children[self.current_index]
            self.current_index += 1
            return x
        raise StopIteration
    pass

    def __getitem__(self, item):
        return self.children[item]
    pass

    def __str__(self):
        s: str = ""
        for child in self.children:
            s += str(child)
        return s
    pass

    def isType(self, nodeType):
        return isinstance(self, nodeType)
    pass

    def relateAsParent(self, child, topLevel=True, replace=False):
        if replace or self.parent == None:
            child.ind = len(self.children)
            self.children.append(child)
            if topLevel:
                child.relateAsChild(self, False)
    pass

    def relateAsChild(self, parent, topLevel=True):
        self.parent = parent
        if topLevel:
            parent.relateAsParent(self, False)
    pass

    def next(self, iter=0):
        if self.parent != None and len(self.parent.children) > self.ind+1+iter :
            return self.parent.children[self.ind+1+iter]
        
        return None
    pass

    def previous(self, iter=0):
        if self.parent != None and self.ind-1+iter>=0:
            return self.parent.children[self.ind-1+iter]

        return None

    def delRelations(self):
        del self.parent
        del self.ind
        del self.children

        Node.__init__(self)
    pass
    pass


    def decapsulate(self):
        #sert à récupérer l'enfant qui est le plus en bout d'arbre (=pas d'enfants)
        r = []

        if len(self.children)>0:
            

            for child in self.children:
                
                if len(child.children)>0:
                    r = r + child.decapsulate()
                    
                else:
                    r.append(child)
                    #print(len(r), r[-1])
        else:
            r = self

        return r
    pass


    def getDepth(self):
        r = []
        count = 1

        if len(self.children)>0:
            

            for child in self.children:
                
                if len(child.children)>0:
                    r = r + child.decapsulate()
                    
                else:
                    r.append(child)
                    count += 1
                    #print(len(r), r[-1])
        else:
            r = self

        return count
    pass


    def decapsulateToType(self, childType):
        #sert à récupérer le noeud le plus bas d'un certains type
        r = self

        if len(self.children)>0:
            if isinstance(self.children[0], childType):
                r = self.children[0]
            else:
                for child in self.children:
                    r = child.decapsulateToType(childType)

        else: 
            return None

        return r
    
    pass

    ###############

    def encapsulate(self):
        #sert à récupérer le parent des noeuds (parent commun)

        if self.parent != None:
                r = self.parent.encapsulate()
        else:
                r = self

        return r
    pass

    def groupSetParent(self, nodes):
        for n in nodes:
            self.relateAsParent(n)
    pass
pass


class TextObjSM(Node):

    def __init__(self, txt):
        self.txt = txt
        Node.__init__(self)
    pass

    def __len__(self) -> int:
        return len(self.txt)
    pass

    def __str__(self):
        return f"{self.txt}"
    pass

    def getString(self):
        return self.txt
    pass

    def getLength(self):
        return len(self.txt)
    pass

    def append(self, txt):
        self.txt += txt

pass


