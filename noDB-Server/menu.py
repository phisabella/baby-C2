from collections import OrderedDict
from os import system, error

import readline

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


def evHome(command, args):
    if command == "help":
        homeMenu.showHelp()
    elif command == "lista":
        viewAgents()
    elif command == "removea":
        removeAgent(args)
    elif command == "interact":
        interactWithAgent(args)
    elif command == "listl":
        listenerHelper.viewListeners()
    elif command == "start":
        listenerHelper.startListener(args)
    elif command == "stop":
        listenerHelper.stopListener(args)
    elif command == "removel":
        listenerHelper.removeListener(args)
    elif command == "listp":
        viewPayloads()
    elif command == "generate":
        generatePayload(args)
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
            print("diaoi yong ing")


def Exit():
    listenerHelper.saveListeners()
    exit()


homeMenu = Menu("server")


homeMenu.registerCommand("renamea", "Rename agent.", "<agent> <new name>")
homeMenu.registerCommand("removea", "Remove an agent.", "<name>")
homeMenu.registerCommand("lista", "List active agents.", "")
homeMenu.registerCommand("listl", "List active listeners.", "")
homeMenu.registerCommand("listp", "List available payload types.", "")
homeMenu.registerCommand("start", "Start a listener.", "<name> <port> <interface> | <name>")
homeMenu.registerCommand("stopl", "Stop an active listener.", "<name>")
homeMenu.registerCommand("removel", "Remove a listener.", "<name>")
homeMenu.registerCommand("generate", "Generate a payload", "<type> <arch> <listener> <output name>")
homeMenu.registerCommand("help", "Show helps", "")
homeMenu.registerCommand("exit", "Save and Exit", "")
homeMenu.uCommands()

homeCommands = homeMenu.Commands
