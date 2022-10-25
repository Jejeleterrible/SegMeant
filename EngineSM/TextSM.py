# -*- coding: utf-8 -*-

from .WordSM import *
from .FilesSM import *
import re

HIERARCHY = [('proposition', ',;:'),('phrase', '.?!'),('chunk', '\n')]

class SegmentedTextSM:
    '''Représente un texte segmenté en tokens et organisés hiérarchiquement.'''
   
    
    def __init__(self, txt: str="", levels: list[tuple]=HIERARCHY):

        self.listObjs: list = self.segment(txt)
        self.order()
        self.hierarchy: list = levels

        self._index: int = 0
    pass

    def __add__(self, seg2):
        newData: SegmentedTextSM = SegmentedTextSM.__new__(SegmentedTextSM)
        newData.listObjs = self.listObjs + seg2.listObjs

        del self.listObjs
        del seg2.listObjs

        return newData
    pass


    def __str__(self) -> str:
        txt: str = ""

        for obj in self.listObjs:
            txt += str(obj)

        return txt     
    pass

    def __len__(self) -> int:
        return len(self.listObjs)
    pass

    def __iter__(self):
        self._index = 0
        return self
    pass

    def __next__(self):
        if self._index < len(self.listObjs):
            result = str(self.listObjs[self._index])
            self._index += 1
            return result
        raise StopIteration
    pass

    def remove(self, item):
        if not item in self:
            raise ValueError

        if isinstance(item, TextObjSM):
            self.listObjs.remove(item)
        elif isinstance(item, str):
            for obj in self.listObjs:
                if item == str(obj):
                    self.listObjs.remove(obj)
    pass


    def hasInSuccession(self, needle: TextObjSM | list) -> bool:
        listWords: list = self.getListWords()
        i: int = 0
        indices: list = []
        has: bool = True

        if not isinstance(needle, list):
            return True

        while i < self.getNbWords():
            for ne in needle:                
                if len(ne) == str(listWords[i]):
                    indices.append(needle.index(ne))
                    needle.remove(ne)
            if len(needle) == 0:
                break
            i += 1

        for i in indices:
            if i>0 and indices[i]-1 == indices[i-1]:
                has = True
            else:
                return False

        return has
    pass

    def has(self, needle: list | TextObjSM) -> bool:
        '''Retourne si oui ou non, le texte possède le mot ou la liste de mots en entrée. Les mots de la liste sont testés \
            de manière discontinue (=non contigue)'''
        
        i: int = 0

        if isinstance(needle, list):
            for i in range(0, len(self)):
                for ne in needle:
                    if isinstance(ne, list):
                            if self.hasInSuccession(ne):
                                needle.remove(ne)
                    else:
                        if str(ne) == str(self.listObjs[i]):
                            needle.remove(ne)
                if len(needle) == 0:
                    break

        else:
            for i in range(0, len(self)):
                if str(needle) == str(self.listObjs[i]):
                    needle = []

        if len(needle) > 0:
            return False
        else:
            return True
    pass

    def findIndex(self, needle: list | TextObjSM) -> tuple:
        '''Trouve le premier index des mots recherchés. Les index sont retournés dans l'ordre croissant (pas l'ordre des mots).'''

        result: tuple(int,) = ()
        if isinstance(needle, list):
            for i in range(0, len(self)):
                for ne in needle:
                    if isinstance(ne, list):
                            if self.hasInSuccession(ne):
                                result += (i,)
                    else:
                        if str(ne) == str(self.listObjs[i]):
                            result += (i,)
                if len(needle) == 0:
                    break
            return result
        else:
            for i in range(0, len(self)):
                if needle == str(self.listObjs[i]):
                    return (i,)

        return (-1,)
    pass


    def retrieve(self, needle):
        
        listWords = self.getListWords()

        '''for i in range(0, self.getNbWords()):
            if needle == listWords[i].getString():
                return listWords[i]
        return None'''

        i = 0

        while i < self.getNbWords():# and needle != listWords[i].getString():
            if needle == listWords[i].getString():
                return listWords[i]
            else:
                i += 1

        return None
    pass

    def order(self, hierarchy: list =[('proposition', ',;:'),('phrase', '.?!'),('chunk', '\n')]) -> None:
        '''La fonction 'order' découpe le texte en différents niveaux imbriqués spécifiés dans 'hierarchy' et crée un arbre de dépendances \
            à partir des tokens. Elle renvoie ensuite le noeud maître, qui donne accès par le haut aux données.
        hierarchy est un tableau de tuples avec le nom et les délimiteurs utilisés, ordonné depuis le plus petit ensemble. Dans la fonction, \
            les niveaux sont imbriqués, c'est à dire que le niveau 5 ne peut contenir que des éléments de niveau 4, le niveau 4 des éléments de niveau \
                3 etc. '''

        #buffer est une mémoire tampon contenant, pour chaque niveau, les différents noeuds.
        #delims est un tableau de chaînes qui contiennent les délimiteurs ; chaque niveau inférieur contient les délimiteurs du niveau supérieur afin
        # de les imbriquer.
        buffer = [[] for i in range(len(hierarchy)+1)]
        delims = [""]*len(hierarchy)

        #cette boucle génère les différentes chaînes de délimiteurs issus de 'hierarchy' 
        for i in range(0, len(hierarchy)+1):
            temp = hierarchy[i:]
            for c in temp:
                delims[i] = delims[i] + ''.join(c[1])

        #le tableau 'indices' est une mémoire contenant les indices des délimiteurs pour chaque niveau.
        #Architecture : [niveau][compteur|index précédent] Accès : indices[0][0] : compteur de tokens ; indices[3][1] : index du chunk précédent
        indices = [[0,0] for i in range(len(hierarchy)+1)]

        for i, token in enumerate(self.listObjs):
            buffer[0].append(token)

            for h in range(0, len(hierarchy)):
                #h = 1
                if delims[h].find(str(token)) != -1:
                    #si on trouve un démarqueur de niveau :
                    if h > 0:
                        phrase = Node(hierarchy[h-1][0])
                    else:
                        phrase = Node('token')
                    

                    for el in buffer[h]:
                        if el.parent == None:
                            el.relateAsChild(phrase)


                    indices[h+1][1] += indices[h][0]+1
                    buffer[h+1].append(phrase)

                    indices[h][0] += 1

        if len(buffer[-1]) == 0:
            buffer[-1].append(Node())
            buffer[-1][0].groupSetParent(buffer[-2][:])

        self.masterNode = Node(hierarchy[-1][0])
        self.masterNode.groupSetParent(buffer[-1][:])
    pass
        

    def segment(self, txt: str) -> list:
        '''Découpe un texte en différents objets : SepSM pour les séparateurs et WordSM pour les mots.'''

        #temp est un buffer pour le mot en cours.
        #listObjs est la liste d'objets retournée en fin de fonction.
        temp: str = ""
        listObjs: list = []
        
        for i in range(0, len(txt)):

            print(txt[i], end="")
    
            if WordSM.isLetter(txt[i]):
                
                sig = re.search(AlphabetSM.sigle, ''.join(txt[i:]))
                #print(f"SIG:{sig}")

                if sig != None and sig.start() == 0:
                        
                        l = sig.end() - sig.start()

                        #print(f"SIGLE i:{i} {txt[i:i+l]}")
                        wor = WordSM(txt[i:i+l])
                        listObjs.append(wor)

                        if len(txt)-i > l:
                            listObjs.append(SepSM(' '))

                        i += wor.getLength()
                   
                        sig = None
                else:
                    temp += txt[i]
            else:

                if txt[i] == '\'' or txt[i] == '’':
                    listObjs.append(WordSM(temp.lower()+txt[i]))

                elif txt[i] == '-':
                    temp += '-'

                elif txt[i] != '\"':

                    if temp != "":
                        #Si j'ai un mot en formation je l'ajoute à la liste
                            listObjs.append(WordSM(temp.lower()))
                    
                    if len(listObjs) > 0 :
                    #Si j'ai déjà des objets listés, et que le précédent est un séparateur, alors :

                        if txt[i] in AlphabetSM.seprs["all"] and str(listObjs[-1]) == " ":
                            #Si j'ai un séparateur et que l'objet précédent est un espace, alors je supprime ce dernier
                            listObjs.pop()


                        if txt[i] in AlphabetSM.seprs["punctuation"][0]:
                        #Si j'ai un signe de ponctuation :
                            if str(listObjs[-1])[0] in AlphabetSM.seprs["punctuation"][0]:
                            #Si l'objet précédent est lui aussi une ponctuation:
                                if (str(listObjs[-1])[0] == txt[i]) or \
                                    (AlphabetSM.seprs["punctuation"][1][AlphabetSM.seprs["punctuation"][0].index(txt[i])] and \
                                    AlphabetSM.seprs["punctuation"][1][AlphabetSM.seprs["punctuation"][0].index(str(listObjs[-1])[-1])]):
                                #Si l'objet précédent égale l'actuel OU si le poids de l'objet actuel et le poids de l'objet précédent 
                                    listObjs[-1].append(txt[i])

                                else:
                                    listObjs.append(SepSM(txt[i]))
                            else:
                                #Sinon, je l'ajoute en tant qu'objet indépendant
                                listObjs.append(SepSM(txt[i]))
                                

                        elif txt[i] in AlphabetSM.seprs["delimiters"] and txt[i] != " ":
                        #Si j'ai un délimiteur, je l'ajoute en tant qu'objet à part entière :
                            listObjs.append(SepSM(txt[i]))
                    else:                
                        listObjs.append(SepSM(txt[i]))
                else:                
                    listObjs.append(SepSM(txt[i]))

                temp = ""
            i += 1
        if temp != "":
            listObjs.append(WordSM(temp.lower()))

        if str(listObjs[-1]) != '\n':
            listObjs.append(SepSM("\n"))

        return listObjs
       
    pass


    def getListWords(self) -> list:
        '''Retourne une liste de mots exclusivement (les séparateurs sont omis).'''
        
        lst: list = []
        for obj in self.listObjs:
            if WordSM.isLetter(obj.getString()):
                lst.append(obj)

        return lst
    pass

    def getListSep(self) -> list:
        '''Retourne une liste de séparateurs exclusivement (les mots sont omis).'''
        
        lst: list = []
        for obj in self.getListObjs():
            if not WordSM.isLetter(obj.getString()):
                lst.append(obj)

        return lst
    pass

    def getNbWords(self):
        return len(self.getListWords())
    pass

    def getNbObjs(self):
        return len(self.listObjs)
    pass

    def getNbSep(self):
        return len(self.getListSep())
    pass

    def getMaxWordSize(self) -> int:
        '''Retourne la longeur maximale d'un mot dans le texte ; utile pour aider au formattage d'une sortie console.'''

        ml: int = 0
        for i in range(0, self.getNbWords()):
            length = self.getListWords()[i].getLength()
            if length > ml:
                ml = length
        return ml
    pass

    def logWords(self) -> str:
        '''Retourne un texte listant les mots ainsi que toutes les données relatives à ces derniers'''
        tx = f"Liste des mots de la phrase ({self.getNbWords()}) \n\"{str(self)}\" : \n\n"
        pad = self.getMaxWordSize()

        for i in range(0, self.getNbWords()):
              tx += f"- ({i:03d}) [{self.getListWords()[i].getString():<{pad}}] {'':>13}[{self.getListWords()[i].struct:{pad}}] ({self.getListWords()[i].getNbSyllables()} syl.) \
               : VOWELS ({self.getListWords()[i].getNbVowels()}) ; CONS ({self.getListWords()[i].getNbConsonants()}) ; SEP ({self.getListWords()[i].getNbSeparators()})\n"

        return tx
    pass

    def logObjs(self, separate: bool =True) -> str:
        '''Retourne un texte listant les objets ainsi que toutes les données relatives à ces derniers'''
        tx: str = f"Liste des objets de la phrase ({self.getNbObjs()}) \n\"{str(self)}\" : \n\n"
        ts: str = ""
        pad: int = self.getMaxWordSize()

        for i in range(0, self.getNbObjs()):
              
            if WordSM.isLetter(self.getListObjs()[i].getString()):
                tx += f"- ({i:03d}) [{self.getListObjs()[i].getString():<{pad}}] {'':>13}[{self.getListObjs()[i].struct:{pad}}] ({self.getListObjs()[i].getNbSyllables()} syl.) \
               : VOWELS ({self.getListObjs()[i].getNbVowels()}) ; CONS ({self.getListObjs()[i].getNbConsonants()}) ; SEP ({self.getListObjs()[i].getNbSeparators()})\n"

            else:
                if separate:
                    ts += f"- ({i:02d}) SEP [{self.getListObjs()[i].getString()}]{'-':->{100-len(self.getListObjs()[i].getString())}}\n"
                else:
                    tx += f"- ({i:02d}) SEP [{self.getListObjs()[i].getString()}]{'-':->{100-len(self.getListObjs()[i].getString())}}\n"

        return tx + "\n" + ts
    pass
pass

###################################################################################################################################################

