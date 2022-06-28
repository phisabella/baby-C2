from collections import OrderedDict
from os import system, error

import readline

import listenerHelper
from agentsHelper import *
from payloadHelper import *


class AutoComplete(object):
    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        response = None
        if state == 0:
            if text:
                self.matches = [s
                                for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response


class Menu:
    def __init__(self, name):
        self.name = name

        self.commands = OrderedDict()
        self.Commands = []

        self.commands["help"] = ["Show help.", ""]
        self.commands["home"] = ["Return home.", ""]
        self.commands["exit"] = ["Exit.", ""]

    def registerCommand(self, command, description, args):

        self.commands[command] = [description, args]

    def clearScreen(self):
        pass

    def uCommands(self):
        for i in self.commands:
            self.Commands.append(i)

    def parse(self):
        # readline模块定义了一系列函数用来读写Python解释器中历史命令，
        # 并提供自动补全命令功能。这个模块可以通过relcompleter模块直接调用，
        # 模块中的设置会影响解释器中的交互提示
        readline.set_completer(AutoComplete(self.Commands).complete)
        readline.parse_and_bind('tab: complete')

        cmd = input(prompt(self.name))
        cmd = cmd.split()
        command = cmd[0]
        args = []

        for i in range(1, len(cmd)):
            args.append(cmd[i])

        return command, args

    def showHelp(self):

        success("Avaliable commands: ")

        print(YELLOW)
        print(" Command                         Description                         Arguments")
        print("---------                       -------------                       -----------")

        for i in self.commands:
            print(" {}".format(i) + " " * (32 - len(i)) + "{}".format(self.commands[i][0]) + " " * (
                        36 - len(self.commands[i][0])) + "{}".format(self.commands[i][1]))


print(cRESET)


def evListeners(command, args):
    if command == "list":
        # qweqweqweqwe
        listenerHelper.viewListeners()

    elif command == "start":
        listenerHelper.startListener(args)

    elif command == "stop":
        listenerHelper. stopListener(args)

    elif command == "remove":
        listenerHelper. removeListener(args)

def evAgents(command, args):
    if command == "list":
        viewAgents()
    elif command == "remove":
        removeAgent(args)
    elif command == "rename":
        renameAgent(args)
    elif command == "interact":
        interactWithAgent(args)

def evPayloads(command, args):

    if command == "help":
        payloadMenu.showHelp()
    elif command == "home":
        home()
    elif command == "exit":
        Exit()
    elif command == "list":
        viewPayloads()
    elif command == "generate":
        generatePayload(args)

def listenersHelper():
    listenerMenu.clearScreen()

    while True:
        try:
            command, args = listenerMenu.parse()
        except:
            continue
        if command not in ListenersCommands:
            error("Invalid command.")
        elif command == "home":
            home()
        elif command == "help":
            listenerMenu.showHelp()
        elif command == "exit":
            Exit()
        else:
            evListeners(command, args)


def agentsHelper():
    agentsMenu.clearScreen()

    while True:

        try:
            command, args = agentsMenu.parse()
        except:
            continue

        if command not in AgentsCommands:
            error("Invalid command.")
        elif command == "home":
            home()
        elif command == "help":
            agentsMenu.showHelp()
        elif command == "exit":
            Exit()
        else:
            evAgents(command, args)


def payloadsHelper():
    payloadMenu.clearScreen()

    while True:

        try:
            command, args = payloadMenu.parse()
        except:
            continue

        if command not in PayloadsCommands:
            error("Invalid command.")
        else:
            evPayloads(command, args)

def evAgents(command, args):
    if command == "list":
        viewAgents()
    elif command == "remove":
        removeAgent(args)
    elif command == "rename":
        renameAgent(args)
    elif command == "interact":
        interactWithAgent(args)


def evHome(command, args):
    if command == "help":
        homeMenu.showHelp()
    elif command == "home":
        home()
    elif command == "listeners":
        listenersHelper()
    elif command == "agents":
        agentsHelper()
    elif command == "payloads":
        payloadsHelper()
    elif command == "exit":
        Exit()


def home():
    homeMenu.clearScreen()
    while True:
        try:
            command, args = homeMenu.parse()
        except:
            continue
        if command not in homeCommands:
            error("Invalid command.")
        else:
            evHome(command, args)


def Exit():
    listenerHelper.saveListeners()
    exit()


agentsMenu = Menu("agents")
listenerMenu = Menu("listeners")
payloadMenu = Menu("payloads")
homeMenu = Menu("c2")

agentsMenu.registerCommand("list", "List active agents.", "")
agentsMenu.registerCommand("interact", "Interact with an agent.", "<name>")
agentsMenu.registerCommand("rename", "Rename agent.", "<agent> <new name>")
agentsMenu.registerCommand("remove", "Remove an agent.", "<name>")

listenerMenu.registerCommand("list", "List active listeners.", "")
listenerMenu.registerCommand("start", "Start a listener.", "<name> <port> <interface> | <name>")
listenerMenu.registerCommand("stop", "Stop an active listener.", "<name>")
listenerMenu.registerCommand("remove", "Remove a listener.", "<name>")

payloadMenu.registerCommand("list", "List available payload types.", "")
payloadMenu.registerCommand("generate", "Generate a payload", "<type> <arch> <listener> <output name>")

homeMenu.registerCommand("listeners", "Manage listeners.", "")
homeMenu.registerCommand("agents", "Manage active agents.", "")
homeMenu.registerCommand("payloads", "Generate payloads.", "")

agentsMenu.uCommands()
listenerMenu.uCommands()
payloadMenu.uCommands()
homeMenu.uCommands()

AgentsCommands = agentsMenu.Commands
ListenersCommands = listenerMenu.Commands
PayloadsCommands = payloadMenu.Commands
homeCommands = homeMenu.Commands
