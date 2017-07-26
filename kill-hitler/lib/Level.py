import math
import pygame as pg
from pygame.locals import *
import time
from datetime import timedelta

class Level:

    tex_dict = {}
    level = []

    def __init__(self,level,tex_dict,sprite_dict,sprite_loc,texW):
        self.texW = texW    #texture width, usually 64

        #dict of textures of walls and level map
        self.tex_dict = tex_dict
        self.level = level

        #dict of sprites and sprite positions
        self.sprite_dict = sprite_dict
        self.sprites = sprite_loc
        self.temp_sprites = []

        #dictionaries of sprites and textures that have the image as a string for pickling
        self.str_tex_dict = {}
        self.str_sprite_dict = {}

        self.start_time = 0
        self.end_time = 0

    def get_size(self):
        return (len(self.level[0]),len(self.level))

    def add_temp_sprite(self,x,y,sprite,hitler=False):
        #hitler - if it is hitler.
        #allows level to check if player can see hitler
        self.temp_sprites.append((x,y,sprite,hitler))

    def pack_tex(self):
        #pack textures for pickling by converting surface to string
        #this way they will be preserved after pickling
        for key,value in self.tex_dict.items():
            self.str_tex_dict[key] = ([pg.image.tostring(mn,"RGBA") for mn in value],(1,64))

        for key,value in self.sprite_dict.items():
            self.str_sprite_dict[key] = ([pg.image.tostring(mn,"RGBA") for mn in value],(1,64))

        self.tex_dict = {}

    def unpack_tex(self):
        #unpack textures that were packed with self.pack_tex() after pickling
        for key,value in self.str_tex_dict.items():
            self.tex_dict[key] = [pg.image.fromstring(mn,value[1],"RGBA") for mn in value[0]]

        for key,value in self.str_sprite_dict.items():
            self.sprite_dict[key] = [pg.image.fromstring(mn,value[1],"RGBA") for mn in value[0]]

        self.str_tex_dict = {}

    def convert_tex(self):
        #convert textures so that they can be indexed by x value
        for key,value in self.tex_dict.items():
            self.tex_dict[key] = [mn.convert() for mn in value]

        for key,value in self.sprite_dict.items():
            colorkey = value[0].get_at((0,0))
            for mn in value:
                mn.set_colorkey(colorkey)
            self.sprite_dict[key] = [mn.convert() for mn in value]

    def start_timer(self):
        #start a timer
        self.start_time = time.time()

    def stop_timer(self):
        #stop a started timer
        self.end_time = time.time()

    def get_time(self):
        #get passed seconds based on current time - self.start_time
        m, s = divmod(int(time.time() - self.start_time), 60)
        h, m = divmod(m, 60)
        return "%d : %02d : %02d" % (h, m, s)

    def render_view(self,surface,posX,posY,dirX,dirY,planeX,planeY,playerRect):
        #render the view of the player
        #uses http://en.wikipedia.org/wiki/Bresenham's_line_algorithm

        all_sprites = []     #sprites + enemy sprites
        can_see_hitler = False 
        hitler_strips_seen = 0
        aim = False

        def sprite_sort(a):
            #function given to sort() method to sort sprites by position, farthest to closest
            return ((a[0] - posX)**2 + (a[1] - posY)**2)**0.5

        screenW = surface.get_width()
        screenH = surface.get_height()

        rayDists = []

        for x in range(screenW):            
            cameraX = 2 * x / float(screenW) - 1    #x pos, camera

            rayPosX,rayPosY = posX,posY     #position of ray
            rayDirX,rayDirY = dirX + planeX * cameraX,dirY + planeY * cameraX   #direction of ray
            mapX,mapY = int(rayPosX),int(rayPosY)   #position of ray on map
            sideDistX,sideDistY = 0.0,0.0

            if rayDirX == 0:
                rayDirX = 0.0001
            if rayDirY == 0:
                rayDirY = 0.0001

            deltaDistX = math.sqrt(1 + (rayDirY**2) / (rayDirX**2))
            deltaDistY = math.sqrt(1 + (rayDirX**2) / (rayDirY**2)) 
            perpWallDist = 0.0

            stepX,stepY = 0.0,0.0

            hit = False  #whether or not there was a collision with a block
            side = "x"   #whether it was a hit on the x side or the y side of a block

            if rayDirX < 0:
                stepX = -1
                sideDistX = (rayPosX - mapX) * deltaDistX
            else:
                stepX = 1
                sideDistX = (mapX + 1.0 - rayPosX) * deltaDistX

            if rayDirY < 0:
                stepY = -1
                sideDistY = (rayPosY - mapY) * deltaDistY
            else:
                stepY = 1
                sideDistY = (mapY + 1.0 - rayPosY) * deltaDistY

            while hit == False:
                if sideDistX < sideDistY:
                    sideDistX += deltaDistX
                    mapX += stepX
                    side = "x"
                else:
                    sideDistY += deltaDistY
                    mapY += stepY
                    side = "y"

                if self.level[mapY][mapX] >= 1:
                    hit = True

            if rayDirY == 0:
                rayDirY = 0.0001

            if side == "x":
                perpWallDist = (abs((mapX - rayPosX + (1 - stepX) / 2) / rayDirX))
            elif side == "y":
                perpWallDist = (abs((mapY - rayPosY + (1 - stepY) / 2) / rayDirY))
                
            lineHeight = abs(int(screenH / max(perpWallDist,0.0001)))

            #which x coordinate the wall was hit at
            if side == "y":
                wallX = rayPosX + ((mapY - rayPosY + (1 - stepY) / 2) / rayDirY) * rayDirX
            else:
                wallX = rayPosY + ((mapX - rayPosX + (1 - stepX) / 2) / rayDirX) * rayDirY

            wallX -= math.floor(wallX)

            #x coordinate of collision on texture
            texX = int(wallX * float(self.texW))

            texNum = self.level[mapY][mapX] - 1     #1 subtracted because 0 is nothing on the level

            if (side == "x" and rayDirX > 0) or (side == "y" and rayDirY < 0):
                texX = self.texW - texX - 1

            drawStart = -lineHeight / 2 + screenH / 2
            drawEnd = min(lineHeight / 2 + screenH / 2,screenH - 1)

            if(side == "y"):
                texNum +=8
                
            if lineHeight > 10000:
                lineHeight=10000
                drawStart = -10000 /2 + screenH/2

            surface.blit(pg.transform.scale(self.tex_dict[texNum][texX], (1, lineHeight)), (x, drawStart))
            rayDists.append(perpWallDist)

        all_sprites = self.sprites + self.temp_sprites
        all_sprites.sort(key=sprite_sort,reverse=True)

        for sprite in all_sprites:
            spriteX, spriteY = (sprite[0]+0.5) - posX,(sprite[1]+0.5) - posY      #differences in position between player and sprite

            invDet = 1.0 / (planeX * dirY - dirX * planeY)

            #transforming the sprite for camera space to preventfisheye effect
            transformX = invDet * (dirY * spriteX - dirX * spriteY)         #where on the surface, x value
            transformY = invDet * (-planeY * spriteX + planeX * spriteY)    #where on the surface, depth

            if transformY == 0:
                transformY = 0.0001

            #where to draw it on the screen
            spriteSurfaceX = int((screenW / 2) * (1 + transformX / transformY)) 

            #height and width calculations
            spriteH = abs(int(screenH / transformY))
            spriteW = abs(int(screenH / transformY))

            #and where to draw it
            drawStartY = int(-spriteH / 2 + screenH / 2)
            drawEndY = int(spriteH / 2 + screenH / 2)

            drawStartX = int(-spriteW / 2 + spriteSurfaceX)
            drawEndX = int(spriteW / 2 + spriteSurfaceX)

            if spriteH < 1000:  #not too large
                for sx in range(drawStartX,drawEndX):   #draws sprite by vertical lines
                    texX = int(256 * (sx - (-spriteW / 2 + spriteSurfaceX)) * self.texW / spriteW) / 256    #line of sprite
                    #the conditions in the if are:
                    ##1) it's in front of camera plane so you don't see things behind you
                    ##2) it's on the surface (left)
                    ##3) it's on the surface (right)
                    ##4) There is no wall inbetween player and sprite line (checking rayDist)
                    if (transformY > 0 and sx > 0 and sx < screenW and transformY < rayDists[sx]):
                        if len(sprite) == 3:    #for normal sprite, like a column or a lamp
                            surface.blit(pg.transform.scale(self.sprite_dict[sprite[2]][int(texX)], (1, spriteH)), (sx, drawStartY))
                        elif len(sprite) == 4:  #for enemy sprites
                            surface.blit(pg.transform.scale(sprite[2][int(texX)], (1, spriteH)), (sx, drawStartY))
                            if sprite[3] == True:
                                hitler_strips_seen += 1
                                if screenW // 2 - 10 <= sx <= screenW // 2 + 10:
                                    aim = True

        if hitler_strips_seen >= 50:
            can_see_hitler = True                   

        self.temp_sprites = []                        
        return (can_see_hitler,aim)

    def check_wall_col(self,x,y):
        try:
            if self.level[int(y)][int(x)] != 0:
                return True
            else:
                return False
        except IndexError:
            return False

    def a_star_path(self,sx,sy,ex,ey):

        def get_h(x,y):
            #returns heuristic
            return x + y

        def get_adj(x,y,closedset):
            #returns st of adjacent squares of a point
            #if they are not a wall or in the closed set
            #adj = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
            adj = [(1,0),(0,1),(0,-1),(-1,0)]
            ret = set()
            for (m,n) in adj:
                tx,ty = x+m,y+n
                if not self.check_wall_col(tx,ty) and (tx,ty) not in closedset:
                    ret.add((tx,ty))
            return ret

        def follow_current_path(cx,cy,ex,ey,openset,closedset,fx,gx,hx,parent):
            next_cell = None
            for (ax,ay) in get_adj(cx,cy,closedset):
                poss_gx = gx[(cx,cy)] + 1
                if (ax,ay) not in openset:
                    openset.add((ax,ay))
                    poss_best = True
                elif (ax,ay) in gx and poss_gx < gx[(ax,ay)]:
                    poss_best = True
                else:
                    poss_best = False

                if poss_best:
                    x,y = abs(ex-ax),abs(ey-ay)
                    parent[(ax,ay)] = (cx,cy)
                    gx[(ax,ay)] = poss_gx
                    hx[(ax,ay)] = get_h(x,y)
                    fx[(ax,ay)] = gx[(ax,ay)] + hx[(ax,ay)]
                    if not next_cell or fx[(ax,ay)] < fx[next_cell]:
                        next_cell = (ax,ay)

            if next_cell:
                return (next_cell[0],next_cell[1])
            else:
                return None

        def get_path(ax,ay,parent,sol):
            #recursive function to reconstruct path

            bx,by = ax,ay

            while (bx,by) in parent:
                #print(sx,sy,bx,by)
                sol.append((bx,by))
                bx,by = parent[(bx,by)]

            return sol

            '''
            if (ax,ay) in parent:
                sol.append((ax,ay))
                get_path(parent[(ax,ay)][0],parent[(ax,ay)][1],parent,sol)
            '''

        openset = set()
        closedset = set(((sx,sy),))
        fx = {}                 #distance plus cost, g+h
        gx = {(sx,sy):0}     #cost from start to current pos
        hx = {}                 #dist to goal based on heuristic
        parent = {}             #path reconstruction
        solved = False
        sol = []                #solution
        cx,cy = sx,sy   #current position
        cx,cy = follow_current_path(cx,cy,ex,ey,openset,closedset,fx,gx,hx,parent)

        while openset and not solved:  #while there are things in openset, meaning there is a possible path
            for (ax,ay) in openset:
                if ((cx,cy) not in openset) or (fx[(ax,ay)] < fx[(cx,cy)]):
                    cx,cy = ax,ay
            if (cx,cy) == (ex,ey):
                get_path(cx,cy,parent,sol)
                solved = True
            else:
                openset.discard((cx,cy))
                closedset.add((cx,cy))
                next_cell = follow_current_path(cx,cy,ex,ey,openset,closedset,fx,gx,hx,parent)
                if next_cell:
                    cx,cy = next_cell

        if solved == False:
            return None
        else:
            return sol
