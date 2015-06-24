import pygame, time
from pygame.locals import *

class Label:
	def __init__(self, text, userData=None, font=None, color=None, desc=""):
		self.text = text.rstrip()
		self.desc = desc.rstrip()
		self.descFont = pygame.font.Font("OpenSans-Regular.ttf",18)
		self.x = 0
		self.y = 0
		self.font = font
		self.userData = userData
		self.size = (0,0)
		self.pos = (0,0)
		self.rendered = None
		self.descRender = None
		if self.font == None:
			self.font = pygame.font.Font("OpenSans-Regular.ttf",24)
		self.color = color
		if self.color == None:
			self.color = [255,255,255]

	def getUserData(self):
		return self.userData
	def setPos(self,x,y):
		self.pos = (x,y)
	def setText(self,text):
		self.text = text.rstrip()
	def getSize(self):
		return self.size
	def getText(self):
		return self.text
	def setColor(self, color):
		self.color = color
	def setFont(self, font):
		self.font = font
	def setDesc(self, desc):
		self.desc = desc
	def render(self):
		if self.text != "":
			self.rendered = self.font.render(self.text,True,self.color)
			self.size = (self.rendered.get_width(),self.rendered.get_height())
		if self.desc != "":
			self.descRender = self.descFont.render(self.desc,True,[150,150,150])
			self.size = (self.size[0]+self.descRender.get_width(),self.size[1])
	def blit(self,target):
		if self.text != "" and self.rendered != None:
			target.blit(self.rendered,self.pos)
			if self.descRender != None:
				x = self.pos[0]+self.rendered.get_width()+5
				y = self.pos[1]+(self.size[1]/2)-(self.descRender.get_height()/2)+3
				target.blit(self.descRender,(x,y))
			return True
		return False
	def isHovering(self,posToCheck):
		return posToCheck[0] > self.pos[0] and posToCheck[0] < self.pos[0]+self.size[0] and posToCheck[1] > self.pos[1] and posToCheck[1] < self.pos[1]+self.size[1] 

class Menu:
	def __init__(self, launcher, scr):
		# Initialize values
		self.bg = [51,51,51]
		self.fg1 = [255, 255, 255]
		self.fg2 = [154, 197, 12]
		self.scr = scr
		self.launcher = launcher

		# Initialize fonts
		self.font = pygame.font.Font("OpenSans-Regular.ttf",24)
		self.titleFont = pygame.font.Font("OpenSans-Regular.ttf",52)
		self.descFont = pygame.font.Font("OpenSans-Regular.ttf",16)
		self.clockFont = pygame.font.Font(None,24)

		# Initialize joystick if needed
		self.joy = None
		if pygame.joystick.get_count() > 0:
			if not pygame.joystick.get_init():
				pygame.joystick.init()
			self.joy = pygame.joystick.Joystick(0)
			if not self.joy.get_init():
				self.joy.init()
		else:
			print("No joysticks detected")

	def setColors(self, bg=[51,51,51], fg1=[255, 255, 255], fg2=[154, 197, 12]):
		self.bg = bg
		self.fg1 = fg1
		self.fg2 = fg2

	def msg(self, msg, desc=""):
		self.scr.fill(self.bg)
		renderedMsg = self.titleFont.render(msg,True,self.fg1)
		x = self.scr.get_width()/2 - renderedMsg.get_width()/2
		y = self.scr.get_height()/2 - renderedMsg.get_height()/2
		self.scr.blit(renderedMsg,(x,y))

		if desc != "":
			renderedDesc = self.descFont.render(desc,True,[150,150,150])
			x2 = self.scr.get_width()/2 - renderedDesc.get_width()/2
			y2 = self.scr.get_height()/2 - renderedDesc.get_height()/2 + renderedMsg.get_height()
			self.scr.blit(renderedDesc,(x2,y2))

		pygame.display.update()

	def menu(self, items, title=None, desc=None):
		# Initialize values
		self.items = items
		self.title = title
		self.desc = desc

		if self.title != None:
			self.title.setPos(52,52)
			self.title.setFont(self.titleFont)
		if self.desc != None:
			self.desc.setPos(52,52)
			self.desc.setFont(self.descFont)
			self.desc.setColor([150,150,150])
		for item in self.items:
			item.setFont(self.font)

		# Some useful variables
		selected = 0
		prevaxis = 0
		redraw = True
		updateTimer = time.time()
		parentLoaded = self.launcher.loaded

		# Main loop
		while self.launcher.loaded == parentLoaded:
			#Check for gamepad buttons
			for event in pygame.event.get(JOYBUTTONDOWN): 
				#print("Btn: {0}".format(event.button))
				if event.button == 0:
					return selected
				elif event.button == 14:
					redraw = True
					if selected < len(items)-1:
							selected += 1
					else:
						selected = 0
				elif event.button == 13:
					redraw = True
					if selected > 0:
							selected -= 1
					else:
						selected = len(items)-1
					
			
			#Check for gamepad axis
			for event in pygame.event.get(JOYAXISMOTION):
				if event.axis == 1:
					if event.value < -0.5 and prevaxis >= -0.5:
						redraw = True
						if selected > 0:
							selected -= 1
						else:
							selected = len(items)-1
					elif event.value > 0.5 and prevaxis <= 0.5:
						redraw = True
						if selected < len(items)-1:
							selected += 1
						else:
							selected = 0
					prevaxis = event.value

			#Check for mouse clicks
			for event in pygame.event.get(MOUSEBUTTONDOWN):
				if event.button == 1:
					for i, button in enumerate(items):
						if button.isHovering(event.pos):
							return selected
				elif event.button == 4 and selected > 0:
					redraw = True
					if selected > 0:
						selected -= 1
					else:
						selected = len(items)-1
				elif event.button == 5 and selected < len(items)-1:
					redraw = True
					if selected < len(items)-1:
						selected += 1
					else:
						selected = 0
				elif event.button == 2:
					return selected

			#Check for mouse motion
			for event in pygame.event.get(MOUSEMOTION):
				for i, button in enumerate(items):
					if selected != i and button.isHovering(event.pos):
						selected = i
						redraw = True

			#Redraw entire screen if requested, can be optimized later, but for now its ok
			if redraw:
				self.scr.fill(self.bg)
				topmargin = 52
				if title != None:
					title.render()
					topmargin += title.getSize()[1]
					title.blit(self.scr)
				if desc != None:
					desc.setPos(52,topmargin)
					desc.render()
					topmargin += desc.getSize()[1]
					desc.blit(self.scr)
				for i, button in enumerate(items):
					button.setColor(self.fg2 if i == selected else self.fg1)
					button.render()
					button.setPos(128,(button.getSize()[1]+3)*i+topmargin+20)
					button.blit(self.scr)
				redraw = False

			#Draw only clock if no redraw has been performed
			clock = self.font.render(time.strftime("%H:%M:%S"),True,[100,100,100])
			rect = pygame.Rect(10,self.scr.get_height()-clock.get_height()-10,clock.get_width(),clock.get_height())
			if not redraw:
				pygame.draw.rect(self.scr,self.bg,rect)
			self.scr.blit(clock,(rect.x,rect.y))

			pygame.display.update()
		return -1