import io
import pickle
import xml.etree.cElementTree as ET

from EngineSM.TextObjSM import Node, TextObjSM

#from EngineSM.TextSM import SegmentedTextSM


def save(file: io.BufferedWriter, obj) -> None:
    '''Sauvegarde un fichier binaire contenant un objet "SegmentedTextSM"'''
    pickle.dump(obj, file)
pass

def saveTwo(file: io.BufferedWriter, obj1, obj2) -> None:
    pickle.dump([obj1, obj2], file)
pass

def load(file: io.BufferedReader):
    '''Charge un fichier binaire contenant un objet "SegmentedTextSM" et le retourne.'''
    return pickle.load(file)
pass


def saveAsXML(file: io.BufferedWriter, tree: Node):

    top = ET.Element('SegmentedTextSM')
    XMLTree = ET.ElementTree(top)

    def parseChildren(node: Node, parent):
        for child in node.children:
            ch = ET.SubElement(parent, node.label)
            ch.set("tags", child.tags)
            ch.set("struct", child.struct)
            if isinstance(child, TextObjSM):
                ch.set("type", type(child).__name__)
                ch.text = child.getString()

            parseChildren(child, ch)
    pass

    parseChildren(tree, top)

    ET.indent(XMLTree, "    ")
    XMLTree.write(file, encoding='utf-8', xml_declaration=True)
pass


def saveAsXML_DEPREC(file: io.BufferedWriter, tree: Node):

    top = ET.Element('SegmentedTextSM')
    XMLTree = ET.ElementTree(top)

    for child in tree.children:
        ch = ET.SubElement(top, "chunk")

        for chil in child.children:
            c = ET.SubElement(ch, "phrase")

            for chi in chil.children:
                c1 = ET.SubElement(c, "proposition")
                
                for chi1 in chi.children:
                    c2 = ET.SubElement(c1, "token")
                    c2.text = str(chi1)

    ET.indent(XMLTree, "    ")
    XMLTree.write(file, encoding='utf-8', xml_declaration=True)
pass