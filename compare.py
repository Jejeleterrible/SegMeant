# -*- coding: utf-8 -*-

'''
Ce script permet à l'utilisateur de choisir des fichiers d'exclusions, des fichiers textes et de les comparer pour noter les résultats
dans un fichier CSV et un fichier texte de rapport (dossier 'OUT_')
'''

from io import TextIOWrapper
import matplotlib.pyplot as plt
from EngineSM import *
import argparse
import configparser
import mmap
import sys
import os


CONFIG_FILE = "config.ini"

ROOT_PREFIX = "OUT"
XML_FILES = 'xml'
SM_FILES = 'sm'

NEWLINE = '\n'
TABULATION = '\t'
CARRIAGE_RETURN = '\r'

SPECIAL_CHARACTERS = "1"

def toggleSpecialChars(s: str, raw=True) -> str:
    if raw:
        s = re.sub(NEWLINE, r'\\n', s)
        s = re.sub(TABULATION, r'\\t', s)
        s = re.sub(CARRIAGE_RETURN, r'\\r', s)

    else:
        s = re.sub(r'\\n', NEWLINE, s)
        s = re.sub(r'\\t', TABULATION, s)
        s = re.sub(r'\\r', CARRIAGE_RETURN, s)

    return s
pass


def extractFilter(paths: list[str], verbose: bool=False) -> list[str]:
    if paths[0] != "":

        filters: list[str] = []
        excl: list[TextIOWrapper] = []

        for path in paths:
            excl.append(open(path, mode='r', encoding="utf-8"))

        #Si l'on a un descripteur de fichier valide pour les exclusions, on le tokenise
        if excl != None:

            for fi in excl:
                if args.verbose:
                    sys.stdout.write("Fichier de filtre fourni. Tokenisation : ")
                filters += tokenize(fi.read(), verbose=args.verbose)

        for file in excl:
                file.close()
        
        return filters
pass


def createConfig(parser: configparser.ConfigParser, confFile: TextIOWrapper, addFilters: list=None) -> None:
    parser['FILTRES'] = {'newline' : SPECIAL_CHARACTERS, 'tabulation' : SPECIAL_CHARACTERS, 'carriage_return' : SPECIAL_CHARACTERS}
    
    #Si l'on fournit un filtre à ajouter aux filtres normaux
    if addFilters != None:
        parser['FILTRES']['additional'] = ""
        for item in addFilters:
            parser['FILTRES']['additional'] += item + ' '

    parser['FOLDERS'] = {'root_prefix' : ROOT_PREFIX, 'xml_files' : XML_FILES, 'sm_files' : SM_FILES}

    parser['LEVELS'] = {}
    for lvl in HIERARCHY:
        seps = lvl[1]
        seps = toggleSpecialChars(seps)
        parser['LEVELS'][lvl[0]] = seps

    parser.write(confFile)
pass

if __name__ == "__main__":


    #####################################################################################
    # CONFIGURATION
    #####################################################################################

    #On met en place un parser d'arguments de ligne de commande et on précise les arguments acceptés par le programme :
    argparser = argparse.ArgumentParser(description="Analyse la similarité de deux fichiers textes.")
    argparser.add_argument('input', help="Les fichiers texte à comparer.", type=str, default=[""], nargs='*')
    argparser.add_argument('-o', "--output", help="Nom du projet à appliquer au dossier et aux fichiers de sortie?", type=str, default=None, nargs=1)
    argparser.add_argument('-f', '--filter', help="Le(s) fichier(s) d'exclusions (accepte plusieurs fichiers).", type=str, default=[""], nargs='+')
    argparser.add_argument('-v', '--verbose', help="Affiche le déroulé du processus sur la sortie standard.", action="store_true")
    argparser.add_argument('--log', help="Redirige la sortie standard vers le fichier spécifié. ('runtime.log' si rien de spécifié)", \
        type=str, nargs='?', const="runtime.log", default="")
    argparser.add_argument('-g', '--graphs', help="Crée des grpahiques sous format png.", action="store_true")
    argparser.add_argument('--data', help="Précise le format de sortie des vecteurs. CSV par défaut. Accepte CSV,\
         TSV ou encore un caractère unique comme délimiteur de valeur.", default=["tsv"], nargs=1, type=str)
    argparser.add_argument('-c', '--config', help="Reconstruit le fichier de configuration et quitte le programme.", action="store_true")

    args = argparser.parse_args()

    config = configparser.ConfigParser()

    if args.config:
        with open(CONFIG_FILE, mode='w', encoding="utf-8") as f:
            createConfig(config, f)
        exit()

    if args.input == "":
        exit()
    else:
        for i, tx in enumerate(args.input):
            if not os.path.isfile(tx):
                raise TypeError
            else:
                if args.verbose:
                    sys.stdout.write(f"[TXT{i}]\tFichier '{tx}' valide.\n")


    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, mode='w', encoding="utf-8") as f:
            createConfig(config, f)
    else:
        config.read(CONFIG_FILE, encoding="utf-8")

    filters: list = []

    for fil in config['FILTRES']:

        if fil == 'newline':
            if config['FILTRES'].get(fil, SPECIAL_CHARACTERS) == '1':
                filters += NEWLINE
        if fil == 'tabulation':
            if config['FILTRES'].get(fil, SPECIAL_CHARACTERS) == '1':
                filters += TABULATION
        if fil == 'carriage_return':
            if config['FILTRES'].get(fil, SPECIAL_CHARACTERS) == '1':
                filters += CARRIAGE_RETURN
        else:
            sp = config['FILTRES'][fil].split()
            filters += sp

    root_prefix = config["FOLDERS"].get('root_prefix', ROOT_PREFIX)

    folders: dict = {
        'xml_files' : config["FOLDERS"].get('xml_files', XML_FILES),
        'sm_files' : config["FOLDERS"].get("sm_files", SM_FILES)
    }

    hierarchy: list[tuple] = []

    for i,lvl in enumerate(config['LEVELS']):
        hierarchy.append((lvl, toggleSpecialChars(config['LEVELS'].get(lvl, HIERARCHY[i][1]), False)))

    #####################################################################################
    # CHEMINS D'ACCES
    #####################################################################################

    pathExclusion: list[str] = args.filter
    pathTxt: list[str] = args.input
    pathReport: str = ""

    txts: list[str] = []
    t: list[list] = []

    
    interfix: str = "" #chaîne descriptive à insérer dans les noms de fichier, si 
    if args.output != None:
        interfix = args.output[0]
    else:
        for p in pathTxt:
            interfix += p.split('.')[0] + '_'

    if interfix[-1] != '_':
                interfix += '_'

    #On crée les chemins d'accès du dossier de sortie et des fichiers de sortie principaux
    out_dir_full: str = root_prefix + "_" + interfix[:-1]
    fname = interfix + "occurences_vector"
    pathReport = interfix + "report.log"

    
    #On définit l'extension du fichier de donnée en fonction du paramètre --data :
    if args.data[0].lower() == "csv":
        fname += ".csv"
    elif args.data[0].lower() == "tsv":
        fname += ".tsv"
    else:
        fname += ".txt"

    #On regarde si le dossier de sortie existe, sinon on le crée :
    if not os.path.isdir(out_dir_full):
        os.mkdir(out_dir_full)

    #Pour chaque dossier de sortie, on regarde s'il existe et si ce n'est pas le cas, on le crée
    for fold in folders:
        path = os.path.join(out_dir_full, folders[fold])
        if not os.path.isdir(path):
            os.mkdir(path)


    #####################################################################################
    # ENTREES (et leur sauvegarde)
    #####################################################################################

    if args.log != "":
        sys.stdout = open(os.path.join(out_dir_full, "runtime.log"), mode="w", encoding="utf-8")
        args.verbose = True

    if args.verbose:
        sys.stdout.write("###################################################\nDEBUT DU TRAITEMENT.\n\n")


    for i, path in enumerate(pathExclusion):
        if os.path.isfile(path) and args.verbose:
            sys.stdout.write(f"[EXCL{i+1}]\tFichier '{path}' valide.\n")



    for i, tx in enumerate(pathTxt):
        if args.verbose:
            sys.stdout.write(f"[TXT{i}]\tTokenisation : ")

        #On génère le nom du dossier de sortie, du fichier qui va récupérer les valeurs des vecteurs et 
        # le nom du fichier log à partir des fichiers txt
        interfix += tx.split("/")[-1].split(".")[-2] + "_"

        #On ouvre et on récupère le texte des fichiers, puis on tokenise le texte de chaque fichier 
        # et on stocke les tokens obtenus dans une liste.
        with open(tx, mode='r', encoding="utf-8") as f:
            txts.append(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ).read().decode("utf-8"))
            text = SegmentedTextSM(txts[-1], hierarchy)
            t.append(text)
        
        #On écrit la structure de chaque texte dans un fichier xml.
        with open(os.path.join(out_dir_full, folders['xml_files'], str(tx[:-4] + ".xml")), mode='wb') as fXML:
            saveAsXML(fXML, text.masterNode)

        #On enregistre chaque texte dans un fichier binaire contenant l'objet SegmentedTextSM
        with open(os.path.join(out_dir_full, folders['sm_files'], str(tx[:-4] + ".sm")), mode='wb') as fSM:
            save(fSM, text)

    #Si l'on a un(des) fichier(s) d'exclusions valide(s), on l'(les) ouvre et on le(s) passe au constructeur de TextComparison, 
    # avec les deux textes tokenisés.
    if pathExclusion != [""]:
        filters += extractFilter(pathExclusion, args.verbose)


    txtComp = TextComparison(t, filters, verbose=args.verbose) 


    #####################################################################################
    # SORTIES
    #####################################################################################

    #On crée le fichier des vecteurs et on écrit les données dedans.
    with open(os.path.join(out_dir_full, fname), mode='w', encoding="utf-8") as ftsv:
        if args.data[0].lower() == "csv":
            ftsv.write(txtComp.export(separator=','))
        elif args.data[0].lower() == "tsv":
            ftsv.write(txtComp.export(separator='\t'))
        elif args.data[0] != None:
            ftsv.write(txtComp.export(separator=args.data[0]))

    #On ouvre le fichier de rapport entré par l'utilisateur et on écrit dedans toutes les infos utiles.
    with open(os.path.join(out_dir_full, pathReport), mode='w', encoding="utf-8") as fr:

        for i, path in enumerate(pathTxt):
            fr.write(f"Fichier texte {i} : \t\t\t\"{path}\"\n")

        fr.write(f"Fichier des vecteurs : \t\t\t\"{fname}\"\n")

        for i, path in enumerate(pathExclusion):
            fr.write(f"Fichier de filtre {i} : \t\t\t\"{path}\"\n")
        fr.write(str(txtComp))

    if args.verbose:
        sys.stdout.write("\nOPERATION TERMINEE.\n###################################################")

    #####################################################################################

    if args.graphs:
        #txtComp.vect.sort()

        plt.figure(figsize=(100, 20))
        plt.subplot(131)
        for i, vec in enumerate(txtComp.vect):

            if args.verbose:
                sys.stdout.write(f"VEC{i}: {vec}")

            plt.plot(txtComp.t, vec, linestyle="", marker="*")

        plt.xlabel("Tokens")
        plt.xticks(rotation=65)
        plt.ylabel("Fréquence")
        plt.savefig(os.path.join(out_dir_full, "token_freq.png"), bbox_inches='tight')

        fig = plt.figure(figsize=(100,20))
        fig.add_subplot(132)
        plt.xlabel("Tokens")
        plt.xticks(rotation=65)

        weights: list = [0]*len(txtComp.t)
        threshold = 10
        w: list = []

        for i, vec in enumerate(txtComp.vect):
            for j, v in enumerate(vec):
                weights[j] += v

        for i,p in enumerate(weights):
            if weights[i] >= threshold:
                w.append([txtComp.t[i], weights[i]])

        for point in w:
            plt.scatter(point[0], point[1])

        plt.yscale('log')
        plt.grid(visible=True, which='both', axis='both')

        #plt.ylim(0, max(weights))

        plt.savefig(os.path.join(out_dir_full, "token_proeminent.png"), bbox_inches='tight')
        #plt.show()
        plt.close()

    if args.log != "":
        sys.stdout.close()

        #os.replace("runtime.log", os.path.join(out_dir_full, "runtime.log"))



