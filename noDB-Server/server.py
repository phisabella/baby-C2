#!/usr/bin/python3
import logging
import os
import sys

from agentsHelper import uagents
from listenerHelper import loadListeners
from menu import home


def main():
    if not os.path.exists("./data/"):
        os.mkdir("./data/")

    if not os.path.exists("./data/listeners/"):
        os.mkdir("./data/listeners/")

    if not os.path.exists("./data/databases/"):
        os.mkdir("./data/databases/")

    log = logging.getLogger('hex')
    log.disabled = True

    loadListeners()
    uagents()

    home()


if __name__ == "__main__":
    main()
