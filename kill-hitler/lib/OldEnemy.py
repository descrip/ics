'''
class Enemy_Core:
	#class for enemy objects to take resources from
	#such as sprites
	#so that multiple copies wont be created

	def __init__(self):
		self.sprite_dict = {}
		self.str_sprite_dict = {}
			
	def get_sprites(self,key):
		return self.sprite_dict[key]

	def get_sprite_dict(self):
		return self.sprite_dict

	def load_sprites(self,key,value):
		self.sprite_dict[key] = value

	def pack_sprites(self):
		for key,value in self.sprite_dict.items():
			self.str_sprite_dict[key] = {}
			for key2,value2 in value.items():
				self.str_sprite_dict[key][key2] = [[pg.image.tostring(n,"RGBA") for n in m] for m in value2]

	def unpack_sprites(self):
		for key,value in self.str_sprite_dict.items():
			self.sprite_dict[key] = {}
			for key2,value2 in value.items():
				self.sprite_dict[key][key2] = [[pg.image.fromstring(n,(1,64),"RGBA") for n in m] for m in value2]

	def convert_sprites(self):
		for key,value in self.sprite_dict.items():
			colorkey = self.sprite_dict[key]["still"][0][0].get_at((0,0))
			#print(colorkey)
			for key2,value2 in value.items():
				for m in value2:
					for n in m:
						n = n.set_colorkey(colorkey)
			for key2,value2 in value.items():
				self.sprite_dict[key][key2] = [[n.convert() for n in m] for m in value2]

class Enemy:

	def __init__(self,core,key,posX,posY,dirX,dirY,moveSpeed,level):
		self.posX,self.posY = posX,posY
		self.dirX,self.dirY = dirX,dirY

		temp = 1 / math.sqrt(2)
		self.poss_dir = [(0,-1),(-temp,-temp),(-1,0),(-temp,temp),
			(0,1),(temp,temp),(1,0),(temp,-temp)]
		self.poss_dir_ang = [math.atan2(n[1],n[0]) for n in self.poss_dir]
		
		self.poss_dir_frame = [n for n in range(8)]
		self.dir_frame = 0
		
		#self.sprites = core.get_sprites(key)
		#self.current_sprite = None

		self.key = key

		self.moveSpeed = moveSpeed
		self.level = level

		self.state = "still"

		#frame numbers for animations
		self.move_num = -1
		self.attack_num = -1
		self.death_num = -1

		#counter for when to attack after moving
		self.attack_next = 0
		#when it is equal to 12 enemy attacks
		#still updates until to 16, then it will stop

		self.rect = (posX-0.5,posY-0.5,1,1)

	def move(self,moveDirX,moveDirY,try_again=True):
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
			self.move_num = (self.move_num + 0.2) % 4
			self.state = "move" + str(int(self.move_num))
			self.attack_next += 0.25
		elif try_again:
			#try just X and Y values
			#but prevent it from checking just x and y values
			self.move(moveDirX,0,False)
			self.move(0,moveDirY,False)

	def turn_towards(self,playerPosX,playerPosY,playerDirX,playerDirY):
		#calculating dir needed to move enemy to player
		diffDirX,diffDirY = playerPosX - self.posX,playerPosY - self.posY 	#difference dir vector
		#distPlayer = math.sqrt(diffDirX**2 + diffDirY**2) 					#distance to player
		#exactDirX,exactDirY = diffDirX / distPlayer,diffDirY / distPlayer 	#normalize difference dir vector

		# #matched to the closest dir in self.poss_dir by angle
		# curr_dir_ang = math.atan2(diffDirY,diffDirX)
		# closest_dir = (0,0)
		# closest_ang_dist = 999
		# closest_dir_frame = 0

		# for a in range(len(self.poss_dir_ang)):
		# 	if abs(self.poss_dir_ang[a] - curr_dir_ang) < closest_ang_dist:
		# 		closest_dir = self.poss_dir[a]
		# 		closest_ang_dist = abs(self.poss_dir_ang[a] - curr_dir_ang)
		# 		closest_dir_frame = a

		# self.dirX,self.dirY = closest_dir
		# self.dir_frame = 0

		self.dirX,self.dirY = diffDirX,diffDirY

	def tick(self,playerPosX,playerPosY,playerDirX,playerDirY,playerRect):
		#called every loop
		#returns true if enemy attacks, false if not

		if self.attack_next >= 12:
			self.attack()
			return True
		elif playerRect[0] <= self.posX <= playerRect[0] + playerRect[2] and playerRect[1] <= self.posY <= playerRect[1] + playerRect[3]:
			self.attack()
			return True
		else:
			self.turn_towards(playerPosX,playerPosY,playerDirX,playerDirY)
			self.move(self.dirX,self.dirY)
			#self.update_current_sprite()

		return False

	def attack(self):
		self.state = "attack"
		self.attack_num = (self.attack_num + 0.25) % 4
		if self.attack_next == 24:
			self.attack_next = 0
		elif 12 <= self.attack_next:
			self.attack_next += 0.25

	def get_sprite(self):
		#gives the current sprite of the enemy
		if self.state == "attack":
			return (self.posX,self.posY,self.key,self.state,int(self.attack_num))
		elif self.state == "death":
			return (self.posX,self.posY,self.key,self.state,int(self.death_num))
		else:
			return (self.posX,self.posY,self.key,self.state,self.dir_frame)
'''

# class Hitler:

# 	def __init__(self,posX,posY,dirX,dirY,moveSpeed,level):
# 		self.sprites = {}
# 		sprites["priest"] = {
# 			 "move": [load_image(n) for n in glob.glob("res/hitler/priest_move_*.png")],
# 			 "death": [load_image(n) for n in glob.glob("res/hitler/priest_death_*.png")],
# 			 "shoot": [load_image(n) for n in glob.glob("res/hitler/priest_shoot_*.png")]
# 			 }
# 		'''
# 		self.sprites["mech"] = {
# 			"move": [load_image(n) for n in glob.glob("res/hitler/mech_move_*.png")],
# 			"death": [load_image(n) for n in glob.glob("res/hitler/mech_death_*.png")],
# 			"shoot": [load_image(n) for n in glob.glob("res/hitler/mech_shoot_*.png")]
# 			}
# 		self.sprites["hitler"] = {
# 			"move": [load_image(n) for n in glob.glob("res/hitler/hitler_move_*.png")],
# 			"death": [load_image(n) for n in glob.glob("res/hitler/hitler_death_*.png")],
# 			"shoot": [load_image(n) for n in glob.glob("res/hitler/hitler_shoot_*.png")]
# 			}
# 		'''

# 		self.posX,self.posY = posX,posY
# 		self.dirX,self.dirY = dirX,dirY
# 		self.moveSpeed = moveSpeed

# 		self.hp = 2000

# 		self.actions = ["move","shoot","death"]
# 		self.action_num = 0

# 		#frame counter for each animation
# 		self.frame = 0

# 		#frames per loop for each of the frame counters
# 		self.fpl = [0.5,0.25,0.25]

# 		self.level = level

# 		self.path = []
# 		self.follow_path = False
# 		self.can_see_player = False

# 		self.player_last_pos = (4,4)

# 		self.suit_breaking = False

# 		self.last_action = None

# 		self.moving_lock = 0

# 	'''
# 	def can_see(self,x,y):
# 		dist = ((x - self.posX)**2 + (y - self.posY)**2)**0.5

# 		rayPosX,rayPosY = self.posX,self.posY	 #position of ray
# 		rayDirX,rayDirY = (x - self.posX),(y - self.posY)	#direction of ray
# 		mapX,mapY = int(rayPosX),int(rayPosY)	#position of ray on map
# 		sideDistX,sideDistY = 0.0,0.0

# 		if rayDirX == 0:
# 			rayDirX = 0.0001
# 		if rayDirY == 0:
# 			rayDirY = 0.0001

# 		deltaDistX = math.sqrt(1 + (rayDirY**2) / (rayDirX**2))
# 		deltaDistY = math.sqrt(1 + (rayDirX**2) / (rayDirY**2)) 
# 		perpWallDist = 0.0

# 		stepX,stepY = 0.0,0.0

# 		hit = False  #whether or not there was a collision with a block
# 		side = "x"	#whether it was a hit on the x side or the y side of a block

# 		if rayDirX < 0:
# 			stepX = -1
# 			sideDistX = (rayPosX - mapX) * deltaDistX
# 		else:
# 			stepX = 1
# 			sideDistX = (mapX + 1.0 - rayPosX) * deltaDistX

# 		if rayDirY < 0:
# 			stepY = -1
# 			sideDistY = (rayPosY - mapY) * deltaDistY
# 		else:
# 			stepY = 1
# 			sideDistY = (mapY + 1.0 - rayPosY) * deltaDistY

# 		while hit == False:
# 			if sideDistX < sideDistY:
# 				sideDistX += deltaDistX
# 				mapX += stepX
# 				side = "x"
# 			else:
# 				sideDistY += deltaDistY
# 				mapY += stepY
# 				side = "y"

# 			if self.level.level[mapY][mapX] >= 1:
# 				hit = True

# 		if side == "x":
# 			perpWallDist = (abs((mapX - rayPosX + (1 - stepX) / 2) / rayDirX))
# 		elif side == "y":
# 			perpWallDist = (abs((mapY - rayPosY + (1 - stepY) / 2) / rayDirY))

# 		if dist < perpWallDist:
# 			return True
# 		else:
# 			return False

# 	def can_see(self,x0,y0,x1,y1):
# 		x0,y0 = int(x0),int(y0)
# 		x1,y1 = int(x1),int(y1)

# 		dx = abs(x0-x1)
# 		dy = abs(y0-y1)

# 		can_see = True

# 		if x0 < x1:
# 			sx = 1
# 		else:
# 			sx = -1

# 		if y0 < y1:
# 			sy = 1
# 		else:
# 			sy = -1

# 		err = dx-dy

# 		while 1:
# 			if x0 == x1 and y0 == y1:
# 				break

# 			e2 = 2*err
# 			if e2 > -dy:
# 				err -= dy
# 				x0 += sx
# 			if e2 < dx:
# 				err += dx
# 				y0 += sy

# 			if self.level.level[y0][x0] >= 1:
# 				can_see = False

# 		return can_see

# 	def tick(self,playerX,playerY,playerRect):
# 		#called every loop to update hitler

# 		self.can_see_player = self.can_see(self.posX,self.posY,playerX,playerY)

# 		if self.suit_breaking:
# 			pass

# 		elif self.path and self.follow_path:

# 			if self.last_action != 0:
# 				self.action_num = 0
# 				self.frame = 0
# 				self.last_action = 0

# 			pathX,pathY = self.path[-1]
# 			self.dirX,self.dirY = pathX - self.posX,pathY - self.posY
# 			self.posX += self.dirX * self.moveSpeed
# 			self.posY += self.dirY * self.moveSpeed
# 			del self.path[-1]

# 			if len(self.path) == 0:
# 				self.player_last_pos = playerX,playerY

# 		elif self.can_see_player == False:
# 			self.path = self.level.a_star_path(round(self.posX),round(self.posY),int(self.player_last_pos[0]),int(self.player_last_pos[1]))
# 			self.follow_path = True

# 		elif self.can_see_player:
# 			if self.last_action != 1:
# 				self.action_num = 1
# 				self.frame = 0
# 				self.follow_path = False
# 				self.player_last_pos = (playerX,playerY)
# 				self.last_action = 1

# 			self.attack()

# 		self.level.add_temp_sprite(self.posX,self.posY,
# 			self.sprites[self.actions[self.action_num]][int(self.frame)],True)

# 		if self.hp == self.suit_break_hp:
# 			self.suit_breaking = True
# 			self.action_num = 2
# 	'''

# 	def tick(playerX,playerY):
# 		self.dirX,self.dirY = self.dirX + 

# 	def attack(self):
# 		self.action_num = 1
# 		self.frame += self.fpl[self.action_num]
# 		if self.frame >= len(self.sprites[self.actions[self.action_num]]):
# 			self.frame = 0

# 	def damage(self,n):
# 		self.hp -= n

# 	def drop(self):
# 		pass

# 	def die(self):
# 		pass