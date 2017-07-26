import pickle
from lib.Level import *

level = pickle.load(open("res/level/square.level","rb"))
a = level.level

for y in a:
    print(y)
