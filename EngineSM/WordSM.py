import re
import random
from .TextObjSM import *


class SepSM(TextObjSM):
    def __init__(self, txt):
        TextObjSM.__init__(self, txt)
    pass
pass



class WordSM(TextObjSM):
    '''This class represents a word which you can extract features from, like number of vowels, consonants, and syllable structure'''

    struct = "" #structure interne du mot (étiquetage de chaque caractère)
    structure = []
    
    def __init__(self, word):
        '''Initialise the word by feeding it a character representation ; it will then do all the work of parsing the word and defining its structure'''
        TextObjSM.__init__(self, word)
        self.struct = WordSM.syllabation(word, self.struct)

        for i in range(0, len(self.struct)):
            if 'V'.find(self.struct[i]) != -1:
                self.addToStructure('v', False, self.txt[i])
            elif 'K'.find(self.struct[i]) != -1:
                self.addToStructure('v', True, self.txt[i])
            elif 'c'.find(self.struct[i]) != -1:
                self.addToStructure('c', False, self.txt[i])
            elif 'C'.find(self.struct[i]) != -1:
                self.addToStructure('c', True, self.txt[i])
            else:
                self.addToStructure('s', False, self.txt[i])



    pass

    def setStructureVal(self, index, att='car', val=''):
        if index < len(self.structure):
            self.structure[index][att] = val
    pass

    def addToStructure(self, cat, core, car):
        self.structure.append({'cat' : cat, 'core' : core, 'car' : car})
    pass

    def getNbVowels(self):
        '''Returns the number of graphical vowels that are present in the word'''
        vo = []
        for i in range(0, len(self.txt)):
            if self.txt[i] in AlphabetSM.vowels:
                vo.append([i, self.txt[i]])
        return len(vo)
    pass

    def getNbConsonants(self):
        '''Returns the number of graphical consonants that are present in the word'''
        co = []
        for i in range(0, len(self.txt)):
            if self.txt[i] in AlphabetSM.consonants:
                co.append([i, self.txt[i]])
        return len(co)
    pass

    def getNbSyllables(self):
        '''Returns the number of kernels that are present in the word structure'''
        co = []
        for i in range(0, len(self.struct)):
            if self.struct[i] == 'K':
                co.append([i, self.struct[i]])
        return len(co)
    pass

    def getNbSeparators(self):
        '''Returns the number of graphical separators that are present in the word'''
        counter = 0
        for i in range(0, len(self.txt)):
            if self.txt[i] in AlphabetSM.seprs["all"]:
                counter += 1
        return counter
    pass

    def syllabationDeprec(self):

        s = []

        for i in range(0, len(self.vowels)):
            
            if i>0:
                if i == len(self.vowels)-1:
                    s.append([self.s[i-1][1]+1, len(self.txt)-1])
                else:
                    s.append([self.s[i-1][1]+1, self.vowels[i+1][0]-1])
            else:
                if i == len(self.vowels)-1:
                    s.append([0, len(self.txt)-1])
                else:
                    s.append([0, self.vowels[i+1][0]-1])
                
    pass

    @classmethod
    def syllabation(cls, inputText, inputStructure):
        '''Returns the internal syllabic structure of the word in form of a string'''
        inputStructure = "o"*len(inputText)

        for i in range(0, len(inputText)):
            #pour chaque caractère, on définit sa catégorie : voyelle, consonne ou autre
            if AlphabetSM.v.find(inputText[i]) != -1:
                #si le caractère est une voyelle, on met v
                inputStructure = inputStructure[:i] + 'V' + inputStructure[i+1:]
            elif AlphabetSM.c.find(inputText[i]) != -1:
                #si le caractère est une consonne, on met c
                inputStructure = inputStructure[:i] + 'c' + inputStructure[i+1:]
            else:
                #si le caractère n'est ni une voyelle, ni une consonne
                inputStructure = inputStructure[:i] + inputText[i] + inputStructure[i+1:]

        inputStructure = WordSM.defineKernels(inputText, inputStructure) #on définit quelles voyelles sont les noyaux des syllabes
        inputStructure = WordSM.defineOnset(inputStructure)
        #inputStructure = WordSM.separate(inputStructure)

        return inputStructure

    pass

    @classmethod
    def separate(cls, inputStructure):

        build = ""
        comp = 0

        if 'KC'.find(inputStructure[0]) != -1:

            build += inputStructure[0]

            for i in range(1, len(inputStructure)):
                if comp == 0:
                    if inputStructure[i] == 'K':
                        comp = 1
                    elif comp == 0 and inputStructure[i] == 'C':
                        comp = 2
                    build += inputStructure[i]
                else:
                    if comp == 1:
                        if inputStructure[i] == 'C':
                            comp = 2
                        elif inputStructure[i] == 'K':
                            comp = 1
                            build += inputStructure[i]

        return build

    pass

    @classmethod
    def defineOnset(cls, inputStructure):
        cut = re.split('(K)', inputStructure)
        newstruct = ""

        for ls in cut:
            if len(ls) > 1:
                cons = re.split('([c]+)', ls)
                #on sépare en groupes de consonnes

                for cc in cons:
                    if len(cc) > 0:
                       if cc[0] == 'c':
                           if len(cc) > 3:
                                newstruct += cc[:1] + 'C' + cc[2:]
                           else:
                                newstruct += 'C' + cc[1:]
                       else:
                            newstruct += cc
            else:
                newstruct += ls

        return newstruct


    pass

    @classmethod
    def defineKernels(cls, inputText, inputStructure):
        '''Returns an updated structure with identified vowel kernels'''
        
        
        #On regarde d'abord les digraphes de voyelle :

        matches = re.finditer(r'[' + AlphabetSM.v + ']{2}', inputText)
        #on recherche toutes les occurences de digraphes de voyelles


        for match in matches:
            if ''.join(AlphabetSM.vowelsAccented).find(inputText[match.start()]) != -1:
                #si la première voyelle est accentuée alors il s'agit du noyau
                inputStructure = inputStructure[:match.start()] + 'KV' + inputStructure[match.end():]
            else:
                inputStructure = inputStructure[:match.start()] + 'VK' + inputStructure[match.end():]

        '''Puis on s'occupe des monographes :'''

        matches = re.finditer(r'(?<!'+AlphabetSM.v+')[' + AlphabetSM.v + ']{1}(?!'+AlphabetSM.v+')', inputText)
        #on recherche toutes les occurences de monographes de voyelles

        for match in matches:
            if (match.start() > 0 and inputStructure[match.start()-1] != 'V' and inputStructure[match.start()-1] != 'K') and (match.start()+1 < len(inputText) and inputStructure[match.start()+1] != 'V' and inputStructure[match.start()+1] != 'K'):
                #si l'on n'est pas en début de chaîne et que le caractère précédent n'est pas une voyelle
                inputStructure = inputStructure[:match.start()] + 'K' + inputStructure[match.end():]
            elif match.start() == 0 and (match.start() < len(inputText) and match.end() < len(inputText)-1 and inputStructure[match.start()+1] != 'V' and inputStructure[match.start()+1] != 'K'):
                inputStructure = inputStructure[:match.start()] + 'K' + inputStructure[match.end():]
            elif ''.join(AlphabetSM.vowelsAccented).find(inputText[match.start()]) != -1:
                inputStructure = inputStructure[:match.start()] + 'K' + inputStructure[match.end():]
            #elif match.start() == len(inputText)-1: 
                #inputStructure = inputStructure[:match.start()] + 'K' + inputStructure[match.end():]

        #print(inputStructure, "?!")
        if inputStructure.find('K') == -1:
            #print("!!")
            #si l'on n'a pas d'autres noyaux précédemment :
            if inputText[len(inputText)-1] == 'e':
                #si l'on a un 'e' en dernière position :
                inputStructure = inputStructure[:len(inputText)-1] + 'K' + inputStructure[len(inputText):]
           
            elif inputText[len(inputText)-2] == 'e' and 'trnmlgzpdfhjkxb'.find(inputText[len(inputText)-1]) == -1:
                inputStructure = inputStructure[:len(inputText)-2] + 'K' + inputStructure[len(inputText)-1:]

        else:
            if inputText[len(inputText)-1] == 'e':
                inputStructure = inputStructure[:len(inputText)-1] + 'V' + inputStructure[len(inputText):]
           
            elif inputText[len(inputText)-2] == 'e' and 'trnmlgzpdfhjkxb'.find(inputText[len(inputText)-1]) == -1:
                inputStructure = inputStructure[:len(inputText)-2] + 'V' + inputStructure[len(inputText)-1:]


        return inputStructure
    pass

    @classmethod
    def Categorize(cls, txt):
        if TextObjSM.isLetter():
            return WordSM(txt)
        else:
            return SepSM(txt)
    pass

    @classmethod
    def isLetter(cls, txt):
        if txt != "" and (not txt[0] in AlphabetSM.seprs["all"] or txt[0] == '-'):
           return True
        else:
           False
    pass

    def printSyllablesStruc(self):
        return self.getSyllables(self.struct)
    pass

    def printSyllablesText(self):
        return self.getSyllables(self.txt)
    pass

    def getSyllables(self, txt):
        
        cut = txt
        matches = re.finditer("Kc[.]+", self.struct)
        i = 0
        for match in matches:
            cut = cut[:match.start()+i+1] + '.' + cut[match.end()+i-1:]
            i += 1

        matches = re.finditer("(?<=K)Cc(?!v|K)", self.struct)
        for match in matches:
            cut = cut[:match.start()+i+1] + '.' + cut[match.end()+i-1:]
            i += 1

        matches = re.finditer("cC(?!c|C)", self.struct)
        for match in matches:
            cut = cut[:match.start()+i+1] + '.' + cut[match.end()+i-1:]
            i += 1

        return cut
    pass

    def shuffleCharacters(self):
        
        l = list(range(1, len(self.txt)-1))

        random.shuffle(l)

        stOut = ""

        for i in l:
            stOut += self.txt[i]

        return self.txt[0] + stOut + self.txt[-1]
    pass

    def updateArray(self, struct):
        self.array[0] = struct
        self.array[1] = self.getTextStructure(self.array[0], self.txt)
    pass

    def getTextStructure(self, struc, txt):
        for i in range(0, len(struc)):
            if struc[i] == ".":
                txt = txt[:i] + "." + txt[i:]

        return txt
    pass

pass