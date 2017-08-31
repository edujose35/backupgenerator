import os
import re
import datetime
import sys

class Cmd(object):
   def __init__(self, cmd):
       self.cmd = cmd
   def __call__(self, *args):
       return os.system("%s %s" % (self.cmd, " ".join(args)))

class Sh(object):
    def __getattr__(self, attribute):
        return Cmd(attribute)

sh = Sh()

class Tools(object):
    def __init__(self,nomeArquivo):
        self.nomeArquivo = nomeArquivo
        self.arrDados = []
        self.data = data = str(datetime.datetime.now())[:19]

    def backup(self,dados):
        passwd = dados["password"]
        db = dados["database"]
        user = dados["user"]
        host = dados["host"]

        if "port" in dados:
            port = dados["port"]
        else:
            port = "3306"

        if "backupFolder" in dados:
            backupFolder = dados["backupFolder"]
        else:
            backupFolder = "./backups/"

        ignoreTables = dados["ignoreTables"] if "ignoreTables" in dados else ""
        dumpLine = "mysqldump -u " + user + " -p" + passwd + " -h " + host + " -P " + port

        print "Iniciando backup de:\"" + db + "\" em: " + self.data
        print "Criando Diretorio"

        if not os.path.isdir(backupFolder):
            sh.mkdir(backupFolder)

        if "name" in dados:
            name = dados["name"] + ".sql"
        else:
            name = "backup" + ".sql"

        backupName = backupFolder + db + (self.data.replace(" ", "-")).replace(":", "-") + name

        sqlIgnoreTables = ""

        for table in ignoreTables.split(","):
            sqlIgnoreTables += " --ignore-table=" + db + "." + table

        print "Gerando arquivo de backup para base"

        dumpLine += sqlIgnoreTables + " --add-drop-table --skip-triggers --add-drop-database --set-gtid-purged=OFF --databases " + db + " > " + backupName
        os.system(dumpLine)

        print "Compactando os dados"

        tarLine = "tar -cf " + backupName + ".tar.gz " + backupName
        os.system(tarLine)

        print "Limpando cache"

        cleanLine = "rm " + backupName
        os.system(cleanLine)

        return 1

    def lerArquivo(self):
        arquivo = open(self.nomeArquivo, "r")

        if re.sub('.*\.', '', arquivo.name) != "txt":
            print "Formato invalido"
            exit(1)

        i = 0

        tempDict = {}

        for linha in arquivo:
            if linha[:1] == "#":
                continue

            temp = linha.split("=")

            if (len(temp) < 2):
                tempDict["HEADER"] = re.sub('[^a-zA-Z0-9]+', '', temp[0])
            else:
                tempDict[temp[0]] = temp[1].replace('\n', '')

            if temp[0] == "\n" or linha[:5] == "[END]" or linha == "":
                self.arrDados.insert(i, tempDict)
                tempDict = {}

            i += 1

        arquivo.close()