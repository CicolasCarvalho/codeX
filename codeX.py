#!/usr/bin/env python3
# Nícolas dos Santos Carvalho
# UEM 2022

from enum import Enum
from datetime import date
import sys
import os
import re

class IndentationType(Enum): SPACE = 1; TAB = 2;

################################################################################
def sortFiles(l: list[str]):
    """
    Ordene os arquivos e os exercicios para que ordem devem ficar
    por padrão ordena pela data e número do exercicio
    """

    # fileNumbers = list(map(splitFileName, l))

    # newL = []
    # for f in fileNumbers:
    #     newL = sortingFilesList(newL, f)
    # newL = list(map(lambda f: f["name"], newL))

    print(l)

    return l

def mapLines(l):
    """
    Faça aqui oque quiser com as linhas!
    a string que for passada aqui passa para filtragem e depois é salva no arquivo
    """

    return l

def filterLines(l):
    """
    Filtre as linhas do jeito que quiser aqui! (acontece depois do map)
    se retornar verdadeiro a linha será salva no arquivo, caso falso não será
    """

    return True

fileregex = r"\d{8,}_\d{2}\..+$"
numberegex = r"(?<=_)\d{2}(?=\..+$)"
dateregex = r"\d{8,}(?=_)"

opts = {
    "strict": True,
    "absolute_numeration": True,

    "indentation_type": IndentationType.SPACE,
    "indentation_size": 4,
    "block_scoping": False,

    "name": "Nícolas dos Santos Carvalho",
    "ra": "128660",
}

################################################################################

class Argument:
    def __init__(self, names, requirements):
        self.names = names
        self.requirements = requirements

args: list[Argument] = [
    Argument(["-bs", "--block_scoping"],        0),
    Argument(["-rn", "--relative_numeration"],  0),
    Argument(["-is", "--indentation_size"],     1),
    Argument(["-it", "--indentation_type"],     1),
]

def argParsing(argv: list[str], argsTemplate: list[Argument]):
    newL = []
    i = 0

    while i < len(argv):
        name = argv[i]

        for a in argsTemplate:
            if name in a.names:
                i += 1

                req = a.requirements
                name = f"{a.names[0]} {' '.join(argv[i:i+req])}"

                i += req - 1
                break

        newL.append(name.strip())
        i += 1

    return newL

def argEvaluation(argv: list[str]):
    folderPath = argv.pop(0)
    files = []

    while len(argv) > 0:
        arg = argv.pop().split(" ")

        if arg[0] == "-bs":
            opts["block_scoping"] = True
        elif arg[0] == "-rn":
            opts["absolute_numeration"] = False
        elif arg[0] == "-is":
            opts["indentation_size"] = int(arg[1])
        elif arg[0] == "-it":
            if arg[1].lower() == "tab": opts["indentation_type"] = IndentationType.TAB
            elif arg[1].lower() == "space": opts["indentation_type"] = IndentationType.SPACE
            else: raise f"Unknown IndenatationType: {arg[1]}"
        else:
            files.append(arg[0])

    return (folderPath, files)

################################################################################

partsCombined = {
    "expl-all": "", # explain all
    "expl": "",     # explain
    "incl": "",     # include
    "defn": "",     # definitions
    "main": "",     # main
    "func": ""      # functions
}
onceList = {}
relativeExNumber = 0

def main(argv: list[str]):
    argv = argParsing(argv, args)
    print(argv)

    if len(argv) <= 1:
        print("ERRO: Precisa de um caminho para concatenar os arquivos, porém nenhum argumento foi passado")
        return 1

    argv.pop(0)
    (folderPath, files) = argEvaluation(argv)
    print(folderPath)

    fileNames = os.listdir(folderPath)
    fileNames = list(filter(
        lambda f: re.match(fileregex, f),
        fileNames
    ))

    fileNames += files
    fileNames = sortFiles(fileNames)

    fileParts = []

    for f in fileNames:
        # message(os.path.join(folderPath, f), 0)
        reg = re.search(numberegex, f);
        fileNumber = reg.group() if reg != None else -1;
        interp = Interpreter()
        interp.interpretFiles(os.path.join(folderPath, f))

        part = interp.partitions
        part["number"] = int(fileNumber)
        fileParts = addByPrior(fileParts, part)

    for p in fileParts:
        setupParts(p, p["number"])


    writeFile(os.path.join(folderPath), partsCombined)
    return 0

def writeFile(filePath, parts):
    today = date.today()

    with open(os.path.join(filePath, "./out.c"), "w") as file, open("./.templates/trabalho.c") as template:
        templ = template.read()                                 \
                        .replace("$NOME", f"{opts['name']}")    \
                        .replace("$RA",   f"{opts['ra']}")      \
                        .replace("$DD",   f"{today.day:02}")    \
                        .replace("$MM",   f"{today.month:02}")  \
                        .replace("$AAAA", f"{today.year:04}")   \
                        .replace("$INCL", parts["incl"])        \
                        .replace("$EXPL", parts["expl-all"])    \
                        .replace("$MAIN", parts["main"])        \
                        .replace("$DEFS", parts["defn"])        \
                        .replace("$FUNC", parts["func"])        \
                        .replace("\r", "")                      \
                        .split("\n")

        templ = list(filter(filterLines,
                    list(map(mapLines, templ))
                ))
        templ = "\n".join(templ)
        templ = re.sub(r"\n{2,}", "\n\n", templ)

        file.write(templ)
        print(f"{os.path.join(filePath, './out.c')} criado com sucesso!")

def setupParts(parts, exNumber):
    global relativeExNumber
    body = ""
    relativeIndentation = 0
    relativeExNumber += 1

    number = exNumber if opts['absolute_numeration'] else relativeExNumber;

    if number >= 0 and (parts["main"] != "" or parts["expl"] != ""):
        body = increaseIndentation(f"// {number}\n", 1)

    if opts["block_scoping"]:
        body += increaseIndentation("{\n", 1);
        relativeIndentation += 1

    if parts["expl"] != "":
        body += increaseIndentation(parts["expl"], relativeIndentation+1) + "\n"

    if parts["main"] != "":
        body += increaseIndentation(parts["main"], relativeIndentation)

    if opts["block_scoping"]:
        body += increaseIndentation("}\n", relativeIndentation)
        relativeIndentation -= 1

    partsCombined["incl"] += parts["incl"]
    partsCombined["main"] += body +                 ("\n" if body != "" else "")
    partsCombined["expl-all"] += parts["expl-all"]
    partsCombined["defn"] += parts["defn"]
    partsCombined["func"] += parts["func"] +        ("\n" if parts["func"] != "" else "")

def getIndentationType():
    return (" " if opts["indentation_type"] == IndentationType.SPACE else "\t")

def increaseIndentation(str: str, space: int):
    space_number = opts["indentation_size"] * (space if opts["indentation_type"] == IndentationType.SPACE else space//4)
    indentation = getIndentationType()*space_number

    str = indentation + str.replace("\n", "\n" + indentation)

    return str.rstrip(getIndentationType())

def splitFileName(str):
    return {
        "date": re.search(dateregex, str).group(),
        "number": re.search(numberegex, str).group(),
        "name": str
    }

def strDateCompare(strDate1, strDate2):
    if strDate1 == strDate2: return 0

    dateToInt = lambda s: int(s[4:]+s[2:4]+s[:2])
    return 1 if dateToInt(strDate1) > dateToInt(strDate2) else -1

def sortingFilesList(filesList: list[str], file):
    print(file["name"])
    for i in range(0, len(filesList)):
        strCmp = strDateCompare(filesList[i]["date"], file["date"])
        if strCmp == -1 or (strCmp == 0 and filesList[i]["number"] < file["number"]):
            filesList.insert(i, file)
            return filesList

    filesList.append(file)
    return filesList

def addByPrior(partList, elem):
    print(elem["prior"])
    for i in range(0, len(partList)):
        if elem["prior"] > partList[i]["prior"]:
            partList.insert(i, elem)
            return partList

    partList.append(elem)
    return partList

class Interpreter:
    def __init__(self):
        self.partitions = {
            "prior": 7,
            "expl-all": "",
            "expl": "",
            "incl": "",
            "defn": "",
            "main": "",
            "func": ""
        }

    def interpretFiles(self, filePath):
        with open(filePath, 'r') as f:
            data = f.readlines()

            i = 0
            while i < len(data):
                d = self.parseData(data, i)

                i = d["index"] + 1

                if d["type"] == "prior":
                    self.partitions["prior"] = d["value"]
                    pass

                if opts["strict"] and d["type"] == "start":
                    print(d["name"])
                    self.partitions[d["name"]] += d["value"]
                else:
                    #TODO: implementar in-line (non strict mode)
                    pass

    def parseData(self, lines, i):
        line = lines[i]

        lineTrimed = line.strip()
        if lineTrimed.startswith("//@ignore"):
            return {"index": i+1, "type": "ignore", "value": ""}
        elif lineTrimed.startswith("//@once "):
            name = re.search(r"((?<=//@once ).*)$", lineTrimed).group()

            if name in onceList:
                onceList[name] += 1
                print(i if onceList[name] == 1 else i+1)
            else:
                onceList[name] = 1

            return {
                "index": i if onceList[name] == 1 else i+1,
                "type": "once",
                "value": ""
            }
        elif lineTrimed.startswith("//@start "):
            name = re.search(r"((?<=//@start )[a-zA-Z_].*)$", lineTrimed).group()
            d = {"type": ""}
            l = ""
            body = ""

            while d["type"] != "end":
                i += 1
                d = self.parseData(lines, i)
                l = d["value"].replace("\r", "")
                body += l
                i = d["index"]
            # print("//@start "+name+":\n"+body)

            return {"index": i, "type": "start", "name": name, "value": body}
        elif lineTrimed.startswith("//@end"):
            return {"index": i, "type": "end", "value": ""}
        elif lineTrimed.startswith("//@prior"):
            prior = re.search(r"((?<=//@prior )[0-9]+)$", lineTrimed).group()

            return {"index": i, "type": "prior", "value": int(prior)}

        return {"index": i, "type": "line", "value": line}

if __name__ == "__main__":
    # try:
    main(sys.argv)
    print("Programa executado com sucesso")
    # except:
    #     print("Programa retornou erros")
    #     input("Aperte 'Enter' para fechar")

