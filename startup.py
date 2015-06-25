#!/usr/bin/env python
import os, sys, time, random, pygame, glob, subprocess, threading, signal
from Gui import Menu, Label
from Moonlight import Moonlight
from pygame.locals import *

def signalHandler(signal, frame):
	Startup.thread.stop()
	sys.exit(0)

class QuitThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.active = True
		self.joy = None
		self.running = True
	def setActive(self, active):
		self.active = active
	def stop(self):
		self.running = False
	def run(self):
		print "Quit thread starting"
		if not pygame.joystick.get_init():
			pygame.joystick.init()
		if pygame.joystick.get_count() > 0:
			self.joy = pygame.joystick.Joystick(0)
			if not self.joy.get_init():
				self.joy.init()
		else:
			return 0

		print "Quit thread running"
		while self.running:
			if self.active:
				if self.joy.get_button(4) and self.joy.get_button(5) and self.joy.get_button(6):
					print("Force stream quit!")
					Startup.menu.msg("Stopping stream")
					Startup.moonlight.quit()
				time.sleep(0.25)

class Startup:
	def __init__(self):
		self.screen = None
		self.menu = None
		self.moonlight = None
		self.loaded = 0

	def main(self):
		# Initialize Startup
		if len(sys.argv) != 2:
			print("Correct usage: startup.py <ip address> or startup.py map")
			sys.exit(1)

		# Set working directory
		os.chdir(os.path.dirname(os.path.realpath(__file__)))

		# Set driver, fix problems on certain devices
		drivers = ['fbcon', 'directfb', 'svgalib']
		found = False
		for driver in drivers:
			if not os.getenv('SDL_VIDEODRIVER'):
				os.putenv('SDL_VIDEODRIVER', driver)
			try:
				pygame.display.init()
				print("Using {0} as video driver".format(driver))
			except pygame.error:
				continue
			found = True
			break

		if not found:
			print("Suitable video driver not found!")
			sys.exit(2)

		# Initialize PyGame
		print("Initializing PyGame")
		pygame.init()
		pygame.font.init()
		pygame.display.init()
		self.screen = pygame.display.set_mode((pygame.display.Info().current_w,pygame.display.Info().current_h), pygame.FULLSCREEN)
		self.screen.fill((0, 0, 0))  
		pygame.display.update()

		# Initialize other stuff
		print("Initializing moonlight")
		self.moonlight = Moonlight(sys.argv[1])
		self.moonlight.loadConfig()

		print("Initializing menu")
		self.menu = Menu(self,self.screen)

		if sys.argv[1] == "map":
			self.loadMapping()
		else:
			self.thread = QuitThread()
			self.thread.start()
			self.loadMainMenu()

	def loadMainMenu(self):
		self.loaded = 1
		items = [Label(i) for i in ["Stream","Settings","Exit","Shutdown"]]
		out = self.menu.menu(items,title=Label("Main Menu"),desc=Label("Welcome to pyMoonLight Alpha 1.0"))
		if out == 0:
			self.loadStream()
		elif out == 1:
			self.loadSettings()
		elif out == 2:
			self.thread.stop()
			sys.exit(0)
		elif out == 3:
			os.system("halt")

	def loadMapping(self,loadMainMenu=False):
		proc = self.moonlight.execute(["map","mapping.map"],False)
		while True:
			line = proc.stdout.readline()
			if line == '':
				break
			self.menu.msg(line.rstrip())
		if loadMainMenu:
			self.loadMainMenu()

	def loadPair(self):
		self.loaded = 2
		self.menu.msg("Pairing with PC",desc="Please wait")
		proc = self.moonlight.execute(["pair"])
		while True:
			line = proc.stdout.readline()
			if line == '':
				break
			if "PIN on the target PC" in line:
				self.menu.msg(str(line.rstrip()[-4:]),desc="Enter above PIN on PC")
		proc.wait()

	def loadStream(self):
		self.loaded = 3
		self.menu.msg("Getting game list")
	 	gList = self.moonlight.listGames()
	 	if gList == -1:
	 		self.loadPair()
	 		self.loadMainMenu()

		games = [Label(i) for i in gList]
		games.append(Label("Back",0))
		out = self.menu.menu(games,title=Label("Games"),desc=Label("You can force quit stream at any time by holding LB+RB+Back"))
		if out != -1:
			game = games[out]
			if game.getUserData() == 0:
				self.loadMainMenu()
			else:
				self.menu.setColors(bg=[0,0,0])
				self.menu.msg("Stream starting")
				proc = self.moonlight.stream(game.getText().split(". ")[1].rstrip())
				while True:
					line = proc.stdout.readline()
					if line == '':
						break
					self.menu.msg("Stream starting",desc=line.rstrip())
				self.menu.msg("Please wait",desc="Waiting for process to end")
				proc.wait()
				self.menu.setColors()
				self.loadMainMenu()

	def loadSettings(self):
		self.loaded = 4
		# Create Settings menu items
		items = [Label(i) for i in ["Resolution", "Framerate","Bitrate","Packetsize","Local audio","Force quit stream","Map gamepad","Back"]]
		cfg = self.moonlight.getConfig()
		if "width" in cfg: 
			if "height" in cfg: 
				items[0].setDesc("{0}x{1}".format(cfg["width"],cfg["height"]))
		if "framerate" in cfg: 
			items[1].setDesc("{0}FPS".format(cfg["framerate"]))
		if "bitrate" in cfg: 
			items[2].setDesc("{0}Kbps".format(cfg["bitrate"]))
		if "packetsize" in cfg:
			items[3].setDesc("{0}b".format(cfg["packetsize"]))
		if "localaudio" in cfg:
			if cfg["localaudio"] == 0:
				items[4].setDesc("Disabled")
			else:
				items[4].setDesc("Enabled")

		# Display settings menu and wait for response
		out = self.menu.menu(items, title=Label("Settings"))
		if out == 0:
			# First, select aspect ratio
			items = [Label(i) for i in ["16:9","16:10","4:3","Cancel"]]
			out = self.menu.menu(items,title=Label("Aspect Ratio"),desc=Label("Select aspect ratio, most common is 16:9"))
			if out == 0:
				aspect = 1.77777777778
			elif out == 1:
				aspect = 1.6
			elif out == 2:
				aspect = 1.33333333333
			elif out == 3:
				self.loadSettings()

			# Select resolution
			items = [Label(i) for i in ["360p","540p","720p","1080p","1440p","2160p","Cancel"]]
			out = self.menu.menu(items,title=Label("Resolution"),desc=Label("Select stream resolution, 720p is recommended for WiFi and 1080p for LAN"))
			if out == 0:
				self.moonlight.config["width"] = int(aspect*360)
				self.moonlight.config["height"] = 360
			elif out == 1:
				self.moonlight.config["width"] = int(aspect*540)
				self.moonlight.config["height"] = 540
			elif out == 2:
				self.moonlight.config["width"] = int(aspect*720)
				self.moonlight.config["height"] = 720
			elif out == 3:
				self.moonlight.config["width"] = int(aspect*1080)
				self.moonlight.config["height"] = 1080
			elif out == 4:
				self.moonlight.config["width"] = int(aspect*1440)
				self.moonlight.config["height"] = 1440
			elif out == 5:
				self.moonlight.config["width"] = int(aspect*2160)
				self.moonlight.config["height"] = 2160
			if out != -1:
				self.moonlight.saveConfig()
				self.loadSettings()
		elif out == 1:
			items = [Label(i) for i in ["30FPS","60FPS","Cancel"]]
			out = self.menu.menu(items,title=Label("Framerate"),desc=Label("60FPS is recommended only for high speed LAN"))
			if out == 0:
				self.moonlight.config["framerate"] = 30
			elif out == 1:
				self.moonlight.config["framerate"] = 60
			if out != -1:
				self.moonlight.saveConfig()
				self.loadSettings()
		elif out == 2:
			items = [Label(i) for i in ["2Mbps","4Mbps","6Mbps","8Mbps","10Mbps","12Mbps","Cancel"]]
			out = self.menu.menu(items,title=Label("Bitrate"),desc=Label("Higer the bitrate, better the quality. Default is 8Mbps, lower it if you experiencing FPS drops"))
			if out == 0:
				self.moonlight.config["bitrate"] = 2000
			elif out == 1:
				self.moonlight.config["bitrate"] = 4000
			elif out == 2:
				self.moonlight.config["bitrate"] = 6000
			elif out == 3:
				self.moonlight.config["bitrate"] = 8000
			elif out == 4:
				self.moonlight.config["bitrate"] = 10000
			elif out == 5:
				self.moonlight.config["bitrate"] = 12000
			if out != -1:
				self.moonlight.saveConfig()
				self.loadSettings()
		elif out == 3:
			items = [Label(i) for i in ["512","1024","2048"]]
			out = self.menu.menu(items,title=Label("Packet Size"),desc=Label("Default is 1024"))
			if out == 0:
				self.moonlight.config["packetsize"] = 512
			elif out == 1:
				self.moonlight.config["packetsize"] = 1024
			elif out == 2:
				self.moonlight.config["packetsize"] = 2048
			if out != -1:
				self.moonlight.saveConfig()
				self.loadSettings()
		elif out == 4:
			items = [Label(i) for i in ["Enabled","Disabled"]]
			out = self.menu.menu(items,title=Label("Local audio"),desc=Label("If enabled, audio will play on target, not here."))
			if out == 0:
				self.moonlight.config["localaudio"] = 1
			elif out == 1:
				self.moonlight.config["localaudio"] = 0
			if out != -1:
				self.moonlight.saveConfig()
				self.loadSettings()
		elif out == 5:
			self.menu.msg("Quittting all games")
			self.moonlight.quit()
			self.loadSettings()
		elif out == 6:
			self.loadMapping(True)
		elif out == 7:
			self.loadMainMenu()

if __name__ == "__main__":
	Startup = Startup()
	signal.signal(signal.SIGINT, signalHandler)
	Startup.main()