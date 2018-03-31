import subprocess, json, os

import pexpect as pexpect


class Moonlight:
    def __init__(self, ip):
        # Configuration
        self.config = {}
        self.app = None
        self.ip = ip

        # Other
        self.executable = "moonlight"
        self.workingdir = "bin"
        self.proc = None

    def loadConfig(self):
        try:
            cfg = json.loads(open("config.txt", "r").read())
            self.config.update(cfg)
        except IOError:
            print("Failed to read config.txt")

    def getConfig(self):
        return self.config

    def saveConfig(self):
        with open("config.txt", "w") as outfile:
            json.dump(self.config, outfile)

    def execute(self, args, includeip=True):
        ar = [self.executable]
        ar += args
        if includeip:
            ar += [self.ip]

        if not os.path.exists(self.workingdir):
            os.makedirs(self.workingdir)

        self.proc = subprocess.Popen(ar, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.workingdir)
        return self.proc

    def pair_pexpect(self):

        if not os.path.exists(self.workingdir):
            os.makedirs(self.workingdir)

        child = pexpect.spawn('{} {}'.format(self.executable, 'pair'), cwd=self.workingdir)
        child.expect('[1-9]{4}')
        return child

    def listGames(self):
        process = self.execute(["list"])
        games = []
        while True:
            line = process.stdout.readline()
            if line == '':
                break
            if "You must pair with the PC first" in line:
                return -1
            else:
                games.append(line.rstrip())
        return games

    def quit(self):
        if self.proc != None:
            self.proc.kill()
        process = self.execute(["quit"])
        process.wait()

    def stream(self, app=None):
        args = ["stream"]
        if os.path.isfile("bin/mapping.map"):
            args.append("-mapping")
            args.append("mapping.map")
        if "width" in self.config:
            args.append("-width")
            args.append(str(self.config["width"]))
        if "height" in self.config:
            args.append("-height")
            args.append(str(self.config["height"]))
        if "framerate" in self.config:
            if self.config["framerate"] == 30:
                args.append("-30fps")
            elif self.config["framerate"] == 60:
                args.append("-60fps")
        if "bitrate" in self.config:
            args.append("-bitrate")
            args.append(str(self.config["bitrate"]))
        if "audio" in self.config:
            args.append("-audio")
            args.append(str(self.config["audio"]))
        if "input" in self.config:
            args.append("-input")
            args.append(str(self.config["input"]))
        if "localaudio" in self.config:
            if self.config["localaudio"] != 0:
                args.append("-localaudio")
        if app:
            args.append("-app")
            args.append(app)

        print("Exec: " + str(args))
        return self.execute(args)

    def setAction(self, action):
        self.action = action

    def setApp(self, app):
        self.app = app
