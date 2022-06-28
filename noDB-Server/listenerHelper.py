import os
from shutil import rmtree

import netifaces
import os
from agentsHelper import removeAgent, getAgentsForListener
from common import *
from collections import OrderedDict
from listener import Listener

# 'Dictionary that remembers insertion order'
listeners = OrderedDict()


def checkListenersEmpty(s):
    if len(listeners) == 0:

        if s == 1:
            error("There are no active listeners.")
            return True
        else:
            return True

    else:
        return False


def ulisteners():
    l = []

    for listener in listeners:
        l.append(listeners[listener].name)

    return l


def isValidListener(name, s):
    vListeners = ulisteners()

    if name in vListeners:
        return True
    else:
        if s == 1:
            error("Invalid listener.")
            return False
        else:
            return False


def viewListeners():
    if not checkListenersEmpty(1):

        success("Active listeners:")

        print(YELLOW)
        print(" Name                         IP:Port                                  Status")
        print("------                       ------------------                       --------")

        for i in listeners:

            if listeners[i].isRunning == True:
                status = "Running"
            else:
                status = "Stopped"

            print(" {}".format(listeners[i].name) + " " * (29 - len(listeners[i].name)) + "{}:{}".format(
                listeners[i].ip, str(listeners[i].port)) + " " * (
                          41 - (len(str(listeners[i].port)) + len(":{}".format(listeners[i].ip)))) + status)

        print(cRESET)


def startListener(args):
    if len(args) == 1:
        name = args[0]
        if not listeners[name].isRunning:
            try:
                listeners[name].start()
                success("Started listener {}.".format(name))
            except:
                error("Invalid listener")
        else:
            error("Listener {} is already running".format(name))
    else:
        if len(args) != 3:
            error("Invalid arguments.")
        else:
            name = args[0]

            try:
                port = int(args[1])
            except:
                error("Invalid port.")
                return 0

            iface = args[2]

            # 获取网络相关信息
            try:
                netifaces.ifaddresses(iface)
                ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
            except:
                error("Invalid interface.")
                return 0
            if isValidListener(name, 0):
                error("Listener {} already exists.".format(name))
            else:

                listeners[name] = Listener(name, port, ip)
                progress("Starting listener {} on {}:{}.".format(name, ip, str(port)))

                try:
                    listeners[name].start()
                    success("Listener started.")
                except:
                    error("Failed. Check your options.")
                    del listeners[name]


def stopListener(args):
    if len(args) != 1:
        error("Invalid arguments.")
    else:

        name = args[0]

        if isValidListener(name, 1):

            if listeners[name].isRunning == True:
                progress("Stopping listener {}".format(name))
                listeners[name].stop()
                success("Stopped.")
            else:
                error("Listener {} is already stopped.".format(name))
        else:
            pass


def removeListener(args):
    if len(args) != 1:
        error("Invalid arguments.")
    else:

        name = args[0]

        if isValidListener(name, 1):

            listenerAgents = getAgentsForListener(name)

            for agent in listenerAgents:
                removeAgent([agent])

            rmtree(listeners[name].Path)

            if listeners[name].isRunning == True:
                stopListener([name])
                del listeners[name]
            else:
                del listeners[name]

        else:
            pass


# 11111111111111111111111
def loadListeners():
    if os.path.exists(listenersDB):

        data = readFromDatabase(listenersDB)
        temp = data[0]

        for listener in temp:
            listener = temp[listener].split()

            name = listener[0]
            port = int(listener[1])
            ip = listener[2]
            flag = listener[3]

            listeners[name] = Listener(name, port, ip)

            if flag == "1":
                listeners[name].start()

    else:
        pass


def saveListeners():
    if (len(listeners) == 0):
        clearDatabase(listenersDB)
    else:
        data = OrderedDict()
        clearDatabase(listenersDB)

        for listener in listeners:

            if listeners[listener].isRunning == True:
                name = listeners[listener].name
                port = str(listeners[listener].port)
                ip = listeners[listener].ip
                flag = "1"
                data[name] = name + "" + port + " " + ip + " " + flag

                # should be stop flask
                listeners[listener].stop()

            else:
                name = listeners[listener].name
                port = str(listeners[listener].port)
                ip = listeners[listener].ip
                flag = "0"
                data[name] = name + "" + port + " " + ip + " " + flag
        writeToDatabase(listenersDB, data)
