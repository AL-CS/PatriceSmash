import itertools
from numpy import random
import pygame as pg
import main as control

class Character(pg.sprite.Sprite):
    """
    Represents a character builder
    """
    def __init__(self, name, lives):
        print("init")
        self.surf = pg.Surface((30,30))
        self.surf.fill((control.get_game().Colors.RED))
        self.rect = self.surf.get_rect(center=(10,420))

        self.idle: pg.Surface = None
        self.running: pg.Surface = None
        self.attack: pg.Surface = None 

        self.game = control.get_game()       
        self.health: float = 250
        self.name: str = name
        self.alive: bool = True
        self.lives: int = lives

    class Platform(pg.sprite.Sprite):
        game = control.get_game()
        def __init__(self):  
            self.surf = pg.Surface((self.game.dimensions[0], 20))
            self.surf.fill(self.game.Colors)
    
    class damagetypes():
        HEAVY = "heavy"
        LIGHT = "light"

        def chooseRandomType(self):
            probs = [.75, .25]
            types = [self.LIGHT, self.HEAVY]

            randomType = random.choice(types, p=probs)
            return randomType

    def damage(self, type, custom: float = None):

        if self.alive is True:
            if custom is None:
                if type == "heavy":
                    randomDamage = random.uniform(20.0, 30.0)
                elif type == "light":
                    randomDamage = random.uniform(5.0, 15.0)
            else:
                randomDamage = custom
            self.health -= randomDamage
            print(self.health)

            if self.health <= 0:
                if self.lives > 1:
                    self.lives -= 1
                    self.health = 250

                    print(f"{self.name} has {self.lives} lives left!")

                elif self.lives <= 1:
                    self.alive = False
                    self.health = 0
                    self.lives = 0

                    print(f"{self.name} died!")

patrice = Character("Andrew", 3)
damageTypes = patrice.damagetypes()
for i in range(100):
    type = damageTypes.chooseRandomType()
    patrice.damage(type)
