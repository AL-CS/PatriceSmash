import asyncio
import math
import time
from numpy import character, random
import pygame as pg
import main as control

class Character(pg.sprite.Sprite):
    """
    Represents a character builder
    """

    game = control.game
    vec = game.vec
    x, y = (1920, 1080)

    def __init__(self, name, power, desc, imgpath):
        super().__init__()
        self.imageattack = self.game.loadimage("attack.png")
        self.imagereg = self.game.loadimage(imgpath)
        self.imageattacked = self.game.loadimage("attacked.png")

        self.image = self.imagereg
        self.rect = self.image.get_rect(center=((self.x/2), (self.y/2)))

        self.idle: pg.Surface = None
        self.running: pg.Surface = None
        self.attack: pg.Surface = None 

        self.health: float = 250
        self.name: str = name
        self.alive: bool = True
        self.canattack: bool = True
        self.lives: int = 3
        self.bind = None

        # movement vars
        self.jum = 2
        self.pos = self.vec((self.x/2, 385))
        self.vel = self.vec(0,0)
        self.acc = self.vec(0,0)
        
    class damagetypes():
        HEAVY = "heavy"
        LIGHT = "light"

        def chooseRandomType(self):
            probs = [.75, .25]
            types = [self.LIGHT, self.HEAVY]

            randomType = random.choice(types, p=probs)
            return randomType

    def initChar(self): 
        if self.bind is not None:
            if self.bind == "wasd":
                self.pos.x = 225
            elif self.bind == "arrow":
                self.pos.x = 1693

    def check(self):
        if self.alive and self.canattack is True:
            return True

    def draw(self):
        self.game._window.blit(self.image, self.rect)

    def update(self, collisionBoxes, playerlist):
        hits = pg.sprite.spritecollide(self, collisionBoxes, False)

        if hits:
            self.jum = 2
            self.pos.y = hits[0].rect.top + 1
            self.vel.y = 0

    def move(self):
        if self.check():
            self.acc = self.vec(0,1.5)
            pressedKeys = pg.key.get_pressed()
            if self.bind == "arrow":
                if pressedKeys[pg.K_LEFT]:
                    self.acc.x = -self.game.ACC
                if pressedKeys[pg.K_RIGHT]:
                    self.acc.x = self.game.ACC
            elif self.bind == "wasd":
                if pressedKeys[pg.K_a]:
                    self.acc.x = -self.game.ACC
                if pressedKeys[pg.K_d]:
                    self.acc.x = self.game.ACC

            self.acc.x += self.vel.x * self.game.FRIC
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc

            if self.pos.x > 1703:
                self.pos.x = 1703
            if self.pos.x < 215:
                self.pos.x = 215
            self.rect.midbottom = self.pos


    def attk(self, binding):
        if self.check():
            health_remaining = None
            lives = None
            if self.bind == "wasd":
                enemy = binding["arrow"]
            elif self.bind == "arrow":
                enemy = binding["wasd"]

            enpos = enemy.pos
            pos = self.pos

            distance = math.sqrt((enpos.x - pos.x) ** 2 + (enpos.y - pos.y) ** 2)
            print(distance)

            damageTypes = self.damagetypes()

            if distance <= 175:
                self.image = self.imageattack
                if self.bind == "wasd":
                    todamage = binding["arrow"]
                    damage = damageTypes.chooseRandomType()
                    health_remaining = todamage.damage(damage) 
                    lives = todamage.lives

                    self.canattack = False
                    todamage.canattack = False
                    self.canattack = True
                    todamage.canattack = True

                if self.bind == "arrow":
                    todamage = binding["wasd"]
                    damage = damageTypes.chooseRandomType()
                    health_remaining = todamage.damage(damage)
                    lives = todamage.lives

                    self.canattack = False
                    todamage.canattack = False
                    self.canattack = True
                    todamage.canattack = True

                self.image = self.imagereg
            return health_remaining, lives

    def jump(self):
        if self.check():
            self.jum -= 1
            if self.jum >= 0:
                self.vel.y = -30
    
    def damage(self, type, custom: float = None):
        if self.check():
            if self.alive is True:
                if custom is None:
                    if type == "heavy":
                        randomDamage = random.uniform(20.0, 30.0)
                    elif type == "light":
                        randomDamage = random.uniform(5.0, 15.0)
                else:
                    randomDamage = custom
                self.health -= randomDamage
                self.image = self.imageattacked
                print(self.health)

                if self.health < 1:
                    if self.lives > 1:
                        self.lives -= 1
                        self.health = 250


                        if self.bind == "wasd":
                            self.canattack = False
                            self.pos = self.vec((225, 385))
                            self.canattack = True

                        elif self.bind == "arrow":
                            self.canattack = False
                            self.pos = self.vec((1693, 385))    
                            self.canattack = True

                        print(f"{self.name} has {self.lives} lives left!")

                    elif self.lives <= 1:
                        self.alive = False
                        self.health = 0
                        self.lives = 0

                        self.alive = False
                        self.kill()
                        print(f"{self.name} died!")
                self.image = self.imagereg
                return self.health

class Platform(pg.sprite.Sprite):
    game = control.game
    x, y= game.dimensions
    def __init__(self):  
        super().__init__()
        self.surf = pg.Surface((self.game.dimensions[0], 10))
        self.surf.fill((127, 33, 33))
        self.surf.set_colorkey((127, 33, 33))
        self.surf.set_alpha(100)
        self.rect = self.surf.get_rect(center = (self.x/2, 800))
    
    def draw(self):
        self.game._window.blit(self.surf, self.rect)

#patrice = Character("Andrew", "", "")
#damageTypes = patrice.damagetypes()
#for i in range(100):
    #type = damageTypes.chooseRandomType()
    #patrice.damage(type)
