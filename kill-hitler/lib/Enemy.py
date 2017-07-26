import math
import pygame as pg
from pygame.locals import *
from random import randint,uniform
import glob

def load_image(image, darken = False):
        #load an image
        #applies a color key
        #can darken an image
        #splits it into one-sprite wide surfaces for each vertical line in teh sprite
        #for rendering views
	image = pg.image.load(image)
	ret = []
	colorKey = image.get_at((0,0))
	if darken:
		image.set_alpha(127)
	for i in range(image.get_width()):
		s = pg.Surface((1, image.get_height()))
		#s.fill((0,0,0))
		s.blit(image, (- i, 0))
		s.set_colorkey(colorKey)
		ret.append(s)
	return ret

#sprites for fireball
fireball_sprites  = [load_image(n) for n in glob.glob("res/hitler/fireball_*.png")]

class Fireball:

        #fireball class
        #created everytime hitler shoots one
        #updated in the hitler class

	def __init__(self,posX,posY,dirX,dirY,moveSpeed,level):
		global fireball_sprites
		self.sprites = fireball_sprites

		self.posX,self.posY = posX,posY         #position
		self.dirX,self.dirY = dirX,dirY         #direction vector
		self.moveSpeed = moveSpeed              #movespeed
		self.rect = (posX-0.5,posY-0.5,1,1)     #collision rect

		self.level = level                      #level

		self.frame = 0                          #sprite frame

		self.livetime = 0                       #how long it has lived (loops)

	def tick(self,player,hitler,num):
		self.hitler = hitler
		self.num = num          #the index within hitler's list of fireballs
		#used for deleting the fireball

		self.livetime += 1      #update live time

		self.frame = 1 - self.frame     #toggles which frame (1 or 0)

		self.move(self.dirX,self.dirY)

                #if collision with player, damage the player
		if self.rect[0] <= player.posX <= self.rect[0] + self.rect[2] and self.rect[1] <= player.posY <= self.rect[1] + self.rect[3]:
			player.damage(randint(0,30))
			self.die()      #and delete fireball object

                #if fireball has lived for 200 loops
		if self.livetime == 200:
			self.die()      #kill it

		self.level.add_temp_sprite(self.posX,self.posY,self.sprites[self.frame])

	def move(self,moveDirX,moveDirY):
		#moves the player if there is no collision in where the player is about to be (a priori)

		#whether or not there is a collision in where the player is about to move
		collide = False

		#the collide rect if the player moved
		poss_rect = (self.posX + moveDirX * self.moveSpeed - 0.5,self.posY + moveDirY * self.moveSpeed - 0.5,1,1)

		#points of the new possible collide rect
		rect_points = [
		(poss_rect[0],poss_rect[1]),
		(poss_rect[0]+poss_rect[2],poss_rect[1]),
		(poss_rect[0],poss_rect[1]+poss_rect[3]),
		(poss_rect[0]+poss_rect[2],poss_rect[1]+poss_rect[3])
		]

		#blocks that the collide rect is over
		colliding_blocks = [(int(n[0]),int(n[1])) for n in rect_points]

		#check for walls on the blocks that the collide rect is over
		for i in colliding_blocks:
			if self.level.check_wall_col(i[0],i[1]):
				collide = True
				break

		if not collide:	 #no collison
			#move the player
			self.posX += moveDirX * self.moveSpeed
			self.posY += moveDirY * self.moveSpeed
			self.rect = poss_rect
		else:
			self.die()

	def die(self):
                #function to kill fireball
                #by calling hitler object to delete it
		self.hitler.kill_fireball(self.num)

class Hitler:

        #hitler enemy class

	def __init__(self,posX,posY,dirX,dirY,moveSpeed,level):

                #sprite dictionary
		self.sprites = {
			"move": [load_image(n) for n in glob.glob("res/hitler/priest_move_*.png")],
			"death": [load_image(n) for n in glob.glob("res/hitler/priest_death_*.png")]
			}

		self.posX,self.posY = posX,posY #position
		self.dirX,self.dirY = dirX,dirY #direction vectore
		self.moveSpeed = moveSpeed      #move speed

		self.lastPosX,self.lastPosY = 0,0       #last position (from last loop)

                #level object
		self.level = level
		self.levelW,self.levelH = self.level.get_size()

                #frame state
		self.state = "move"
		self.frame = 0  #frame number

		self.hp = 1000  #health

		self.can_see_player = False
		self.first_see = True   #has seen the player for the first time

                #fireball list
		self.fireballs = []
		#list of indexes of self.fireballs of fireballs that requested death
		self.fireballs_to_kill = []

                #shooting cooldowns
		self.cooldown = 10
		self.cooldown2 = 0
		self.is_cooldown2 = False

                #sounds
		self.gutentag = pg.mixer.Sound("res/snd/Guten Tag!.wav")
		self.pain = pg.mixer.Sound("res/snd/Enemy Pain.wav")

	def tick(self,player,game):
                #update hitler

                #get player position
		playerX,playerY = player.posX,player.posY

                #move hitler
		self.move()

		if self.hp <= 0:
                        #win the game for the player
			game.win(self.posX,self.posY,self.sprites["death"])

                #check if hitler can see player
		self.can_see_player = self.can_see(self.posX,self.posY,playerX,playerY)
		if self.can_see_player:
			self.attack(playerX,playerY)    #attack
			if self.first_see:
                                #say hello
				self.gutentag.play()
				self.first_see = False

                #update fireballs
		for f in range(len(self.fireballs)):
			self.fireballs[f].tick(player,self,f)

                #kill fireballs
		self.fireballs_to_kill.sort(reverse = True)
		for f in self.fireballs_to_kill:
			try:
				del self.fireballs[f]
			except:
				pass

                #empty fireball kill list
		self.fireballs_to_kill = []

                #add a temporary sprite of hitler in the level
		self.level.add_temp_sprite(self.posX,self.posY,self.sprites[self.state][self.frame],True)

	def move(self):
                #move hitler randomly
                
		self.lastPosX,self.lastPosY = self.posX,self.posY
		#get new random direction vector
		self.dirX,self.dirY = self.dirX + uniform(-0.3,0.3),self.dirY + uniform(-0.3,0.3)
		#normalise new direction vector
		dirDist = math.sqrt(self.dirX**2 + self.dirY**2)
		self.dirX /= dirDist
		self.dirY /= dirDist

                #an move it provided that the destination is within the level
		#meaning it is allowed to collide through walls
		if 2 <= self.posX + self.dirX * self.moveSpeed <= self.levelW - 2:
			self.posX += self.dirX * self.moveSpeed
		if 2 <= self.posY + self.dirY * self.moveSpeed <= self.levelH - 2:
			self.posY += self.dirY * self.moveSpeed

                #if lastpos equals curerent poistion, meaning it didnt move
                #get inverse random vector
		if self.lastPosX == self.posX or self.lastPosY == self.posY:
			self.dirX = -self.dirX + uniform(-0.3,0.3)
			self.dirY = -self.dirY + uniform(-0.3,0.3)

	def attack(self,playerX,playerY):
                #attack the player if hitler can see him/her

                #there is a cooldown
                #self.cooldown handles fireball between fireball (does not allow hitler to shoot fireballs every loop)
                #self.cooldown2 handles fireball shooting lengths, allows hitler to shoot five and then forces him to wait 5 seconds
                #before he can shoot more

                #if not coolingdown
		if self.cooldown == 0 and not self.is_cooldown2:
			self.is_cooldown2 = False
			
			#get direction vector between enemy and player 
			fireX,fireY = playerX - self.posX,playerY - self.posY   

                        #stages of hitler based on health
			if self.hp >= 1500:
                                #shoot only one fireball at the player
				self.fireballs.append(Fireball(self.posX,self.posY,fireX,fireY,0.1,self.level))
			elif 1500 <= self.hp <= 100:
                                #shoot one at player one in opposite direction
				self.fireballs.extend([
				Fireball(self.posX,self.posY,fireX,fireY,0.1,self.level),
				Fireball(self.posX,self.posY,-fireX,-fireY,0.1,self.level),
				])
			else:
                                #shoot one at player, one opposite, two perpendicular to the previous two
				self.fireballs.extend([
				Fireball(self.posX,self.posY,fireX,fireY,0.1,self.level),
				Fireball(self.posX,self.posY,self.dirY,-self.dirX,0.1,self.level),
				Fireball(self.posX,self.posY,-fireX,-fireY,0.1,self.level),
				Fireball(self.posX,self.posY,-self.dirX,self.dirY,0.1,self.level),
				])

			self.cooldown = 10
			self.cooldown2 += 10
		else:
                        #cooldown handling
			if self.is_cooldown2:
				self.cooldown2 -= 1

				if self.cooldown2 <= 0:
					self.is_cooldown2 = False
					self.cooldown2 = 0

			else:
				self.cooldown -= 1

				if self.cooldown2 >= 50:
					self.cooldown = 0
					self.is_cooldown2 = True

	def kill_fireball(self,num):
                #kill fireball function
                #append it to the kill list
                #will be handled next self.tick()
		self.fireballs_to_kill.append(num)

	def damage(self,n):
                #damage hitler
		self.hp -= n
		self.pain.play()        #play hurt sound

	def can_see(self,x0,y0,x1,y1):
                #can hitler see the player?
                #uses bresenham's line algorithm, and checks every block that a line from hitler to player hits
                #and if there are any walls at the blocks between hitler and player

                #http://en.wikipedia.org/wiki/Bresenham's_line_algorithm

                #line start, end positions
		x0,y0 = int(x0),int(y0)
		x1,y1 = int(x1),int(y1)

		dx = abs(x0-x1)
		dy = abs(y0-y1)

		can_see = True

		if x0 < x1:
			sx = 1
		else:
			sx = -1

		if y0 < y1:
			sy = 1
		else:
			sy = -1

		err = dx-dy

		while 1:
			if x0 == x1 and y0 == y1:
				break

			e2 = 2*err
			if e2 > -dy:
				err -= dy
				x0 += sx
			if e2 < dx:
				err += dx
				y0 += sy

			if self.level.level[y0][x0] >= 1:
				can_see = False

		return can_see

class Hitler2:

	def __init__(self,posX,posY,dirX,dirY,moveSpeed,level):

		self.sprites = {
			"move": [load_image(n) for n in glob.glob("res/hitler/mech_move_*.png")],
			"shoot": [load_image(n) for n in glob.glob("res/hitler/mech_shoot_*.png")],
			"death": [load_image(n) for n in glob.glob("res/hitler/mech_death_*.png")]
			}

		self.posX,self.posY = posX,posY
		self.dirX,self.dirY = dirX,dirY
		self.moveSpeed = moveSpeed

		self.lastPosX,self.lastPosY = 0,0

		self.level = level
		self.levelW,self.levelH = self.level.get_size()

		self.state = "move"
		self.frame = 0

		self.hp = 2000

		self.can_see_player = False

		self.cooldown = 10
		self.cooldown2 = 0
		self.is_cooldown2 = False

	def tick(self,player,game):

		playerX,playerY = player.posX,player.posY

		self.move()

		self.can_see_player = self.can_see(self.posX,self.posY,playerX,playerY)
		if self.can_see_player:
			self.attack(playerX,playerY)

		for f in range(len(self.fireballs)):
			self.fireballs[f].tick(player,self,f)

		self.fireballs_to_kill.sort(reverse = True)
		for f in self.fireballs_to_kill:
			del self.fireballs[f]
		self.fireballs_to_kill = []

		self.level.add_temp_sprite(self.posX,self.posY,self.sprites[self.state][self.frame],True)

		if self.hp <= 0:
			game.win()

	def move(self):
		if self.posX < self.path[-1][0]:
			self.posX += self.moveSpeed
		elif self.posX > self.path[-1][0]:
			self.posX -= self.moveSpeed

		if self.posY < self.path[-1][1]:
			self.posY += self.moveSpeed
		elif self.posY > self.path[-1][1]:
			self.posY -= self.moveSpeed

		z = (self.posX - self.path[-1][0], self.posY - self.path[-1][1])

		if (z[0] / -self.moveSpeed,z[1] / -self.moveSpeed) == (0,0):
			self.path = self.path[:-1]

	def attack(self,playerX,playerY):
		if self.cooldown == 0 and not self.is_cooldown2:
			self.is_cooldown2 = False
			fireX,fireY = playerX - self.posX,playerY - self.posY

			self.fireballs.extend([
				Fireball(self.posX,self.posY,fireX,fireY,0.1,self.level),
				Fireball(self.posX,self.posY,self.dirY,-self.dirX,0.1,self.level),
				Fireball(self.posX,self.posY,-fireX,-fireY,0.1,self.level),
				Fireball(self.posX,self.posY,-self.dirX,self.dirY,0.1,self.level),
				])

			self.cooldown = 10
			self.cooldown2 += 10
		else:
			if self.is_cooldown2:
				self.cooldown2 -= 1

				if self.cooldown2 <= 0:
					self.is_cooldown2 = False
					self.cooldown2 = 0

			else:
				self.cooldown -= 1
				
				if self.cooldown2 >= 100:
					self.cooldown = 0
					self.is_cooldown2 = True

	def damage(self,n):
		self.hp -= n

	def can_see(self,x0,y0,x1,y1):
		x0,y0 = int(x0),int(y0)
		x1,y1 = int(x1),int(y1)

		dx = abs(x0-x1)
		dy = abs(y0-y1)

		can_see = True

		if x0 < x1:
			sx = 1
		else:
			sx = -1

		if y0 < y1:
			sy = 1
		else:
			sy = -1

		err = dx-dy

		while 1:
			if x0 == x1 and y0 == y1:
				break

			e2 = 2*err
			if e2 > -dy:
				err -= dy
				x0 += sx
			if e2 < dx:
				err += dx
				y0 += sy

			if self.level.level[y0][x0] >= 1:
				can_see = False

		return can_see
