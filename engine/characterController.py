import pygame as pg
import main as control

class Character(pg.sprite.Sprite):
    """
    Represents a character builder
    """
    def __init__(self, name, health, lives):
        self.idle: pg.Surface = None
        self.running: pg.Surface = None
        self.attack: pg.Surface = None 

        self.game = control.get_game()       
        self.health: float = None
        self.name: str = None
        self.alive: bool = True
        self.lives: int = None

patrice = Character("Patrice", 100, 3, )