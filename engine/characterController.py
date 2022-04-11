import asyncio
import json
import math
import time
import threading
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
        self.imageattack = None
        self.imagereg = self.game.loadimage(imgpath)
        self.imageattacked = None
        
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
        self.cooldown: int = 0

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

    def check(self,status=False):
        if self.alive and self.canattack is True and status is False:
            return True

    def timercooldown(self):
        self.cooldown = 1
        for i in range(1):
            time.sleep(1)
            self.cooldown -= 1

    def draw(self):
        self.game._window.blit(self.image, self.rect)

    def update(self, collisionBoxes, playerlist):
        hits = pg.sprite.spritecollide(self, collisionBoxes, False)

        if hits:
            self.jum = 2
            self.pos.y = hits[0].rect.top + 1
            self.vel.y = 0

    def move(self, status):
        if self.check(status):
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

    def attk(self, binding) -> bool:
        if self.cooldown == 0:
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

                damageTypes = self.damagetypes()

                if distance <= 175:
                    t1 = threading.Thread(target=self.timercooldown)
                    t1.setDaemon(True)
                    t1.start()
                    self.image = self.imageattack
                    if self.bind == "wasd":
                        todamage = binding["arrow"]
                        damage = damageTypes.chooseRandomType()
                        health_remaining = todamage.damage(damage) 
                        lives = todamage.lives

                        with open("../assets/resources/json/gameValues.json", "r") as f:
                            dataIn = json.loads(f.read())
                            f.close()

                        if health_remaining is not None:
                            if health_remaining > 0:
                                dataIn["healthValues"]["P2"] = health_remaining
                                dataIn["lives"]["P2"] = lives   

                            elif health_remaining <= 0:
                                dataIn["healthValues"]["P2"] = 0
                                dataIn["lives"]["P2"] = lives

                        elif health_remaining is None:
                            health_remaining = 0

                        with open("../assets/resources/json/gameValues.json", "w") as f:
                            f.write(json.dumps(dataIn))
                            f.close()

                    if self.bind == "arrow":
                        todamage = binding["wasd"]
                        damage = damageTypes.chooseRandomType()
                        health_remaining = todamage.damage(damage)
                        lives = todamage.lives

                        with open("../assets/resources/json/gameValues.json", "r") as f:
                            dataIn = json.loads(f.read())
                            f.close()

                        if health_remaining > 0:
                            dataIn["healthValues"]["P1"] = health_remaining
                            dataIn["lives"]["P1"] = lives

                        elif health_remaining <= 0:
                            dataIn["healthValues"]["P1"] = 0
                            dataIn["lives"]["P1"] = lives

                        with open("../assets/resources/json/gameValues.json", "w") as f:
                            f.write(json.dumps(dataIn))
                            f.close()

                    self.image = self.imagereg
                    if distance <= 175:
                        landed = True
                    else:
                        landed = False
                    return landed

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

    TESTMAPPLATY = 800
    OUTBACKY = 690
    ATLANTISY = 800

    def __init__(self):  
        super().__init__()
        self.surf = pg.Surface((self.game.dimensions[0], 10))
        self.surf.fill((127, 33, 33))
        self.surf.set_colorkey((127, 33, 33))
        self.surf.set_alpha(100)
        self.rect = self.surf.get_rect(center = (self.x/2, self.OUTBACKY))
    
    def draw(self):
        self.game._window.blit(self.surf, self.rect)

class GameOverOverlay(pg.sprite.Sprite):
    game = control.game
    x, y = game.dimensions

    def __init__(self):
        self.surf = pg.Surface(self.game.dimensions)
        self.surf.fill((0, 0, 0, 255))
        self.surf.set_alpha(127)
        self.rect = self.surf.get_rect(center = (self.x/2, self.y/2))

    def draw(self):
        self.game._window.blit(self.surf, self.rect)
#patrice = Character("Andrew", "", "")
#damageTypes = patrice.damagetypes()
#for i in range(100):
    #type = damageTypes.chooseRandomType()
    #patrice.damage(type)
