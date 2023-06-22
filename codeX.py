#!/usr/bin/env python3
# Nícolas dos Santos Carvalho
# UEM 2022

from datetime import date
import sys
import os
import re

################################################################################
def orderFiles(l):
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

# fileregex = r".*_\d{2}\..+$"
fileregex = r".*\..+$"
numberegex = r"(?<=_)\d{2}(?=\..+$)"
dateregex = r"\d{8,}(?=_)"

opts = {
    "strict": True,
    "absolute_numeration": True,
    "name": "Nícolas dos Santos Carvalho",
    "ra": "128660"
}
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

def main(argv):
    print(argv)

    if len(argv) <= 1:
        print("ERRO: Precisa de um caminho para concatenar os arquivos, porém nenhum argumento foi passado")
        return 1

    folderPath = argv[1]

    fileNames = os.listdir(folderPath)
    fileNames = list(filter(
        lambda f: re.match(fileregex, f),
        fileNames
    ))

    fileNames = orderFiles(fileNames)

    for f in fileNames:
        # message(os.path.join(folderPath, f), 0)
        reg = re.search(numberegex, f);
        fileNumber = reg.group() if reg != None else -1;
        interp = Interpreter()
        interp.interpretFiles(os.path.join(folderPath, f))
        setupParts(interp.partitions, fileNumber)

    writeFile(os.path.join(folderPath), partsCombined)
    return 0

def writeFile(filePath, parts):
    today = date.today()

    with open(os.path.join(filePath, "./out.c"), "w") as file, open("./.templates/trabalho.c") as template:
        templ = template.read()                                 \
                        .replace("$NOME", f"{opts.name}")      \
                        .replace("$RA", f"{opts.ra}")      \
                        .replace("$DD", f"{today.day:02}")      \
                        .replace("$MM", f"{today.month:02}")    \
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
    relativeExNumber += 1
    # print(exNumber, parts)
    partsCombined["incl"] += parts["incl"]

    number = exNumber if opts['absolute_numeration'] else relativeExNumber;

    if number >= 0:
       body = (
           f"    // {number if number >= 0 else ''}\n" +
           "    {\n"
        );

    body += (
        increaseIndentation(parts["expl"], 4) + "\n" +
        increaseIndentation(parts["main"], 0)
    ) if parts["main"] != "" else ""

    if number >= 0:
        body += "}\n\n"

    partsCombined["main"] += body

    partsCombined["expl-all"] += parts["expl-all"]
    partsCombined["defn"] += parts["defn"]
    partsCombined["func"] += parts["func"]

def increaseIndentation(str, space):
    return (" "*space)+str.replace("\n", "\n"+(" "*space))

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
        if strCmp == 1 or (strCmp == 0 and filesList[i]["number"] > file["number"]):
            filesList.insert(i, file)
            return filesList

    filesList.append(file)
    return filesList

class Interpreter:
    def __init__(self):
        self.partitions = {
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

                if opts["strict"] and d["type"] == "start":
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
            name = re.search(r"((?<=//@once )[a-zA-Z_]*)", lineTrimed).group()

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
            name = re.search(r"((?<=//@start )[a-zA-Z_]*)", lineTrimed).group()
            d = {"type": ""}
            l = ""
            body = ""

            while d["type"] != "end":
                i += 1
                d = self.parseData(lines, i)
                l = d["value"]
                body += l if l.strip() != "\r\n" else ""
                i = d["index"]
            # print("//@start "+name+":\n"+body)

            return {"index": i, "type": "start", "name": name, "value": body}
        elif lineTrimed.startswith("//@end"):
            return {"index": i, "type": "end", "value": ""}

        return {"index": i, "type": "line", "value": line}

if __name__ == "__main__":
    # try:
    main(sys.argv)
    print("Programa executado com sucesso")
    # except:
    #     print("Programa retornou erros")
    #     input("Aperte 'Enter' para fechar")
