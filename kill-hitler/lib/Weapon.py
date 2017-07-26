import math
import pygame as pg
from pygame.locals import *
import random

def hitscan(dist):
	#returns the damage done by a shot
	rand = random.randint(0,255)
	if dist < 2:
		return int(rand / 4)
	elif 2 < dist < 4:
		return int(rand / 6)
	elif 4 < dist and (rand/12) > dist:
		return int(rand / 6)
	elif 4 < dist and (rand/12) < dist:
		return 0

class Weapon:

	def __init__(self,name,sprites,rest_sprite,firing_sprites,ammo,hitscan=True):
		self.name = name
		self.sprites = sprites
		self.rest_sprite = rest_sprite
		self.firing_sprites = firing_sprites 	#sprites where the gun is fired
		self.hitscan = hitscan					#whether or not it uses hitscan to check for hits
		self.ammo = ammo						#a mutable int class that holds ammo

		self.firing = False

	def get_name(self):
		return self.name

	def set_ammo(self,n):
		self.ammo = n

	def get_ammo(self,n):
		return self.ammo

class Knife(Weapon):

	def __init__(self,overlay):
		#overlay required once to convert all sprites for it

		self.screenW,self.screenH = overlay.get_size()

		self.sprites = [pg.transform.scale(pg.image.load("res/wep/knife"+str(n)+".png"),(int(2*self.screenH/3),int(2*self.screenH/3))) for n in range(5)]

		for s in self.sprites:
			s.set_colorkey(s.get_at((0,0)))
			s = s.convert(overlay)
		
		self.lock = 0
		self.frame = 0
		self.firing_sprite = 2
		self.rest_sprite = 4

		self.sound = pg.mixer.Sound("res/snd/Knife.wav")

	def tick(self,firing):
		if firing:
			if self.lock == 0:
				self.lock = 2
				self.sound.play()
		elif self.lock == 1:
			self.lock = 0

		if self.lock == 2:
			self.frame += 0.25
			if self.frame == len(self.sprites):
				self.frame = 0
				self.lock = 1

		if self.frame == self.firing_sprite:
			return True

		return False

	def deal_damage(self,dist):
		if dist <= 1:
			return hitscan(dist)
		else:	
			return 0

	def get_sprite(self):
		if self.lock == 2:
			return self.sprites[int(self.frame)]
		elif self.lock in [1,0]:
			return self.sprites[self.rest_sprite]

class Pistol(Weapon):

	def __init__(self,overlay):
		self.screenW, self.screenH = overlay.get_size()

		self.sprites = [pg.transform.scale(pg.image.load("res/wep/pistol"+str(n)+".png"),(int(2*self.screenH/3),int(2*self.screenH/3))) for n in range(5)]

		for s in self.sprites:
			s.set_colorkey(s.get_at((0,0)))
			s = s.convert(overlay)
		
		self.lock = 0
		self.frame = 0
		self.firing_sprite = 2
		self.rest_sprite = 4

		self.sound = pg.mixer.Sound("res/snd/Pistol.wav")

	def tick(self,firing):
		if firing:
			if self.lock == 0:
				self.lock = 2
				self.sound.play()
		elif self.lock == 1:
			self.lock = 0

		if self.lock == 2:
			self.frame += 0.25
			if self.frame == len(self.sprites):
				self.frame = 0
				self.lock = 1

		if self.frame == self.firing_sprite:
			return True

		return False

	def deal_damage(self,dist):
		return hitscan(dist)

	def get_sprite(self):
		if self.lock == 2:
			return self.sprites[int(self.frame)]
		elif self.lock in [1,0]:
			return self.sprites[self.rest_sprite]

class MachineGun(Weapon):

	def __init__(self,overlay):
		self.screenW,self.screenH = overlay.get_size()

		self.sprites = [pg.transform.scale(pg.image.load("res/wep/machinegun"+str(n)+".png"),(int(2*self.screenH/3),int(2*self.screenH/3))) for n in range(5)]
	
		for s in self.sprites:
			s.set_colorkey(s.get_at((0,0)))
			s = s.convert(overlay)
		
		self.frame = 0
		self.firing_sprite = 1

		self.looping = False

		self.rest_sprite = 4
		self.resting = True

		self.sound = pg.mixer.Sound("res/snd/Machine Gun.wav")

	def tick(self,firing):
		if firing and not self.looping and self.resting:
			self.looping = True
			self.resting = False
		elif not firing and self.looping:
			self.looping = False

		if self.looping:
			self.frame += 0.25
			if self.frame == 3:
				self.frame = 1
		elif not self.resting:
			self.frame += 0.25
			if self.frame == self.rest_sprite:
				self.resting = True
				self.frame = 0

		if self.frame == self.firing_sprite:
			pg.mixer.find_channel().queue(self.sound)
			return True

		return False

	def deal_damage(self,dist):
		return hitscan(dist)

	def get_sprite(self):
		if self.resting:
			return self.sprites[self.rest_sprite]
		else:
			return self.sprites[int(self.frame)]

class ChainGun(Weapon):

	def __init__(self,overlay):
		self.screenW,self.screenH = overlay.get_size()

		self.sprites = [pg.transform.scale(pg.image.load("res/wep/chaingun"+str(n)+".png"),(int(2*self.screenH/3),int(2*self.screenH/3))) for n in range(5)]
	
		for s in self.sprites:
			s.set_colorkey(s.get_at((0,0)))
			s = s.convert(overlay)
		
		self.frame = 0
		self.firing_sprites = [1,2]

		self.looping = False

		self.rest_sprite = 4
		self.resting = True

		self.sound = pg.mixer.Sound("res/snd/Boss Gun.wav")

	def tick(self,firing):
		if firing and not self.looping and self.resting:
			self.looping = True
			self.resting = False
		elif not firing and self.looping:
			self.looping = False

		if self.looping:
			self.frame += 0.25
			if self.frame == 3:
				self.frame = 1
		elif not self.resting:
			self.frame += 0.25
			if self.frame == self.rest_sprite:
				self.resting = True
				self.frame = 0

		if self.frame in self.firing_sprites:
			self.sound.play()
			return True

		return False

	def deal_damage(self,dist):
		return hitscan(dist)

	def get_sprite(self):
		if self.resting:
			return self.sprites[self.rest_sprite]
		else:
			return self.sprites[int(self.frame)]
