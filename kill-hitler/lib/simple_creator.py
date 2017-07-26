import pickle
import pygame as pg
import os

from lib.Level import Level

def load_image(image, darken, colorKey = None):
    ret = []
    if colorKey is not None:
        image.set_colorkey(colorKey)
    if darken:
        image.set_alpha(127)
    for i in range(image.get_width()):
        s = pg.Surface((1, image.get_height()))
        #s.fill((0,0,0))
        s.blit(image, (- i, 0))
        if colorKey is not None:
            s.set_colorkey(colorKey)
        ret.append(s)
    return ret

leveldir = os.getcwd()

ind = leveldir.rfind("\\")
topdir = leveldir[:ind]

texdir = topdir + "\\wolf\\res\\tex"

texim = pg.image.load(texdir + "\\walls.png")
imw,imh = texim.get_width(), texim.get_height()

tex_dict = {
    0: None
    }

spriteim = pg.image.load(texdir+"\\sprites.png")
sprite_dict = {}


levelmap = [
    [8,8,8,8,8,8,8,8,8,8,8,8,8,8],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,8],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,8],
    [8,0,0,6,6,6,6,6,6,6,6,0,0,8],
    [8,0,0,6,6,6,6,6,6,6,6,0,0,8],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,8],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,8],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,8],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,8],
    [8,0,0,6,6,6,6,6,6,6,6,0,0,8],
    [8,0,0,6,6,6,6,6,6,6,6,0,0,8],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,8],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,8],
    [8,8,8,8,8,8,8,8,8,8,8,8,8,8],
    ]

n = 0

for i in range(0,imw,64):
    surfbuff = pg.Surface((64,64))
    surfbuff.blit(texim,(0,0),pg.Rect(i,0,64,64))
    tex_dict[n] = load_image(surfbuff.copy(),False)
    n += 1

for i in range(0,imw,64):
    surfbuff = pg.Surface((64,64))
    surfbuff.blit(texim,(0,0),pg.Rect(i,0,64,64))
    tex_dict[n] = load_image(surfbuff.copy(),True)
    n += 1

n = 0

for i in range(0,spriteim.get_width(),64):
    surfbuff = pg.Surface((64,64))
    surfbuff.blit(spriteim,(0,0),pg.Rect(i,0,64,64))
    sprite_dict[n] = load_image(surfbuff.copy(),False)
    n += 1

collsprites = [0,1]
sprites = [(6,6,1),(6,7,1),(7,6,1),(7,7,1)]

for i in sprites:
    if i[2] in collsprites:
        levelmap[i[1]][i[0]] = -1

level = Level(levelmap,tex_dict,sprite_dict,sprites,64)
level.pack_tex()

f = open("res/level/simple.level",'wb')

pickle.dump(level,f)

f.close()
