"""
author: 
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download: 
idea: clean python3/pygame template using pygame.math.vector2
"""
import pygame
import random
import os
import time
import math
import Islandwar_levels as Levels

#print(L.levels(3))

def randomize_color(color, delta=50):
    d=random.randint(-delta, delta)
    color = color + d
    color = min(255,color)
    color = max(0, color)
    return color

def make_text(msg="pygame is cool", fontcolor=(255, 0, 255), fontsize=42, font=None):
    """returns pygame surface with text. You still need to blit the surface."""
    myfont = pygame.font.SysFont(font, fontsize)
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    return mytext

def write(background, text, x=50, y=150, color=(0,0,0),
          fontsize=None, center=False):
        """write text on pygame surface. """
        if fontsize is None:
            fontsize = 24
        font = pygame.font.SysFont('mono', fontsize, bold=True)
        fw, fh = font.size(text)
        surface = font.render(text, True, color)
        if center: # center text around x,y
            background.blit(surface, (x-fw//2, y-fh//2))
        else:      # topleft corner is x,y
            background.blit(surface, (x,y))
            
def distance(point_1=(0, 0), point_2=(0, 0)):
    """Returns the distance between two points"""
    return math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)

def elastic_collision(sprite1, sprite2):
        """elasitc collision between 2 VectorSprites (calculated as disc's).
           The function alters the dx and dy movement vectors of both sprites.
           The sprites need the property .mass, .radius, pos.x pos.y, move.x, move.y
           by Leonard Michlmayr"""
        if sprite1.static and sprite2.static:
            return 
        dirx = sprite1.pos.x - sprite2.pos.x
        diry = sprite1.pos.y - sprite2.pos.y
        sumofmasses = sprite1.mass + sprite2.mass
        sx = (sprite1.move.x * sprite1.mass + sprite2.move.x * sprite2.mass) / sumofmasses
        sy = (sprite1.move.y * sprite1.mass + sprite2.move.y * sprite2.mass) / sumofmasses
        bdxs = sprite2.move.x - sx
        bdys = sprite2.move.y - sy
        cbdxs = sprite1.move.x - sx
        cbdys = sprite1.move.y - sy
        distancesquare = dirx * dirx + diry * diry
        if distancesquare == 0:
            dirx = random.randint(0,11) - 5.5
            diry = random.randint(0,11) - 5.5
            distancesquare = dirx * dirx + diry * diry
        dp = (bdxs * dirx + bdys * diry) # scalar product
        dp /= distancesquare # divide by distance * distance.
        cdp = (cbdxs * dirx + cbdys * diry)
        cdp /= distancesquare
        if dp > 0:
            if not sprite2.static:
                sprite2.move.x -= 2 * dirx * dp
                sprite2.move.y -= 2 * diry * dp
            if not sprite1.static:
                sprite1.move.x -= 2 * dirx * cdp
                sprite1.move.y -= 2 * diry * cdp

class Game():
    quit_game = False
    difficulty = 0
    level = 1
    for l in Levels.levels.keys():
        if int(l) <= 0:
            level -= 1 #for every tutorial level we go one level below 0
    enemy_color = [(255,0,0)]
    player_color = (0,255,0)
    player_wood = 0
    player_iron = 0
    player_ships = 0
    player_islands = 0
    
    enemy_wood = 0
    enemy_iron = 0
    enemy_ships = 0
    enemy_islands = 0
    wood_islandgroup = pygame.sprite.Group()
    iron_islandgroup = pygame.sprite.Group()
    ship_islandgroup = pygame.sprite.Group()
    main_islandgroup = pygame.sprite.Group()
    islandgroup = pygame.sprite.Group()
    groups = [wood_islandgroup,iron_islandgroup,ship_islandgroup,main_islandgroup,islandgroup]

        
class Flytext(pygame.sprite.Sprite):
    def __init__(self, x, y, text="hallo", color=(255, 0, 0),
                 dx=0, dy=-50, duration=2, acceleration_factor = 1.0, delay = 0, fontsize=22):
        """a text flying upward and for a short time and disappearing"""
        self._layer = 7  # order of sprite layers (before / behind other sprites)
        pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.r, self.g, self.b = color[0], color[1], color[2]
        self.dx = dx
        self.dy = dy
        self.x, self.y = x, y
        self.duration = duration  # duration of flight in seconds
        self.acc = acceleration_factor  # if < 1, Text moves slower. if > 1, text moves faster.
        self.image = make_text(self.text, (self.r, self.g, self.b), fontsize)  # font 22
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.time = 0 - delay

    def update(self, seconds):
        self.time += seconds
        if self.time < 0:
            self.rect.center = (-100,-100)
        else:
            self.y += self.dy * seconds
            self.x += self.dx * seconds
            self.dy *= self.acc  # slower and slower
            self.dx *= self.acc
            self.rect.center = (self.x, self.y)
            if self.time > self.duration:
                self.kill()      # remove Sprite from screen and from groups
                

class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {} # { number, Sprite }

    def __init__(self, **kwargs):
        self._default_parameters(**kwargs)
        pygame.sprite.Sprite.__init__(self, self.groups) #call parent class. NEVER FORGET !
        self.number = VectorSprite.number # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
        self._overwrite_parameters()
        self.create_image()
        self.distance_traveled = 0 # in pixel
        self.rect.center = (int(self.pos.x), -int(self.pos.y))
        if self.angle != 0:
            self.set_angle(self.angle)
        self.start()
        
    def start(self):
        pass

    def _overwrite_parameters(self):
        """change parameters before create_image is called""" 
        pass

    def _default_parameters(self, **kwargs):    
        """get unlimited named arguments and turn them into attributes
           default values for missing keywords"""

        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
        else:
            self._layer = self.layer
        if "static" not in kwargs:
            self.static = False
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(random.randint(0, Viewer.width),-50)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(0,0)
        if "radius" not in kwargs:
            self.radius = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        if "height" not in kwargs:
            self.height = self.radius * 2
        if "color" not in kwargs:       #self.color = None
            self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if "hitpoints" not in kwargs:
            self.hitpoints = 100
        self.hitpointsfull = self.hitpoints # makes a copy
        if "mass" not in kwargs:
            self.mass = 10
        if "damage" not in kwargs:
            self.damage = 10
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "angle" not in kwargs:
            self.angle = 0 # facing right?
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "mass" not in kwargs:
            self.mass = 15
        if "upkey" not in kwargs:
            self.upkey = None
        if "downkey" not in kwargs:
            self.downkey = None
        if "rightkey" not in kwargs:
            self.rightkey = None
        if "leftkey" not in kwargs:
            self.leftkey = None
        if "speed" not in kwargs:
            self.speed = None
        if "age" not in kwargs:
            self.age = 0 # age in seconds
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False
        if "dangerhigh" not in kwargs:
            self.dangerhigh = False
        if "fluffball_color" not in kwargs:
            self.fluffball_color = random.choice(["fluffballb.", "fluffballp.", "fluffballt.", "fluffballr."])

    def kill(self):
        if self.number in self.numbers:
           del VectorSprite.numbers[self.number] # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width,self.height))
            self.image.fill((self.color))
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect= self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
        
    def ai(self):
        pass

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        #self.ai()
        # ----- kill because... ------
        if self.hitpoints <= 0:
            self.kill()
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.bossnumber is not None:
            if self.kill_with_boss:
                if self.bossnumber not in VectorSprite.numbers:
                    self.kill()
            if self.sticky_with_boss:
                boss = VectorSprite.numbers[self.bossnumber]
                #self.pos = v.Vec2d(boss.pos.x, boss.pos.y)
                self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
        self.pos += self.move * seconds
        self.distance_traveled += self.move.length() * seconds
        self.age += seconds
        self.wallbounce()
        self.rect.center = ( round(self.pos.x, 0), -round(self.pos.y, 0) )

    def wallbounce(self):
        # ---- bounce / kill on screen edge ----
        # ------- left edge ----
        if self.pos.x < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = 0
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = Viewer.width 
        # -------- upper edge -----
        if self.pos.y  > 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = 0
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = -Viewer.height
        # -------- right edge -----                
        if self.pos.x  > Viewer.width:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = Viewer.width
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = 0
        # --------- lower edge ------------
        if self.dangerhigh:
            y = self.dangerhigh
        else:
            y = Viewer.height
        if self.pos.y   < -y:
            if self.kill_on_edge:
                self.hitpoints = 0
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = -y
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = 0

class Explosion():
    
    def __init__(self, pos, what="Spark", maxspeed=150, minspeed=20, color=(255,255,0),maxduration=2.5,gravityy=3.7,sparksmin=5,sparksmax=20,acc=1.0, min_angle=0, max_angle=360):

        for s in range(random.randint(sparksmin,sparksmax)):
            v = pygame.math.Vector2(1,0) # vector aiming right (0°)
            a = random.randint(int(min_angle),int(max_angle))
            v.rotate_ip(a)
            g = pygame.math.Vector2(0, - gravityy)
            speed = random.randint(minspeed, maxspeed)     #150
            duration = random.random() * maxduration
            if what == "Spark":     
                Spark(pos=pygame.math.Vector2(pos.x, pos.y), angle= a, move=v*speed,
                  max_age = duration, color=color, gravity = g)
            elif what == "Crumb":
                
                Crumb(pos=pygame.math.Vector2(pos.x, pos.y), angle= a, move=v*speed,
                  max_age = duration, color=color, gravity = g, acc=acc)
        
class Spark(VectorSprite):

    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "gravity" not in kwargs:
            self.gravity = pygame.math.Vector2(0, -3.7)
    
    def _overwrite_parameters(self):
        self._layer = 2
        self.kill_on_edge = True
    
    def create_image(self):
        r,g,b = self.color
        r = randomize_color(r,50)
        g = randomize_color(g,50)
        b = randomize_color(b,50)
        self.image = pygame.Surface((10,10))
        pygame.draw.line(self.image, (r,g,b), 
                         (10,5), (5,5), 3)
        pygame.draw.line(self.image, (r,g,b),
                          (5,5), (2,5), 1)
        self.image.set_colorkey((0,0,0))
        self.rect= self.image.get_rect()
        self.image0 = self.image.copy()

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        self.move += self.gravity

class Island(VectorSprite):
    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "empire_color" not in kwargs:
            self.empire_color = (0,255,0)
        if "ships" not in kwargs:
            self.ships = 0
            
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        if self.empire_color in Game.enemy_color:
            self.ai()
            
    def ai(self):
        if Game.enemy_wood < 5:
            if random.random() < 0.005:
                if self.ships > 0: #are there any ships?
                    target = []
                    for i in Game.wood_islandgroup:
                        d = distance(self.pos,i.pos)
                        if i.empire_color == self.empire_color:
                            continue
                        elif i.empire_color == Game.player_color:
                            if len(target) == 0:
                                target = [d+1000,i.pos]
                            elif target[0] > d+1000:
                                target = [d+1000,i.pos]
                        else:
                            if len(target) == 0:
                                target = [d,i.pos]
                            elif target[0] > d:
                                target = [d,i.pos]
                    if len(target) != 0:
                        self.ships -= 1
                        print("Wood",self.pos,target)
                        s = pygame.math.Vector2(self.pos[0],self.pos[1])
                        v = target[1] - s
                        m = v.normalize() * 30
                        move = pygame.math.Vector2(m)
                        start = v.normalize() * (self.size//2 + 25)# 25 = length of ship
                        e = pygame.math.Vector2(1,0)
                        angle = e.angle_to(m)
                        Ship(pos=self.pos+start, destination=target[1], move=move, angle=angle, empire_color=self.empire_color)
        if Game.enemy_iron < 5:
            if random.random() < 0.005:
                if self.ships > 0: #are there any ships?
                    target = []
                    print(Game.iron_islandgroup)
                    for i in Game.iron_islandgroup:
                        d = distance(self.pos,i.pos)
                        if i.empire_color == self.empire_color:
                            continue
                        elif i.empire_color == Game.player_color:
                            if len(target) == 0:
                                target = [d+1000,i.pos]
                            elif target[0] > d+1000:
                                target = [d+1000,i.pos]
                        else:
                            if len(target) == 0:
                                target = [d,i.pos]
                            elif target[0] > d:
                                target = [d,i.pos]
                    if len(target) != 0:
                        self.ships -= 1
                        print("Iron",self.pos,target)
                        v = target[1] - self.pos
                        m = v.normalize() * 30
                        move = pygame.math.Vector2(m)
                        start = v.normalize() * (self.size//2 + 25)# 25 = length of ship
                        e = pygame.math.Vector2(1,0)
                        angle = e.angle_to(m)
                        Ship(pos=self.pos+start, destination=target[1], move=move, angle=angle, empire_color=self.empire_color)
        if Game.enemy_iron > 5 and Game.enemy_wood > 5:
            if random.random() < 0.005:
                if self.ships > 0: #are there any ships?
                    target = []
                    for i in Game.ship_islandgroup:
                        d = distance(self.pos,i.pos)
                        if i.empire_color == self.empire_color:
                            continue
                        elif i.empire_color == Game.player_color:
                            if len(target) == 0:
                                target = [d+1000,i.pos]
                            elif target[0] > d+1000:
                                target = [d+1000,i.pos]
                        else:
                            if len(target) == 0:
                                target = [d,i.pos]
                            elif target[0] > d:
                                target = [d,i.pos]
                    if len(target) != 0:
                        self.ships -= 1
                        print("Ships",self.pos,target)
                        v = target[1] - self.pos
                        m = v.normalize() * 30
                        move = pygame.math.Vector2(m)
                        start = v.normalize() * (self.size//2 + 25)# 25 = length of ship
                        e = pygame.math.Vector2(1,0)
                        angle = e.angle_to(m)
                        Ship(pos=self.pos+start, destination=target[1], move=move, angle=angle, empire_color=self.empire_color)
        if random.random() < 0.0001 + Game.enemy_ships*0.0005:
            if self.ships > 0: #are there any ships?
                    target = []
                    for i in Game.main_islandgroup:
                        d = distance(self.pos,i.pos)
                        if i.empire_color == self.empire_color:
                            continue
                        elif i.empire_color == Game.player_color:
                            if len(target) == 0:
                                target = [d+1000,i.pos]
                            elif target[0] > d+1000:
                                target = [d+1000,i.pos]
                        else:
                            if len(target) == 0:
                                target = [d,i.pos]
                            elif target[0] > d:
                                target = [d,i.pos]
                    if len(target) != 0:
                        self.ships -= 1
                        v = target[1] - self.pos
                        print("Main",self.pos,target)
                        m = v.normalize() * 30
                        move = pygame.math.Vector2(m)
                        start = v.normalize() * (self.size//2 + 25)# 25 = length of ship
                        e = pygame.math.Vector2(1,0)
                        angle = e.angle_to(m)
                        Ship(pos=self.pos+start, destination=target[1], move=move, angle=angle, empire_color=self.empire_color)
        

class Wood_Island(Island):
    
    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
        #if "empire_color" not in kwargs:
        #    self.empire_color = (0,255,0)
        #if "ships" not in kwargs:
        #    self.ships = 0

    def _overwrite_parameters(self):
        self.size = 100
        #self.empire_color = (0,255,0)

    def create_image(self):
        self.image = pygame.Surface((self.size,self.size))
        pygame.draw.circle(self.image, self.empire_color, (self.size//2,self.size//2), self.size//2)
        pygame.draw.circle(self.image, (0,128,0), (self.size//2,self.size//2), self.size//2-5)
        write(self.image, "Wood production", x=5, y=40, fontsize=10, color=(1,1,1))
        self.image.set_colorkey((0,0,0))
        self.rect= self.image.get_rect()
        self.image0 = self.image.copy()
        
    def update(self, seconds):
        Island.update(self, seconds)
        if self.empire_color == Game.player_color:
            Game.player_wood += 0.01
        elif self.empire_color in Game.enemy_color:
            Game.enemy_wood += 0.01
        else:
            pass
        #write(self.image, "{}".format(self.ships), x=self.size-10, y=self.size-self.size//5,  fontsize=self.size//5, color=(255,0,0))
        
class Iron_Island(Island):

    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
        #if "empire_color" not in kwargs:
        #    self.empire_color = (0,255,0)
        #if "ships" not in kwargs:
        #    self.ships = 0
    
    def _overwrite_parameters(self):
        self.size = 100
        #self.ships = 5
        #self.empire_color = (0,255,0)

    def create_image(self):
        self.image = pygame.Surface((self.size,self.size))
        pygame.draw.circle(self.image, self.empire_color, (self.size//2,self.size//2), self.size//2)
        pygame.draw.circle(self.image, (100,100,100), (self.size//2,self.size//2), self.size//2-5)
        write(self.image, "Iron production", x=5, y=40, fontsize=10, color=(1,1,1))
        self.image.set_colorkey((0,0,0))
        self.rect= self.image.get_rect()
        self.image0 = self.image.copy()
        
    def update(self, seconds):
        Island.update(self, seconds)
        if self.empire_color == Game.player_color:
            Game.player_iron += 0.01
        elif self.empire_color in Game.enemy_color:
            Game.enemy_iron += 0.01
        else:
            pass
        #write(self.image, "{}".format(self.ships), x=self.size-10, y=self.size-self.size//5,  fontsize=self.size//5, color=(255,0,0))
        
class Ship_Island(Island):

    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
        #if "empire_color" not in kwargs:
        #    self.empire_color = (0,255,0)
        #if "ships" not in kwargs:
        #    self.ships = 0
    
    def _overwrite_parameters(self):
        self.size = 100
        #self.ships = 5
        #self.empire_color = (0,255,0)

    def create_image(self):
        self.image = pygame.Surface((self.size,self.size))
        pygame.draw.circle(self.image, self.empire_color, (self.size//2,self.size//2), self.size//2)
        pygame.draw.circle(self.image, (140,100,20), (self.size//2,self.size//2), self.size//2-5)
        write(self.image, "Ship production", x=5, y=40, fontsize=10, color=(1,1,1))
        self.image.set_colorkey((0,0,0))
        self.rect= self.image.get_rect()
        self.image0 = self.image.copy()
        
    def update(self, seconds):
        Island.update(self, seconds)
        if self.empire_color == Game.player_color:
            if Game.player_iron >= 5 and Game.player_wood >= 5:
                Game.player_iron -= 5
                Game.player_wood -= 5
                self.ships += 1
        elif self.empire_color in Game.enemy_color:
            if Game.enemy_iron >= 5 and Game.enemy_wood >= 5:
                Game.enemy_iron -= 5
                Game.enemy_wood -= 5
                self.ships += 1
        else:
            pass
                

class Main_Island(Island):

    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
        #if "empire_color" not in kwargs:
        #    self.empire_color = (0,255,0)
        #if "ships" not in kwargs:
        #    self.ships = 0

    
    def _overwrite_parameters(self):
        self.size = 200
        #self.ships = 5
        #self.empire_color = (0,255,0)
    
    def create_image(self):
        self.image = pygame.Surface((self.size,self.size))
        pygame.draw.circle(self.image, self.empire_color, (self.size//2,self.size//2), self.size//2)
        pygame.draw.circle(self.image, (30,200,30), (self.size//2,self.size//2), self.size//2-5)
        write(self.image, "Main Island", x=10, y=80, fontsize=20, color=(1,1,1))
        self.image.set_colorkey((0,0,0))
        self.rect= self.image.get_rect()
        self.image0 = self.image.copy()
    
    def update(self, seconds):
        Island.update(self, seconds)
        #write(self.image, "{}".format(self.ships), x=self.size-30, y=self.size-self.size//5,  fontsize=self.size//5, color=(255,0,0))
        
class Ship(VectorSprite):
    
    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "destination" not in kwargs:
            self.destination = None
        if "empire_color" not in kwargs:
            self.empire_color = (0,0,255)
    
    #def _overwrite_parameters(self):
        #self.empire_color = (0,255,0)
        #self.destination = random.choice(Game.islands)
        
    def create_image(self):
        self.image = pygame.Surface((70,20))
        pygame.draw.rect(self.image, (self.empire_color), (10,5,50,10), 0)
        pygame.draw.rect(self.image, (140,100,20), (15,7,40,6), 0)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.image0 = self.image.copy()
        
    def radar(self):
        """Checks if an island is on a given position"""
        #print(self.destination)
        checkpos = self.pos + self.move*2
        for i in Game.islandgroup:
            if self.destination == i.pos:
                continue
            if distance(i.pos,checkpos) < i.size/2+30:
                #print("Collision!")
                return i        
        
    def find_way(self, island):
        """Calculates the shortest way around an island and returns +1 or -1 depending on the direction"""
        #print(island)
        vector_island_to_destination = self.destination - island.pos #vector island-destination
        nvector_island_to_destination = pygame.math.Vector2(-vector_island_to_destination[1],vector_island_to_destination[0]) #vector with 90° to vector island-destination to the right
        vector_islandradius = nvector_island_to_destination.normalize() * island.size/2 #make nvector island-destination to length radius
        point_a = island.pos + vector_islandradius #calculate the first tangent to island through the destination right to the ship
        point_b = island.pos - vector_islandradius #calculate the second tangent to island through the destination left to the ship
        vector_i_a = vector_islandradius #vector from the middle of the island to point a
        vector_i_b = -vector_islandradius #vector from the middle of the island to point b
        vector_i_ship = self.pos - island.pos #vector from the island to the ship
        angle_a = ((vector_i_ship*vector_i_a)/vector_i_ship.length()*vector_i_a.length()) #angle between vector_i_ship and vector_i_a
        angle_b = ((vector_i_ship*vector_i_b)/vector_i_ship.length()*vector_i_b.length()) #angle between vector_i_ship and vector_i_b
        route_a_length = math.pi * 2 * island.size/2 * (angle_a/360) + (self.destination - point_a).length() #length of route around point a
        route_b_length = math.pi * 2 * island.size/2 * (angle_b/360) + (self.destination - point_b).length() #length of route around point b
        #print(route_a_length,route_b_length)
        if route_a_length <= route_b_length:
            return -1
        else:
            return 1
    
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        island = self.radar()
        if island:
            print("Collision!")
            route = self.find_way(island)
            self.move.rotate_ip(route)
            angle = pygame.math.Vector2(1,0).angle_to(self.move)
            self.set_angle(angle)
        #move_vector = self.move.normalize()
        destination_vector = (self.destination - self.pos)
        #print(self.move, destination_vector)
        #print(self.move.angle_to(destination_vector))
        angle_calculation = (self.move*destination_vector)/((self.move.length())*(destination_vector.length()))
        if angle_calculation > 1:       #minor error in the python calculations cause a number slightly above 1, this leads to gamecrash if you try to get the arccos from it
            angle_calculation = 1
        angle_move_destination = math.degrees(math.acos(angle_calculation))
        if angle_move_destination > 3:
            #print("Nicht auf Kurs")
            if not island:
                #print("Kursabweichung!",)
                newangle_calculation = (self.move.rotate(-1)*destination_vector)/(self.move.rotate(-1).length()*destination_vector.length())
                if newangle_calculation > 1:
                    newangle_calculation = 1
                if math.degrees(math.acos(newangle_calculation)) < angle_move_destination:
                    self.move = self.move.rotate(-1)
                else:
                    self.move = self.move.rotate(1)
                angle = pygame.math.Vector2(1,0).angle_to(self.move)
                self.set_angle(angle)
        


class Viewer(object):
    width = 0
    height = 0
    images={}
    
    
    menu = {"main":      ["Play", "Tutorial", "Levels", "Help", "Credits", "Settings","End the game"],
            "Tutorial":   ["back", "Tutorial 1", "Tutorial 2", "Tutorial 3", "Tutorial 4", "Tutorial 5"],
            "Levels":     ["back", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5"],
            "Help":       ["back"],
            "Credits":    ["back", "Ines Schnabl", "Martin Schnabl", ],
            "Settings":   ["back", "Screenresolution", "Fullscreen"],
            "Resolution": ["back"],
            "Fullscreen": ["back", "True", "False"],
            }
            
            
            
    descr = {"Resume" :           ["Resume to the", "game"],                                           #resume
             "Martin Schnabl" :   ["The programmer of", "this game."],
             "Ines Schnabl":      ["Martin's younger sister", "and responsible for", "the graphics"],
             "Settings" :         ["Change the", "screenresolution", "only in the", "beginning!"],
             "Tutorial 1":        ["An introduction to", "the basics of the", "game"],
             "Tutorial 2":        ["More complex management", "of your ships"],
             "Tutorial 3":        ["Teaches you how", "to build ships", "in the shipyard."],
             "Tutorial 4":        ["Your first encounter", "with enemy ships."],
             "Tutorial 5":        ["Teaches you the", "strategies to win", "the game."],
             }
    menu_images = {"Fluffball" : "fluffball_menu",
                   "Donut"     : "donut_menu",
                   "Cookie"    : "cookie_menu",
                   "Car wheel" : "car wheel_menu",
                   "Cat"       : "baby cat_menu",
                   }
 
    history = ["main"]
    cursor = 0
    name = "main"
    fullscreen = False

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments """
        pygame.init()
        Viewer.width = width    # make global readable
        Viewer.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.click_indicator_time = 0
        self.island_selected = []
        self.end_game = False
        self.newlevel = False
        self.end_gametime = 0
        # ------ background images ------
        self.backgroundfilenames = [] # every .jpg file in folder 'data'
        try:
            for root, dirs, files in os.walk("data"):
                for file in files:
                    if file[-4:] == ".jpg" or file[-5:] == ".jpeg":
                        self.backgroundfilenames.append(file)
            random.shuffle(self.backgroundfilenames) # remix sort order
        except:
            print("no folder 'data' or no jpg files in it")
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        self.prepare_sprites()
        self.loadbackground()
        # --- create screen resolution list ---
        li = ["back"]
        for i in pygame.display.list_modes():
            # li is something like "(800, 600)"
            pair = str(i)
            comma = pair.find(",")
            x = pair[1:comma]
            y = pair[comma+2:-1]
            li.append(str(x)+"x"+str(y))
        Viewer.menu["Screenresolution"] = li
        self.set_screenresolution()

    def loadbackground(self):
        
        #try:
        #    self.background = pygame.image.load(os.path.join("data",
        #         self.backgroundfilenames[Viewer.wave %
        #         len(self.backgroundfilenames)]))
        #except:
        #    self.background = pygame.Surface(self.screen.get_size()).convert()
        #    self.background.fill((255,255,255)) # fill background white
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((0,0,255))
        self.background = pygame.transform.scale(self.background,
                          (Viewer.width,Viewer.height))
        self.background.convert()
        
    def set_screenresolution(self):
        #print(self.width, self.height)
        if Viewer.fullscreen:
             self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF|pygame.FULLSCREEN)
        else:
             self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.loadbackground()
        
    def load_sprites(self):
        pass
        
    def clean_up(self):
        for i in Game.islandgroup:
            i.kill()
        for s in self.shipgroup:
            s.kill()
        for g in Game.groups:
            g.empty()
    
    def new_level(self):
        Game.player_iron = 0
        Game.player_wood = 0
        Game.enemy_iron = 0
        Game.enemy_wood = 0
        self.clean_up()
        
        try: 
            islands = Levels.create_sprites(Game.level)
        except:
            print("-------------------------You won the game------------------------")
            Game.level = 1
            for l in Levels.levels.keys():
                if int(l) <= 0:
                    Game.level -= 1 #for every tutorial level we go one level below 0
            self.menu_run()
        finally:
            islands = Levels.create_sprites(Game.level)

        for x in range(len(islands["Main_islands"])):
            if islands["Main_islands"][x][1] == Game.player_color:
                p_ships = int(islands["Main_islands"][x][2]) + Game.difficulty
            else: 
                p_ships = islands["Main_islands"][x][2]
            Main_Island(pos=pygame.math.Vector2(islands["Main_islands"][x][0]), empire_color = islands["Main_islands"][x][1], ships=p_ships)
        for x in range(len(islands["Iron_islands"])):
            Iron_Island(pos=pygame.math.Vector2(islands["Iron_islands"][x][0]), empire_color = islands["Iron_islands"][x][1], ships=islands["Iron_islands"][x][2])
        for x in range(len(islands["Wood_islands"])):
            Wood_Island(pos=pygame.math.Vector2(islands["Wood_islands"][x][0]), empire_color = islands["Wood_islands"][x][1], ships=islands["Wood_islands"][x][2])
        for x in range(len(islands["Ship_islands"])):
            Ship_Island(pos=pygame.math.Vector2(islands["Ship_islands"][x][0]), empire_color = islands["Ship_islands"][x][1], ships=islands["Ship_islands"][x][2])
        
        for i in Game.islandgroup:
                if i.empire_color == Game.player_color:
                    Game.player_ships += i.ships
                    Game.player_islands += 1
                elif i.empire_color in Game.enemy_color:
                    Game.enemy_ships += i.ships
                    Game.enemy_islands += 1
        
    def prepare_sprites(self):
        """painting on the surface and create sprites"""
        self.load_sprites()
        self.allgroup =  pygame.sprite.LayeredUpdates() # for drawing
        self.explosiongroup = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.Group()
        self.shipgroup = pygame.sprite.Group()
        #self.wood_islandgroup = pygame.sprite.Group()
        #self.iron_islandgroup = pygame.sprite.Group()
        #Game.create_groups()
        VectorSprite.groups = self.allgroup
        Explosion.groups = self.allgroup, self.explosiongroup
        Flytext.groups = self.allgroup, self.flytextgroup
        Spark.groups = self.allgroup
        Ship.groups = self.allgroup, self.shipgroup
        Wood_Island.groups = self.allgroup, Game.islandgroup, Game.wood_islandgroup
        Iron_Island.groups = self.allgroup, Game.islandgroup, Game.iron_islandgroup
        Ship_Island.groups = self.allgroup, Game.islandgroup, Game.ship_islandgroup
        Main_Island.groups = self.allgroup, Game.islandgroup, Game.main_islandgroup
        
        self.new_level()
        
    def startmenu_run(self):
        running = True
        while running:
            #pygame.mixer.music.pause()
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            text = Viewer.startmenu[Viewer.name][Viewer.cursor]
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1 # running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return -1 # running = False
                    if event.key == pygame.K_UP:
                        Viewer.cursor -= 1
                        Viewer.cursor = max(0, Viewer.cursor) # not < 0
                        #Viewer.menusound.play()
                    if event.key == pygame.K_DOWN:
                        Viewer.cursor += 1
                        Viewer.cursor = min(len(Viewer.startmenu[Viewer.name])-1,Viewer.cursor) # not > menu entries
                        #Viewer.menusound.play()
                    if event.key == pygame.K_RETURN:
                        if text == "quit":
                            return -1
                            Viewer.menucommandsound.play()
                        elif text in Viewer.startmenu:
                            # changing to another menu
                            Viewer.history.append(text) 
                            Viewer.name = text
                            Viewer.cursor = 0
                        elif text == "Resume":
                            return
                        elif text == "back":
                            Viewer.history = Viewer.history[:-1] # remove last entry
                            Viewer.cursor = 0
                            Viewer.name = Viewer.history[-1] # get last entry
                        elif Viewer.name == "Screenresolution":
                            # text is something like 800x600
                            t = text.find("x")
                            if t != -1:
                                x = int(text[:t])
                                y = int(text[t+1:])
                                Viewer.width = x
                                Viewer.height = y
                                self.set_screenresolution()
                                self.prepare_sprites()
                        elif Viewer.name == "Levels":
                            Game.level = int(text[-1])
                            self.new_level()
                        elif Viewer.name == "Tutorial":
                            Game.level = -(int(text[-1]))
                            self.new_level()
                        elif Viewer.name == "Fullscreen":
                            if text == "True":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = True
                                self.set_screenresolution()
                            elif text == "False":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = False
                                self.set_screenresolution()
                            
                        
            # ------delete everything on screen-------
            self.screen.blit(self.background, (0, 0))
            
            # -------------- UPDATE all sprites -------             
            self.flytextgroup.update(seconds)

            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)
            
            
            pygame.draw.rect(self.screen,(170,170,170),(200,90,350,350))
            pygame.draw.rect(self.screen,(200,200,200),(600,90,350,350))
            pygame.draw.rect(self.screen,(230,230,230),(1000,90,350,350))
            
            self.flytextgroup.draw(self.screen)

            # --- paint menu ----
            # ---- name of active menu and history ---
            write(self.screen, text="you are here:", x=200, y=50, color=(0,255,255), fontsize=15)
            
            t = "main"
            for nr, i in enumerate(Viewer.history[1:]):
                #if nr > 0:
                t+=(" > ")
                t+=(i)
            write(self.screen, text=t, x=200,y=70,color=(0,255,255), fontsize=15)
            # --- menu items ---
            menu = Viewer.startmenu[Viewer.name]
            for y, item in enumerate(menu):
                write(self.screen, text=item, x=Viewer.width//2-500, y=100+y*50, color=(255,255,255), fontsize=30)
            # --- cursor ---
            write(self.screen, text="-->", x=Viewer.width//2-600, y=100+ Viewer.cursor * 50, color=(0,0,0), fontsize=30)
            # ---- descr ------
            if text in Viewer.descr:
                lines = Viewer.descr[text]
                for y, line in enumerate(lines):
                    write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
           # ---- menu_images -----
            if text in Viewer.menu_images:
                self.screen.blit(Viewer.images[Viewer.menu_images[text]], (1020,100))
                
            # -------- next frame -------------
            pygame.display.flip()

    def menu_run(self):
        """Not The mainloop"""
        running = True
        #pygame.mouse.set_visible(False)
        self.menu = True
        while running:
            #pygame.mixer.music.pause()
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            text = Viewer.menu[Viewer.name][Viewer.cursor]
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.quit_game = True
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_UP:
                        Viewer.cursor -= 1
                        Viewer.cursor = max(0, Viewer.cursor) # not < 0
                        #Viewer.menusound.play()
                    if event.key == pygame.K_DOWN:
                        Viewer.cursor += 1
                        Viewer.cursor = min(len(Viewer.menu[Viewer.name])-1,Viewer.cursor) # not > menu entries
                        #Viewer.menusound.play()
                    if event.key == pygame.K_RETURN:
                        if text == "End the game":
                            Game.quit_game = True
                            running = False
                        elif text in Viewer.menu:
                            # changing to another menu
                            Viewer.history.append(text) 
                            Viewer.name = text
                            Viewer.cursor = 0
                        elif text == "Play":
                            running = False
                        elif text == "back":
                            Viewer.history = Viewer.history[:-1] # remove last entry
                            Viewer.cursor = 0
                            Viewer.name = Viewer.history[-1] # get last entry
                        elif Viewer.name == "Screenresolution":
                            # text is something like 800x600
                            t = text.find("x")
                            if t != -1:
                                x = int(text[:t])
                                y = int(text[t+1:])
                                Viewer.width = x
                                Viewer.height = y
                                self.set_screenresolution()
                                self.prepare_sprites()
                        elif Viewer.name == "Levels":
                            Game.level = int(text[-1])
                            self.new_level()
                            running = False
                        elif Viewer.name == "Tutorial":
                            t = 0
                            for l in Levels.levels.keys():
                                if int(l) <= 0:
                                    t += 1
                            Game.level = (int(text[-1]))-t
                            self.new_level()
                            running = False
                        elif Viewer.name == "Fullscreen":
                            if text == "True":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = True
                                self.set_screenresolution()
                            elif text == "False":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = False
                                self.set_screenresolution()
                            
                        
            # ------delete everything on screen-------
            self.screen.blit(self.background, (0, 0))
            
            # -------------- UPDATE all sprites -------             
            self.flytextgroup.update(seconds)

            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)
            
            
            pygame.draw.rect(self.screen,(170,170,170),(200,90,350,350))
            pygame.draw.rect(self.screen,(200,200,200),(600,90,350,350))
            pygame.draw.rect(self.screen,(230,230,230),(1000,90,350,350))
            
            self.flytextgroup.draw(self.screen)

            # --- paint menu ----
            # ---- name of active menu and history ---
            write(self.screen, text="you are here:", x=200, y=50, color=(0,255,255), fontsize=15)
            
            t = "main"
            for nr, i in enumerate(Viewer.history[1:]):
                #if nr > 0:
                t+=(" > ")
                t+=(i)
            write(self.screen, text=t, x=200,y=70,color=(0,255,255), fontsize=15)
            # --- menu items ---
            menu = Viewer.menu[Viewer.name]
            for y, item in enumerate(menu):
                write(self.screen, text=item, x=Viewer.width//2-500, y=100+y*50, color=(255,255,255), fontsize=30)
            # --- cursor ---
            write(self.screen, text="-->", x=Viewer.width//2-600, y=100+ Viewer.cursor * 50, color=(0,0,0), fontsize=30)
            # ---- descr ------
            if text in Viewer.descr:
                lines = Viewer.descr[text]
                for y, line in enumerate(lines):
                    write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
           # ---- menu_images -----
            if text in Viewer.menu_images:
                self.screen.blit(Viewer.images[Viewer.menu_images[text]], (1020,100))
                
            # -------- next frame -------------
            pygame.display.flip()
    
    def run(self):
        """The mainloop"""
        running = True
        Viewer.fullscreen = False
        self.set_screenresolution()
        #pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright  = False, False, False
        self.snipertarget = None
        gameOver = False
        exittime = 0
        self.menu_run()
        running = True
    
        while running:
            if Game.quit_game:
                running = False
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            self.playtime += seconds
            
            if gameOver:
                if self.playtime > exittime:
                    running = False
                    
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_m:
                        running = self.menu_run()
                        if running is None:
                            running = True
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))  # macht alles weiß

            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()

            # write text below sprites
            write(self.screen, "FPS: {:8.3}".format(
                self.clock.get_fps() ), x=10, y=10)
            write(self.screen, "Wood = {:.0f}".format(Game.player_wood), x=10,y=30)
            write(self.screen, "Iron = {:.0f}".format(Game.player_iron), x=10,y=50)
            write(self.screen, "Ships = {:.0f}".format(Game.player_ships), x=10,y=80)
            level = Game.level
            if level <= 0:
                for l in Levels.levels.keys():
                    if int(l) <= 0:
                        level += 1
                write(self.screen, "Tutorial {}".format(level), x=1280, y=30)
            else:
                write(self.screen, "Level {}".format(level), x=1280, y=30)
            #write(self.screen, "Iron = {:.0f}".format(Game.player_iron), x=10,y=50)
            
            for i in Game.islandgroup:
                 write(self.screen, "{}".format(i.ships), x=i.pos[0], y=-i.pos[1],  fontsize=i.size//5, color=(255,0,0))
            self.allgroup.update(seconds)
            
            # -------------- write explanations for the current level on the screen ------------------
            if str(Game.level) in Levels.level_descriptions.keys():
                for x in range(len(Levels.level_descriptions[str(Game.level)])):
                    #print(x)
                    write(self.screen, Levels.level_descriptions[str(Game.level)][x], x=200, y=50+x*25)

            # ------------------win or lose --------------------
            Game.player_ships = 0
            Game.player_islands = 0
            Game.enemy_ships = 0
            Game.enemy_islands = 0
            for i in Game.islandgroup:
                if i.empire_color == Game.player_color:
                    Game.player_ships += i.ships
                    Game.player_islands += 1
                elif i.empire_color in Game.enemy_color:
                    Game.enemy_ships += i.ships
                    Game.enemy_islands += 1
            for s in self.shipgroup:
                if s.empire_color == Game.player_color:
                    Game.player_ships += 1
                elif s.empire_color in Game.enemy_color:
                    Game.enemy_ships += 1
            #print(Game.level, self.newlevel)
            if self.end_gametime < self.playtime:
                if self.newlevel == True:
                    self.newlevel = False
                    Game.level += 1
                    self.new_level()
                elif self.end_game == True:
                    break
                elif Game.enemy_ships == 0 and Game.enemy_islands == 0:
                    Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "You won the level!", fontsize=30, color=Game.player_color)
                    self.end_gametime = self.playtime + 5
                    self.newlevel = True
                elif Game.player_ships == 0 and Game.player_islands == 0:
                    Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "You lose!", fontsize=30, color=random.choice(Game.enemy_color))
                    self.end_gametime = self.playtime + 5
                    self.end_game == True
            # ------------------ click on island ---------------
            left,middle,right = pygame.mouse.get_pressed()
            if oldleft and not left:
                mouse_pos = pygame.mouse.get_pos()
                for i in Game.islandgroup:
                    dist = distance((i.pos[0],i.pos[1]), (mouse_pos[0],-mouse_pos[1]))
                    #v = i.pos - pygame.math.Vector2(mouse_pos[0], mouse_pos[1])
                    #dist = v.length
                    #print("dist:" ,dist)
                    if dist < i.size//2:
                        # -------------- send ship ----------------
                        if len(self.island_selected) != 0: #Island selected?
                            for s in Game.islandgroup: #Which island is selected?
                                if (self.island_selected[0],self.island_selected[1]) == s.pos:
                                    if distance((self.island_selected[0],self.island_selected[1]), i.pos) != 0: #is selected island != target island?
                                        if s.empire_color == Game.player_color: #is it your island?
                                            if s.ships > 0: #are there any ships?
                                                s.ships -= 1
                                                v = i.pos - pygame.math.Vector2(s.pos.x, s.pos.y)
                                                m = v.normalize() * 30
                                                move = pygame.math.Vector2(m)
                                                start = v.normalize() * (s.size//2 + 25)# 25 = length of ship
                                                e = pygame.math.Vector2(1,0)
                                                angle = e.angle_to(m)
                                                Ship(pos=pygame.math.Vector2(self.island_selected[0],self.island_selected[1])+start, destination=i.pos, move=move, angle=angle, empire_color=s.empire_color)
                        # ----------------- select island ---------------
                        else:
                            self.island_selected = [i.pos[0],i.pos[1],i.size,i.ships]
                            self.click_indicator_time = self.playtime + 5
                        break
                else:
                    self.click_indicator_time = 0
                    self.island_selected = []
            oldleft, oldmiddle, oldright = left, middle, right
            
            #m = pygame.mouse.get_pressed()
            #if m[0]:
                
            if self.playtime < self.click_indicator_time:
                pygame.draw.circle(self.screen, (100,100,100), (int(self.island_selected[0]),-int(self.island_selected[1])), self.island_selected[2]//2+10)
            else:
                self.island_selected = []


            #-----------collision detection ------
            for i in Game.islandgroup:
                crashgroup = pygame.sprite.spritecollide(i, self.shipgroup,
                             False, pygame.sprite.collide_mask)
                for s in crashgroup:
                    if i.pos == s.destination:
                        if i.empire_color == s.empire_color:
                            i.ships += 1
                            s.kill()
                        else:
                            if i.ships != 0:
                                i.ships -= 1
                                s.kill()
                            else:
                                i.empire_color = s.empire_color
                                i.ships += 1
                                i.create_image()
                                i.rect=i.image.get_rect()
                                i.rect.center=(i.pos.x, -i.pos.y)
                                s.kill()
            
            #print(Game.main_islandgroup)

                    
                            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)
            for i in Game.islandgroup:
                 write(self.screen, "{}".format(i.ships), x=i.pos[0]+i.size//2-15, y=-i.pos[1]+i.size//5+15,  fontsize=i.size//5, color=(i.empire_color))
                        
            # -------- next frame -------------
            pygame.display.flip()
        #-----------------------------------------------------
        pygame.mouse.set_visible(True)    
        pygame.quit()

if __name__ == '__main__':
    Viewer(1430,800).run()
