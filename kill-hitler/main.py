import math
import pygame as pg
from pygame.locals import *
import random
import pickle
import sys
import os

from lib.Level import Level
from lib.Enemy import *
from lib.Weapon import *
from lib.Slide import *

def restart_program():
    #function to restart game
    python = sys.executable
    os.execl(python,python,* sys.argv)

restart = True

class Game:

    #main game class
    #contains all other classes
    #instance created and run by running this file

    def __init__(self,screenW,screenH):
        pg.mixer.init(frequency=22050,size=-16,channels=4,buffer=512)

        #fonts
        pg.font.init()
        self.fpsfont = pg.font.Font(None,18)
        self.timerfont = pg.font.Font(None,24)

        self.screen = pg.display.set_mode((screenW,screenH))
        self.running = True
        self.screenW = screenW
        self.screenH = screenH

        self.keys = [0 for i in range(256)]
        self.mouse = [(0,0),0,0,0,0,0,0]

        #load pickled level files
        self.levels = [
            pickle.load(open("res/level/square.level",'rb')),
            pickle.load(open("res/level/block.level",'rb')),
            pickle.load(open("res/level/simple.level",'rb'))
            ]
        self.level_num =   0    #which level the player chooses

        #ready each level
        for i in self.levels:
            i.unpack_tex()
            i.convert_tex()

        #background image, blitted on each render view
        self.background = pg.image.load("res/background.png") 

        self.clock = pg.time.Clock() 

        #can player see hitler
        self.can_see_hitler = True

        self.aim = False    #whether or not the player is aiming at hitler

        #if on the slide object (title screens)
        self.on_slide = True

        #create slide object and add buttons
        self.slide = Slide(pg.image.load("res/panorama.png"),640,960)
        self.slide.add_buttons([
            Button(pg.Rect(640+379,960+173,137,55),(640,480)),    #title screen play button, goes to wep select
            Button(pg.Rect(640+270,960+267,349,55),(0,960)),       #title screen instruction button
            Button(pg.Rect(640+345,960+365,202,55),(1280,960)),    #title screen credits button
            Button(pg.Rect(276,1384,97,43),(640,960)),      #how to play button back to title
            Button(pg.Rect(1548,1372,97,43),(640,960)),     #credits back button to title 
            #buttons for weapon choice
            Var_Button(pg.Rect(725,565,192,192),(0,0),"wep",3),         #chain gun
            Var_Button(pg.Rect(1002,565,192,192),(0,0),"wep",2),        #machine gun
            Var_Button(pg.Rect(725,763,192,192),(0,0),"wep",1),         #pistol
            Var_Button(pg.Rect(1002,763,192,192),(0,0),"wep",0),        #knife
            #buttons for level choice
            Var_Button(pg.Rect(58,188,110,145),(-1,-1),"level",0),        #square
            Var_Button(pg.Rect(266,196,106,119),(-1,-1),"level",1),       #blocks
            Var_Button(pg.Rect(496,207,66,98),(-1,-1),"level",2)          #simple
            ])
    
    def event_loop(self):
        for e in pg.event.get():
            if e.type == QUIT:
                self.running = False
                self.on_slide = False
            elif e.type == MOUSEBUTTONDOWN:
                if self.mouse[e.button] == 0:
                    self.mouse[e.button] = 2
                    #mouse - 2 means just clicked
                    #after one loop of 2the button will become 1 if player is holding the button
                    #0 is player releasing
                    self.mouse[0] = e.pos
            elif e.type == MOUSEBUTTONUP:
                self.mouse[e.button] = 0
                self.mouse[0] = e.pos
            elif e.type == MOUSEMOTION:
                self.mouse[0] = e.pos
            elif e.type == KEYDOWN:
                self.keys[e.key % 255] = 1
            elif e.type == KEYUP:
                self.keys[e.key % 255] = 0

    def run(self):
        #menu music
        pg.mixer.music.load("res/music/menu.wav")
        pg.mixer.music.play(loops = -1)

        #first update through the slide object
        while self.on_slide:
            self.event_loop()

            #tick slide
            ret = self.slide.tick(self.screen,self.mouse)

            #if slide is done and player wants to play
            if ret[0] == True:
                #get level, weapon
                self.on_slide = False
                self.level_num = ret[1]
                self.level = self.levels[self.level_num]

                if self.level_num == 0:
                    self.player = Player(self.level,12,3,-1,0,0,0.66,0.2,5,self.screenW,self.screenH)
                elif self.level_num == 1:
                    self.player = Player(self.level,8,17,-1,0,0,0.66,0.2,5,self.screenW,self.screenH)
                elif self.level_num == 2:
                    self.player = Player(self.level,12,12,-1,0,0,0.66,0.2,5,self.screenW,self.screenH)

                self.hitler = Hitler(2,2,-1,0,0.05,self.level)  
                self.player.curr_wep = ret[2]

            pg.display.flip()

            #change mouse 2s into 1s
            for m in range(len(self.mouse)):
                if self.mouse[m] == 2:
                    self.mouse[m] = 1

        #self.level.start_timer()

        #game music
        pg.mixer.music.load("res/music/boss.wav")
        pg.mixer.music.play(loops = -1)

        while self.running:

            self.event_loop()

            self.screen.blit(self.background,(0,0))

            #tick player
            #firing - if the player is firing
            #overlay - a surface that will be blitted over self.screen containing gui
            firing, overlay = self.player.tick(self.keys[K_w],self.keys[K_s],
                self.keys[K_a],self.keys[K_d],self.keys[K_q],self.keys[K_e],
                self.keys[K_SPACE],self.aim,self.hitler,self)

            #tick hitler
            self.hitler.tick(self.player,self)

            #render player view
            self.can_see_hitler,self.aim = self.level.render_view(self.screen,
                self.player.posX,self.player.posY,self.player.dirX,self.player.dirY,
            	self.player.planeX,self.player.planeY,self.player.get_rect())     

            #blit on the overlay
            self.screen.blit(overlay,(0,0))   

            #fps handling
            self.clock.tick()
            render = self.fpsfont.render(str(int(self.clock.get_fps())),1,(255,255,0))
            self.screen.blit(render,(20,20))

            '''
            render = self.timerfont.render(self.level.get_time(),1,(255,255,0))
            self.screen.blit(render,(self.screenW//2 - render.get_width()//2,20))
            '''
            
            pg.display.flip()

            #make mouse 2s to 1s
            for m in range(len(self.mouse)):
                if self.mouse[m] == 2:
                    self.mouse[m] = 1

            if self.win == True:
                self.win()

        pg.quit()

    def win(self,posX,posY,sprites):

        #function called to win the game

        #first watch hitler's death anim
        #then darkens the screen
        #and then blits on win surface

        win_screen = pg.image.load("res/win.png")
        win_screen.set_colorkey(win_screen.get_at((0,0)))
        gray = pg.Surface((640,480))
        gray.set_alpha(200)
        
        self.running = False
        self.can_see_hitler,self.aim = self.level.render_view(self.screen,
                self.player.posX,self.player.posY,self.player.dirX,self.player.dirY,
                self.player.planeX,self.player.planeY,self.player.get_rect())

        frame = 0

        while frame < len(sprites):
            #draw hitler death anim
            
            self.event_loop()
            
            self.level.add_temp_sprite(posX,posY,sprites[int(frame)],True)
            self.can_see_hitler,self.aim = self.level.render_view(self.screen,
                self.player.posX,self.player.posY,self.player.dirX,self.player.dirY,
                self.player.planeX,self.player.planeY,self.player.get_rect())  

            frame += 0.25

            pg.display.flip()

        #darken screen
        self.screen.blit(gray,(0,0))
        pg.display.flip()

        #wait 150 loops
        time = 0

        while time != 150:
            time += 1

        #blit on win screen
        self.screen.blit(win_screen,(0,0))
        pg.display.update()

        while 1:
            self.event_loop()

            #if player press y
            if self.keys[K_y]:
                #restart program
                restart_program()
                self.running = False
                break
            #if player presses n
            elif self.keys[K_n]:
                #quit
                self.running = False
                break

            pg.display.flip()

    def lose(self,overlay):

        #called if player loses

        #makes the screen red (blood)
        #blit on gameover surface

        self.screen.blit(overlay,(0,0))
        time = 0
        game_over = pg.image.load("res/gameover.png")
        game_over.set_colorkey(game_over.get_at((0,0)))
        
        while 1:
            self.event_loop()
            time += 1

            if time >= 200:
                self.screen.blit(game_over,(0,0))

            if self.keys[K_y]:
                #if player presses y, restart program
                restart_program()
                self.running = False
                break
            elif self.keys[K_n]:
                #if player presses n, quit program
                self.running = False
                break

            pg.display.flip()

class Player:

    #player class
    #handles the player's position, health, etc.

    def __init__(self,level,posX,posY,dirX,dirY,planeX,planeY,moveSpeed,rotSpeed,screenW,screenH):
        self.posX, self.posY = posX,posY    #position coord
        self.dirX, self.dirY = dirX,dirY    #direction vector
        self.planeX, self.planeY = planeX,planeY    #camera plane direction vector
        self.level = level  #level
        self.moveSpeed = moveSpeed  #move speed
        self.rotSpeed = rotSpeed    #rotation speed
        self.rect = (posX - 0.33,posY - 0.33,0.66,0.66)   #rect used to check for collisions with objects

        self.screenW,self.screenH = 640,480
        #create surface that has player gui and will be blitted onto main screen
        self.overlay = pg.Surface((640,480))
        self.overlay.set_colorkey((152,0,136))
        self.firing = False     #if playerif firing gun

        #player weapons
        self.weapons = [Knife(self.overlay),Pistol(self.overlay),MachineGun(self.overlay),ChainGun(self.overlay)]
        self.curr_wep = 3   #weapon uindex

        self.hp = 100       #health

        self.font = pg.font.Font(None,48)

        #player damage sounds
        self.damage_sound = [pg.mixer.Sound("res/snd/Oof!.wav"),
            pg.mixer.Sound("res/snd/Player Pain 1.wav"),
            pg.mixer.Sound("res/snd/Player Pain 2.wav")]

    def move(self,moveDirX,moveDirY,try_again=True):
        #moves the player if there is no collision in where the player is about to be (a priori)

        #whether or not there is a collision in where the player is about to move
        collide = False

        #the collide rect if the player moved
        poss_rect = (self.posX + moveDirX * self.moveSpeed - 0.33,self.posY + moveDirY * self.moveSpeed - 0.33,0.66,0.66)

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

        if not collide:     #no collison
            #move the player
            self.posX += moveDirX * self.moveSpeed
            self.posY += moveDirY * self.moveSpeed
            self.rect = poss_rect
            self.walking = True
        elif try_again:
            #try just X and Y values
            #but prevent it from checking just x and y values
            self.move(moveDirX,0,False)
            self.move(0,moveDirY,False)

    def damage(self,n):
        self.hp -= n
        random.choice(self.damage_sound).play()

    def tick(self,u,d,l,r,rotL,rotR,space,aim,hitler,game):   

        #called every loop to update player
        #returns a surface containing gui to be blitted onto screen
        #as well as a boolean indicating if firing or not

        self.overlay.fill((152,0,136))

        #move player
        if u and not d:
            self.move(self.dirX,self.dirY)
        elif d and not u:
            self.move(-self.dirX,-self.dirY)

        #move player strafe
        if l and not r:
            self.move(-self.dirY,self.dirX)
        elif r and not l:
            self.move(self.dirY,-self.dirX)

        #rotate player
        if rotR and not rotL:
            oldDirX = self.dirX
            self.dirX = self.dirX * math.cos(math.radians(-self.rotSpeed)) - self.dirY * math.sin(math.radians(-self.rotSpeed))
            self.dirY = oldDirX * math.sin(math.radians(-self.rotSpeed)) + self.dirY * math.cos(math.radians(-self.rotSpeed))
            oldPlaneX = self.planeX
            self.planeX = self.planeX * math.cos(math.radians(-self.rotSpeed)) - self.planeY * math.sin(math.radians(-self.rotSpeed))
            self.planeY = oldPlaneX * math.sin(math.radians(-self.rotSpeed)) + self.planeY * math.cos(math.radians(-self.rotSpeed))
        elif rotL and not rotR:
            oldDirX = self.dirX
            self.dirX = self.dirX * math.cos(math.radians(self.rotSpeed)) - self.dirY * math.sin(math.radians(self.rotSpeed))
            self.dirY = oldDirX * math.sin(math.radians(self.rotSpeed)) + self.dirY * math.cos(math.radians(self.rotSpeed))
            oldPlaneX = self.planeX
            self.planeX = self.planeX * math.cos(math.radians(self.rotSpeed)) - self.planeY * math.sin(math.radians(self.rotSpeed))
            self.planeY = oldPlaneX * math.sin(math.radians(self.rotSpeed)) + self.planeY * math.cos(math.radians(self.rotSpeed))

        #fire the weapon
        self.firing = self.weapons[self.curr_wep].tick(space)
        #get the weapons's current sprite
        wep_sprite = self.weapons[self.curr_wep].get_sprite()
        #and blit it on the overlay
        self.overlay.blit(wep_sprite,(self.overlay.get_width() / 2 - wep_sprite.get_width() / 2,self.overlay.get_height() - wep_sprite.get_height()))

        self.hp_text = self.font.render("+"+"{0:0=3d}".format(self.hp),1,(255,255,0))   #render hp
        #pg.draw.rect(self.overlay,(0,0,0),(self.screenW - self.hp_text.get_width() - 10,
        #    self.screenH - self.hp_text.get_height() - 10,self.hp_text.get_width(),self.hp_text.get_height()))
        self.overlay.blit(self.hp_text,(self.screenW - self.hp_text.get_width() - 10,self.screenH - self.hp_text.get_height() - 10))        #blit on hp
        
        if self.firing and aim:     #means player will hit hitler
            #deal damage to hitler based on distance from hitler to player
            enemy_dist = ((hitler.posX - self.posX)**2 + (hitler.posY - self.posY)**2)**0.5
            damage = self.weapons[self.curr_wep].deal_damage(enemy_dist)
            hitler.damage(damage)

        if self.hp <= 0:
            #kill player
            deadsound = pg.mixer.Sound("res/snd/Player Dies.wav")    #load death sound
            #blit on overlay a red surface (blood)
            bloodsurf = pg.Surface((640,480))
            bloodsurf.fill((255,0,0))
            bloodsurf.set_alpha(200)
            self.overlay.blit(bloodsurf,(0,0))                      
            deadsound.play()                                        #play death sound
            game.lose(self.overlay)                                 #call lose function

        return (self.firing,self.overlay.convert())

    def get_rect(self):
        return self.rect

if __name__ == "__main__":
    game = Game(640,480)
    game.run()
