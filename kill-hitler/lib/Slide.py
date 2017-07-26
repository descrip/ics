import pygame as pg 
from pygame.locals import *

class Slide:

	def __init__(self,im,frameX,frameY):
		self.im = im
		self.buttons = []
		self.frameX,self.frameY = frameX,frameY
		self.done = False

		self.level = 0
		self.wep = 0

	def tick(self,screen,mouse):
		#called every loop to update screen
		#returns true if it is done and player wants to play the game (through self.done)
		#returns false if it should keep looping
		#self.done will be made true if frameX,y become negative

		screen.blit(self.im,(0,0),(self.frameX,self.frameY,screen.get_width(),screen.get_height()))

		for b in self.buttons:
			if b.collide_point(self.frameX + mouse[0][0],self.frameY + mouse[0][1]):
				rect = b.get_rect()
				rect = pg.Rect(rect[0] - self.frameX,rect[1] - self.frameY,rect[2],rect[3])
				pg.draw.rect(screen,(255,255,255),rect,2)
				if mouse[1] == 2:
					a = b.press()
					if len(a) == 2:
						self.frameX,self.frameY = a
					elif len(a) == 3:
						self.frameX,self.frameY = a[0]
						if a[1] == "level":
							self.level = a[2]
						elif a[1] == "wep":
							self.wep = a[2]
					break

		if self.frameX < 0 or self.frameY < 0:
			self.done = True

		return (self.done,self.level,self.wep)

	def add_button(self,x,y,w,h,frameX,frameY):
		#creates a button object that will change frame when clicked
		self.buttons.append(Button((x,y,w,h),(frameX,frameY)))

	def add_var_button(self,x,y,w,h,frameX,frameY,var,value):
		#creates a button object that will change variable when clicked
		self.buttons.append(Var_Button((x,y,w,h),(frameX,frameY),var,value))

	def add_buttons(self,b):
		self.buttons += b
	
class Button:

	def __init__(self,rect,go_to_pos):
		self.rect = rect
		self.go_to_pos = go_to_pos	#position for camera

	def collide_point(self,x,y):
		if self.rect.collidepoint((x,y)):
			return True
		else:
			return False

	def get_rect(self):
		return self.rect

	def press(self):
		return self.go_to_pos

class Var_Button(Button):

	def __init__(self,rect,go_to_pos,var,value):
		super().__init__(rect,go_to_pos)
		self.var = var
		self.value = value

	def press(self):
		return (self.go_to_pos,self.var,self.value)