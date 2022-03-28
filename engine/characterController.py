import random
import itertools
from numpy import datetime_as_string
import pygame as pg
import main as control

class Character(pg.sprite.Sprite):
    """
    Represents a character builder
    """
    def __init__(self, name, lives):
        self.idle: pg.Surface = None
        self.running: pg.Surface = None
        self.attack: pg.Surface = None 

        self.game = control.get_game()       
        self.health: float = 250
        self.name: str = name
        self.alive: bool = True
        self.lives: int = lives
    
    class damagetypes():
        HEAVY = "heavy"
        LIGHT = "light"

    def damage(self, type: damagetypes, custom: float = None):

        if self.alive is True:
            if custom is None:
                if type is self.damagetypes.HEAVY:
                    randomDamage = random.uniform(20.0, 30.0)
                elif type is self.damagetypes.LIGHT:
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

patrice = Character("Patrice", 3)
for i in range(100):
    patrice.damage(Character.damagetypes.HEAVY)
