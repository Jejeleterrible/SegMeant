# -*- coding: utf-8 -*-

from .TextSM import *
import math
import re
import sys
from dataclasses import dataclass


@dataclass
class Point:
    '''Dataclass qui représente un couple token/nb d'occurences.'''

    token: str
    occurences: int = 1

    def __str__(self) -> str:
        return str(self.token)
    pass

pass


class TextComparison:
    '''Classe permettant de comparer deux textes tokenisés. L'option 'verbose' permet d'afficher la progression sur la sortie standard.'''

    def __init__(self, tx: list[SegmentedTextSM], filter: list[str] = None, verbose: bool = False):

        #Compteur du nombre de tokens exclus
        self.excluded: list = []

        for i in range(0, len(tx)):
            self.excluded.append(0)

        #On enregistre les sacs de mot dans l'instance
        self.tx: list = tx

        if verbose:
            sys.stdout.write("\n----Démarrage du processus de comparaison ----\n")

            #On exclue de chaque sac de mots les tokens du fichier d'exclusions
            if verbose:
                sys.stdout.write(f"Exclusion des {len(filter)} tokens blacklistés.\n")
            
            for i,tok in enumerate(tx):
                for w in filter:
                    for el in tok:
                        if str(el) == w:
                            tok.remove(w)
                            self.excluded[i] += 1
            
                if verbose:
                    sys.stdout.write(f"{self.excluded[i]} tokens exclus dans le texte {i}.\n")

                #On supprime les éventuels "mots vides"

                while '' in tok:
                    if verbose:
                        sys.stdout.write(f"Suppression de mots vides dans le texte {i}.\n")
                    tok.remove('')


        self.v: list = [] #le vocabulaire commun
        self.t: list = [] #le vocabulaire total (sans les doublons)

        #On parcours les tokens pour essayer de trouver le vocabulaire commun :
        for i in range(0, len(tx)):
            for j in range(i, len(tx)):
                if i != j:
                    self.v.append([])
                    if verbose:
                            sys.stdout.write(f"\n\n----Recherche du vocabulaire commun ({i}-{j}) : ----\n")
                    for k, ref in enumerate(tx[i]):
                        
                        if ref in tx[j]:

                            if not ref in self.v[-1]:
                                #On ajoute le mot au vocabulaire commun seulement si il n'est pas déjà présent
                                if verbose:
                                    sys.stdout.write(f">\t({k:4d}/{len(tx[i]):4d}) \tNouveau token commun trouvé : \'{ref}\'\n")
                                self.v[-1].append(ref)

            for token in tx[i]:
                    self.t.append(token)

        self.t = self.__clean(self.t, count=False, verbose=verbose)

        self.tu: list[list] = []
        self.vect: list[list] = []

        for i,t in enumerate(tx):
            if verbose:
                sys.stdout.write("\n\n----Suppression des doublons et comptage des occurences : ----\n")
                sys.stdout.write(f"\n\t# Texte {i} : \n")
            #On supprime tous les doublons des sacs et on compte le nombre d'occurences
            self.tu.append(self.__clean(t, verbose=verbose))

            if verbose:
                sys.stdout.write("\n\n----Construction des vecteurs : ----\n")
                sys.stdout.write(f"\n\t# Texte {i} : \n")
            #On construit les vecteurs pour chaque sac basé sur le nombre d'occurences de chaque token du vocabulaire total
            self.vect.append(self.__buildVector(self.t, self.tu[-1], verbose=verbose))


    def __clean(self, lst: list, *, verbose: bool = False, count: bool = True) -> list[Point]:
        '''Supprime les doublons dans la liste et compte le nombre d'occurences de chaque token.'''

        l: list = []
        has: bool = False

        #On cherche les doublons et on compte les occurences
        for word in lst:
            if len(l) > 0:
                has = False
                for el in l:
                    if count:
                        if el.token == word:
                            has = True
                            el.occurences += 1
                            break
                    else:
                        if word == el:
                            has = True
                            break
                if not has:
                    if count:
                        l.append(Point(token=word))
                    else:
                        l.append(word)
                elif verbose:
                    sys.stdout.write(f"\t>\tDoublon trouvé : \'{word}\'\n")
            else:
                if count:
                    l.append(Point(token=word))
                else:
                    l.append(word)

        return l
    pass

    def __buildVector(self, t: list, tu: list, *, verbose: bool = False) -> list[int]:
        '''On crée le vecteur pour le sac de mots à partir d'une liste d'occurences (sans les doublons) et d'une liste du vocabulaire total'''
        
        v: list = []

        for el in t:
            found = False
            for vec in tu:
                if el == str(vec):
                    #Si le token est dans la liste d'occurences du sac, on ajoute directement son nombre d'occurences au vecteur
                    v.append(vec.occurences)
                    found = True
                    if verbose:
                        sys.stdout.write(f"\t>\t\'{el:<15}\' présent.\n")
            if not found:
                #Si le mot n'est pas dans ce sac, alors on l'ajoute au vecteur avec un nombre d'occurences de 0.
                v.append(0)

                if verbose:
                    sys.stdout.write(f"\t>\t\'{el:<15}\' NON présent.\n")

        return v
    pass

    def dice(self, a:list, b:list, intersection:list) -> float:
        '''Retourne l'indice DICE de similarité entre les deux listes :
        s(t1, t2) = 2(t1 ∩ t2) / (|t1| + |t2|)
        Avec t1 et t2 débarassés des doublons
        '''
        if len(a)+len(b) != 0:
            return (2*len(intersection))/(len(a)+len(b))
        else:
            return 0

    pass

    def jaccard(self, a:list, b:list, v:list) -> float:
        '''Retourne l'indice jaccard de similarité entre les deux listes :
        J(t1, t2) = (t1 ∩ t2) / (t1 ∪ t2)
        Avec t1 et t2 débarassés des doublons
        '''
        if (len(a)+len(b)-len(v)) != 0:
            return len(v)/(len(a)+len(b)-len(v))
        else:
            return 0

    pass

    def cosVector(self, x, y) -> float:
        '''Retourne le cosinus des deux vecteurs de taille égale générés depuis les deux textes étudiés.
        cos(v1, v2) = (v1 ∙ v2) / (∥v1∥ * ∥v2∥) = pdtScalaire(v1, v2) / pdtNormes(v1, v2)
        '''

        v1norm = 0
        v2norm = 0

        #On calcule la norme de chaque vecteur, en élevant chaque coordonée au carré pour ensuite faire la racine de la somme, 
        # afin d'obtenir la valeur absolue
        for val in self.vect[x]:
            v1norm += val*val

        for val in self.vect[y]:
            v2norm += val*val
        
        v1norm = math.sqrt(v1norm)
        v2norm = math.sqrt(v2norm)

        #On calcule le produit scalaire (la somme du produit des coordonnées des vecteurs deux à deux)
        scalarProduct = 0
        for i in range(0, len(self.vect[x])):
            scalarProduct += (self.vect[x][i]*self.vect[y][i])

        if (v1norm*v2norm) != 0:
            return scalarProduct / (v1norm*v2norm)
        else:
            return 0
    pass

    def correlation(self, vec1: list, vec2: list) -> float:
        
        if len(vec1) == 0 or len(vec2) == 0:
            return 0
        
        mean1: float = sum(vec1)/len(vec1)
        mean2: float = sum(vec2)/len(vec2)

        ecart1: list = []
        for v in vec1:
            ecart1.append(v - mean1)

        ecart2: list = []
        for v in vec2:
            ecart2.append(v - mean2)
        
        sumP = 0
        for i in range(len(vec1)):
            sumP += ecart1[i]*ecart2[i]

        s1 = 0
        for e in ecart1:
            s1 += e ** 2

        s2 = 0
        for e in ecart2:
            s2 += e ** 2

        denom = math.sqrt((s1) * (s2))

        if denom == 0:
            return 0

        return sumP / denom

    pass

    def __str__(self) -> str:
        resultStr: str = ""

        resultStr += f"\n\n#######\t\tVocabulaire total des textes : \t({len(self.t)} tokens)\n---------------------------------------------------------------------\n" + str(self.t)
        b = 0

        for i in range(0, len(self.tx)):

            resultStr = f"\nTexte {i} : \t{len(self.tx[i])} tokens \t|\t {self.excluded[i]} exclus \t|\t total : {len(self.tx[i]) + self.excluded[i]} tokens\n" + resultStr
                    

            for j in range(i, len(self.tx)):
            
                if i != j:

                    union:list = [] #l'ensemble des mots 
                    for el in self.t:
                        if el in self.tx[i] or el in self.tx[j]:
                            union.append(el)

                    inter:list = []
                    for el in self.t:
                        if el in self.tx[i] and el in self.tx[j]:
                            inter.append(el)

                    
                    '''if i+1>=len(self.tx):
                        ind2 = len(self.tx)-i
                        resultStr += f"\n\n#######\t\tVocabulaire commun des textes {ind2}|{i} : \t({len(self.v[j])} tokens)\n---------------------------------------------------------------------\n" + str(self.v[i])
'''
                    #else:
                    if i+1>=len(self.tx):
                        ind2 = len(self.tx)-i
                    else:
                        ind2 = b
                    resultStr += f"\n\n######################################################################\
                        \n#######\t\tVocabulaire commun des textes {i}|{j} : \t({len(self.v[b])}/{len(union)} tokens)\n---------------------------------------------------------------------\n" + str(self.v[b]) + '\n'


                    resultStr += "\n\n\n\t\tMETRIQUES : \n---------------------------------------------------------------------\n"
                    resultStr += f"Indice DICE : \t\t{round(self.dice(self.tu[i], self.tu[j], self.v[ind2])*100, 3)} %\n"
                    resultStr += f"Indice Jaccard : \t{round(self.jaccard(self.tu[i], self.tu[j], self.v[ind2])*100, 3)} %\n"
                    resultStr += f"Cosinus : \t\t{round(self.cosVector(i, j), 3)} / 1.00\n"
                    resultStr += f"Corrélation linéaire : \t{round(self.correlation(self.vect[i], self.vect[j]), 3)}\n\n"

                    b += 1

        resultStr += "\n\n--FIN DE L'ANALYSE--\n#####################################################################"

        return resultStr
    pass

    def export(self, *, separator: str ='\t') -> str:
        '''Exporte les vecteurs au format tsv ou csv'''
        
        out: str = f"token{separator}"

        for i in range(0, len(self.tx)):
                out += f"texte {i}{separator}"
        else:            
            if out[-1] == separator:
                out = out[:-1]
            out += "\n"
                
            

        for i in range(0, len(self.t)):

            out += f"{self.t[i]}{separator}"

            for j in range(0, len(self.tx)):
                out += f"{self.vect[j][i]}{separator}"

            if out[-1] == separator:
                out = out[:-1]
            out += "\n"

        return out
    pass

    def nbComparison(self, n) -> int:
        '''
        Soit la suite u telle que : u(0) = 0 et u(n) = n-1 + u(n-1)
        '''
        if n == 0:  # Base case
            return n
        return (n - 1) + self.nbComparison(n - 1)
    pass

pass






def tokenize(txt: str, *, verbose: bool = False) -> list[str]:
    '''Découpe une chaîne de caractères en listes de mots en minuscule via une expression régulière.'''

    txt = txt.lower()
    result = re.split(r"[^\w0-9-]+", txt)

    if verbose:
        sys.stdout.write(f"Terminée. Tokens : {len(result)} pour {len(txt)} caractères.\n")

    return result
pass
