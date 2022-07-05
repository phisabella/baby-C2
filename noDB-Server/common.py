import os
import pickle

# 设置打印颜色以及数据库文件CRUD


# 控制台打印颜色
from collections import OrderedDict

RED = "\u001b[31m"
GREEN = "\u001b[32m"
YELLOW = "\u001b[33m"
# 封闭标签
cRESET = "\u001b[0m"

listenersDB = "data/databases/listeners.db"
agentsDB = "data/databases/agents.db"


def prompt(name):
    prompt = "\n" + GREEN + "(" + name + ")" + RED + "::> " + cRESET
    return prompt


def error(message):
    print("\n" + RED + "[!] " + message + cRESET)


def success(message):
    print("\n" + GREEN + "[*]" + message + "\n" + cRESET)


def progress(message):
    print("\n" + YELLOW + "[*] " + message + "\n" + cRESET)


def writeToDatabase(database, newData):
    with open(database, "ab") as d:
        # HIGHEST_PROTOCOL
        # 能够支持很大的数据对象，以及更多的对象类型，并且针对一些数据格式进行了优化
        pickle.dump(newData, d, pickle.HIGHEST_PROTOCOL)


def removeFromDatabase(database, name):
    data = readFromDatabase(database)
    final = OrderedDict()

    for i in data:
        final[i.name] = i

    # del 删除字典、列表的元素、删除变量
    del final[name]

    with open(database, "wb") as d:
        for i in final:
            pickle.dump(final[i], d, pickle.HIGHEST_PROTOCOL)


# pickle can’t serialize objects that use threads
# so instead of saving the objects themselves I created
# a dictionary that holds all the information of the active
# listeners and serialized that, the server loads that dictionary
# and starts the listeners again according to the options in the dictionary.
def readFromDatabase(database):
    data = []
    with open(database, 'rb') as d:
        while True:
            try:
                data.append(pickle.load(d))
            except EOFError:
                break
    return data


def writeToDatabase(database, newData):
    print("before")
    with open(database, "ab") as d:
        pickle.dump(newData, d, pickle.HIGHEST_PROTOCOL)
    print("after")


def clearDatabase(database):
    if os.path.exists(database):
        os.read(database)
    else:
        pass
