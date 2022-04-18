import json
import math
import time
import threading
from numpy import random
import pygame as pg
import main as control

class Character(pg.sprite.Sprite):
    """
    Represents a character builder
    """

    # define game specific values
    game = control.game
    vec = game.vec
    x, y = (1920, 1080)

    # init character builder
    def __init__(self, name, desc, imgpath, bind):
        super().__init__()
        self.imageattack = True

        self.imageRight = self.game.loadimage(f"{imgpath}right.png")
        self.imageLeft = self.game.loadimage(f"{imgpath}left.png")
        
        #check if character has attack poses
        try:
            self.imagePunchRight = self.game.loadimage(f"{imgpath}right_attack.png")
            self.imagePunchLeft = self.game.loadimage(f"{imgpath}left_attack.png")
        except:
            self.imageattack = False

        #bind character and image
        if bind == "wasd":
            self.imagereg = self.imageRight
            self.currentOrientation = "right"
        elif bind == "arrow":
            self.imagereg = self.imageLeft
            self.currentOrientation = "left"
        
        self.image = self.imagereg
        self.rect = self.image.get_rect(center=((self.x/2), (self.y/2)))

        # more variables
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
        self.yieldingForThread = False
        self.jum = 2
        self.pos = self.vec((self.x/2, 385))
        self.vel = self.vec(0,0)
        self.acc = self.vec(0,0)
        
    # standardized damage types and probability function
    class damagetypes():
        HEAVY = "heavy"
        LIGHT = "light"

        def chooseRandomType(self):
            probs = [.75, .25]
            types = [self.LIGHT, self.HEAVY]

            randomType = random.choice(types, p=probs)
            return randomType

    # place character based on binding
    def initChar(self): 
        if self.bind is not None:
            if self.bind == "wasd":
                self.pos.x = 225
            elif self.bind == "arrow":
                self.pos.x = 1693

    # check function
    def check(self,status=False):
        if self.alive and self.canattack is True and status is False:
            return True

    # threaded timer cooldown function to prevent spam attacks
    def timercooldown(self):
        self.cooldown = 1
        for i in range(1):
            time.sleep(1)
            self.cooldown -= 1

    # switches character orientation image to attack within a thread to not yield game loop
    def switchtoattackimg(self):
        if self.currentOrientation == "right":
            self.image = self.imagePunchRight
            self.yieldingForThread = True
            time.sleep(.75)
            self.image = self.imageRight
            self.yieldingForThread = False
        elif self.currentOrientation == "left":
            self.image = self.imagePunchLeft
            self.yieldingForThread = True
            time.sleep(.75)
            self.image = self.imageLeft
            self.yieldingForThread = False

    # draw character function
    def draw(self):
        self.game._window.blit(self.image, self.rect)

    # determine if character is colliding with any collision boxes
    def update(self, collisionBoxes, playerlist):
        hits = pg.sprite.spritecollide(self, collisionBoxes, False)

        if hits:
            self.jum = 2
            self.pos.y = hits[0].rect.top + 1
            self.vel.y = 0

    # move character and change image based on key
    def move(self, status):
        if self.check(status):
            self.acc = self.vec(0,1.5)
            pressedKeys = pg.key.get_pressed()
            if self.bind == "arrow":
                if pressedKeys[pg.K_LEFT]:
                    self.currentOrientation = "left"
                    self.acc.x = -self.game.ACC
                    if self.yieldingForThread is False:
                        self.image = self.imageLeft
                if pressedKeys[pg.K_RIGHT]:
                    self.currentOrientation = "right"
                    self.acc.x = self.game.ACC
                    if self.yieldingForThread is False:
                        self.image = self.imageRight
            elif self.bind == "wasd":
                if pressedKeys[pg.K_a]:
                    self.currentOrientation = "left"
                    self.acc.x = -self.game.ACC
                    if self.yieldingForThread is False:
                        self.image = self.imageLeft
                if pressedKeys[pg.K_d]:
                    self.currentOrientation = "right"
                    self.acc.x = self.game.ACC
                    if self.yieldingForThread is False:
                        self.image = self.imageRight

            # core physics engine functions
            self.acc.x += self.vel.x * self.game.FRIC
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc

            # map bordering
            if self.pos.x > 1703:
                self.pos.x = 1703
            if self.pos.x < 215:
                self.pos.x = 215
            self.rect.midbottom = self.pos

    # attack function
    def attk(self, binding) -> bool:
        if self.cooldown == 0:
            if self.check():
                health_remaining = None
                lives = None
                if self.bind == "wasd":
                    enemy = binding["arrow"]
                elif self.bind == "arrow":
                    enemy = binding["wasd"]
                
                # thread image attack so game is not yielded
                if self.imageattack is True:
                    t1 = threading.Thread(target=self.switchtoattackimg)
                    t1.setDaemon(True)
                    t1.start()

                enpos = enemy.pos
                pos = self.pos
                landed = False
                died = False

                # determine distance between cords
                distance = math.sqrt((enpos.x - pos.x) ** 2 + (enpos.y - pos.y) ** 2)

                damageTypes = self.damagetypes()

                # run if character is within attacking distance
                if distance <= 250:
                    t1 = threading.Thread(target=self.timercooldown)
                    t1.setDaemon(True)
                    t1.start()
                    if self.bind == "wasd":
                        todamage = binding["arrow"]
                        damage = damageTypes.chooseRandomType()
                        data = todamage.damage(damage) 
                        health_remaining = data[0]
                        died = data[1]
                            
                        lives = todamage.lives

                        # read health values
                        with open("../assets/resources/json/gameValues.json", "r") as f:
                            dataIn = json.loads(f.read())
                            f.close()

                        if health_remaining is not None:
                            print(health_remaining)
                            if health_remaining > 0:
                                dataIn["healthValues"]["P2"] = health_remaining
                                dataIn["lives"]["P2"] = lives   

                            elif health_remaining <= 0:
                                dataIn["healthValues"]["P2"] = 0
                                dataIn["lives"]["P2"] = lives

                        elif health_remaining is None:
                            health_remaining = 0

                        # write health values
                        with open("../assets/resources/json/gameValues.json", "w") as f:
                            f.write(json.dumps(dataIn))
                            f.close()

                    if self.bind == "arrow":
                        todamage = binding["wasd"]
                        damage = damageTypes.chooseRandomType()
                        data = todamage.damage(damage)
                        health_remaining = data[0]
                        died = data[1]
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

                    if distance <= 250:
                        landed = True
                    else:
                        landed = False
                # return values to main game file
                return (landed, died)

    # jump function
    def jump(self):
        if self.check():
            self.jum -= 1
            if self.jum >= 0:
                self.vel.y = -29

    # client side damage function which determines random probablity and checks lives to determine death
    def damage(self, type, custom: float = None):
        died = False
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

                # reduce lives if health is below 1
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

                        # play death effect and print console debugging
                        self.game.playIfActive(self.game._deathSoundEffect)
                        print(f"{self.name} has {self.lives} lives left!")

                    elif self.lives <= 1:
                        self.alive = False
                        self.health = 0
                        self.lives = 0

                        self.alive = False
                        # kill sprite and end game
                        self.kill()
                        print(f"{self.name} died!")
                        died = True
                return self.health, died

# define platform to stand on
class Platform(pg.sprite.Sprite):
    game = control.game
    x, y= game.dimensions

    # saved dimensions for Y value on individual maps
    SAVEDDIMENSIONS = {"testmap": 800, "outback": 690, "atlantis": 770, "bathroom": 760, "classroom": 720}

    # init platform data
    def __init__(self, selectedMap):  
        super().__init__()
        self.surf = pg.Surface((self.game.dimensions[0], 10))
        self.surf.fill((127, 33, 33))
        self.surf.set_colorkey((127, 33, 33))
        self.surf.set_alpha(100)
        selectedMapYValue = self.SAVEDDIMENSIONS[selectedMap["name"].lower()]

        self.rect = self.surf.get_rect(center = (self.x/2, selectedMapYValue))
    
    def draw(self):
        self.surf.set_alpha(128)
        self.game._window.blit(self.surf, self.rect)

# game overlay used for menu and gameover functions
class GameOverOverlay(pg.sprite.Sprite):
    game = control.game
    x, y = game.dimensions

    def __init__(self):
        self.surf = pg.Surface(self.game.dimensions)
        self.surf.fill((0, 0, 0, 255))
        self.surf.set_alpha(150)
        self.rect = self.surf.get_rect(center = (self.x/2, self.y/2))

    def draw(self):
        self.game._window.blit(self.surf, self.rect)