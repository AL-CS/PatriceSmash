import csv
from time import sleep
import pygame as pg
from pygame.rect import *

import pygame_widgets as pgw
from pygame_widgets.button import Button

class Game():
    
    """
    Main game class holding major functions and variables
    """
    _running = False
    _playrunning = False
    _optionsrunning = False
    _creditsrunning = False

    def __init__(self):
        
        
        self.BACKGROUND = self.loadimage("../assets/art/background.png")
        self.framerate: int = None
        self.name: str = None
        self.dimensions: tuple = None
        # self.icon: pg.Surface = None

        self._clock = pg.time.Clock()

        self._status = "main"
        self._selected = "play"

        self._WHITE = (255, 255, 255)
        self._RED = (255, 0, 0)
        self._GREEN = (0, 225, 0)
        self._BLUE = (0, 0, 225)
        self._BLACK = (0, 0, 0)

    def loadimage(self, image: str):
        """
        Function to return an image by filename passed a string in the pygame Surface format
        """
        img = pg.image.load(image)
        return img
    
    def loadcsv(self, location):
        """
        Loads CSV file as dictonary list from relative or absolute location
        """
        final = []
        with open(location, 'r') as data:
            for line in csv.DictReader(data):
                final.append(line)
        return final

    def compileCSVList(self, loadedcsv: list):
        """
        Take CSV file list as input (self.loadcsv(location))
        and output nested list
        """

        csvOut = []

        for line in loadedcsv:
            temp = []
            for value in line.values():
                temp.append(value)   

            csvOut.append(temp)        
        return csvOut 

    def run(self):
        """
        Function to run game
        """
        
        if self._running is not True and self.framerate and self.name and self.dimensions:
            pg.init()
            self._window = pg.display.set_mode(self.dimensions)
            pg.display.set_caption(self.name)
            # pg.display.set_icon(self.icon)
            self._running = True
            self._mainloop()

            print("Game loop started.")
        else:
            print("You have not initialized the game correctly, or the game is already running!")


    def get(self, var: str):
        """
        Gets and returns private vars
        """
        if var.lower() == "framerate":
            return self.framerate
        elif var.lower() == "name":
            return self.name
        elif var.lower() == "dimensions":
            return self.dimensions
        elif var.lower() == "running":
            return self._running
        elif var.lower() == "clock":
            return self._clock
        elif var.lower() == "game":
            return self

    def getfont(self, fontname: str, size: int):
        """
        Takes font name and size and returns system font
        """
        status = pg.font.get_init()

        if (status is False):
            pg.font.init()

        font = pg.font.Font(fontname, size)
        return font
    
    def renderfont(self, font, text: str, antialias: bool, color: tuple, backgroundcolor: tuple = None):
        """
        Renders font object as an image
        """
        if (backgroundcolor is not None):
            text = font.render(text, antialias, color, backgroundcolor)

        elif (backgroundcolor is None):
            text = font.render(text, antialias, color)

        return text

    def displaytext(self, text, position: tuple = (0, 0)):
        """
        Takes text surface object and displays it on specific position tuple if provided.
        """
        self._window.blit(text, position)

    def _mainloop(self):
        """
        Main menu loop
        """

        self._selected = "play"

        pg.mouse.set_visible(False)
        x, y = self.dimensions

        arcade_90 = self.getfont("../assets/resources/fonts/arcade.ttf", 90)
        arcade_72 = self.getfont("../assets/resources/fonts/arcade.ttf", 72)


        mainmenu = self.renderfont(arcade_90, "Patrice Smash", True, (255, 255, 255))
        playText = self.renderfont(arcade_72, "Play", True, (255, 255, 255))
        optionsText = self.renderfont(arcade_72, "Options", True, (255, 255, 255))
        creditsText = self.renderfont(arcade_72, "Credits", True, (255, 255, 255))

        centerMainText = mainmenu.get_rect(center=((x/2), (y/4)))
        centerPlayText = playText.get_rect(center=((x/2), (y/2.5)))
        centerOptionsText = optionsText.get_rect(center=((x/2), (y/1.75)))
        centerCreditsText = creditsText.get_rect(center=((x/2), (y/1.35)))

        selectionOutline = centerPlayText.inflate(30,30)
        centerPlayText.inflate(30,30)
        centerOptionsText.inflate(30, 30)
        centerCreditsText.inflate(30, 30)
        selectionOutline.center = centerPlayText.center

        while self._running:
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self._status == "main":

                            self._playrunning = False
                            self._running = False
                    elif event.key == pg.K_DOWN:
                        if self._status == "main":
                            if self._selected == "play":
                                selectionOutline = centerOptionsText.inflate(30, 30)
                                self._selected = "options"
                            elif self._selected == "options":
                                selectionOutline = centerCreditsText.inflate(30, 30)
                                self._selected = "credits"
                            elif self._selected == "credits":
                                selectionOutline = centerPlayText.inflate(30, 30)
                                self._selected = "play"
                    elif event.key == pg.K_UP:
                        if self._status == "main":
                            if self._selected == "play":
                                selectionOutline = centerCreditsText.inflate(30, 30)
                                self._selected = "credits"
                            elif self._selected == "options":
                                selectionOutline = centerPlayText.inflate(30, 30)
                                self._selected = "play"
                            elif self._selected == "credits":
                                selectionOutline = centerOptionsText.inflate(30, 30)
                                self._selected = "options"
                    elif event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                        if self._status == "main":
                            if self._selected == "play":

                                self._status = "play"

                                self._playrunning = True
                                self._selectloop()

                                self._running = False
                            elif self._selected == "options":

                                self._status = "options"

                                self._optionsrunning = True
                                self._optionsloop()

                                self._running = False

                            elif self._selected == "credits":
                                
                                self._status = "credits"

                                self._creditsrunning = True
                                self._creditsloop()

                                self._running = False

            self._window.blit(self.BACKGROUND, (0,0))
            self.displaytext(mainmenu, centerMainText)
            self.displaytext(playText, centerPlayText)
            self.displaytext(optionsText, centerOptionsText)
            self.displaytext(creditsText, centerCreditsText)

            pg.draw.rect(self._window, (100, 100, 100), selectionOutline, 2, 10, 10, 10, 10)

            pg.display.update()

            self._clock.tick(self.framerate)

    def _selectloop(self):
        self._selected = "back"
        pg.mouse.set_visible(False)
        x, y = self.dimensions

        maps = self.loadcsv('../assets/resources/maps.csv')
        compiliedMaps = self.compileCSVList(maps)

        characters = self.loadcsv('../assets/resources/characters.csv')
        compiliedCharacters = self.compileCSVList(characters)

        for character in compiliedCharacters:
            print(character[0])

        arcade_72 = self.getfont("../assets/resources/fonts/arcade.ttf", 72)

        playPlaceholder = self.renderfont(arcade_72, "Insert info here", True, (255, 255, 255))
        backText = self.renderfont(arcade_72, "Back", True, (255, 255, 255))

        centerPlaceholder = playPlaceholder.get_rect(center=((x/2), (y/4)))
        centerBack = backText.get_rect(center=((x/2), (y/2.5)))

        selectionOutline = centerBack.inflate(30,30)

        centerPlaceholder.inflate(30,30)
        centerBack.inflate(30, 30)
        selectionOutline.center = centerBack.center

        while self._playrunning:
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self._status == "play":
                            self._status = "main"
                            
                            self._playrunning = False
                            self._mainloop()

                    if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                        if self._status == "play":
                            if self._selected == "back":
                                self._status = "main"
                            
                                self._playrunning = False
                                self._mainloop()



            self._window.blit(self.BACKGROUND, (0,0))
            self.displaytext(playPlaceholder, centerPlaceholder)
            self.displaytext(backText, centerBack)

            pg.draw.rect(self._window, (100, 100, 100), selectionOutline, 2, 10, 10, 10, 10)

            pg.display.update()

            self._clock.tick(self.framerate)
    
    def _optionsloop(self):
        self._selected = "back"
        pg.mouse.set_visible(False)
        x, y = self.dimensions

        arcade_72 = self.getfont("../assets/resources/fonts/arcade.ttf", 72)

        playPlaceholder = self.renderfont(arcade_72, "Insert info here", True, (255, 255, 255))
        backText = self.renderfont(arcade_72, "Back", True, (255, 255, 255))

        centerPlaceholder = playPlaceholder.get_rect(center=((x/2), (y/4)))
        centerBack = backText.get_rect(center=((x/2), (y/2.5)))

        selectionOutline = centerBack.inflate(30,30)

        centerPlaceholder.inflate(30,30)
        centerBack.inflate(30, 30)
        selectionOutline.center = centerBack.center

        while self._optionsrunning:
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self._status == "options":
                            self._status = "main"
                            
                            self._optionsrunning = False
                            self._mainloop()

                    if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                        if self._status == "options":
                            if self._selected == "back":
                                self._status = "main"
                            
                                self._optionsrunning = False
                                self._mainloop()


            self._window.blit(self.BACKGROUND, (0,0))
            self.displaytext(playPlaceholder, centerPlaceholder)
            self.displaytext(backText, centerBack)

            pg.draw.rect(self._window, (100, 100, 100), selectionOutline, 2, 10, 10, 10, 10)

            pg.display.update()

            self._clock.tick(self.framerate)

    def _creditsloop(self):
        self._selected = "back"
        pg.mouse.set_visible(False)
        x, y = self.dimensions

        arcade_72 = self.getfont("../assets/resources/fonts/arcade.ttf", 72)

        playPlaceholder = self.renderfont(arcade_72, "Insert info here", True, (255, 255, 255))
        backText = self.renderfont(arcade_72, "Back", True, (255, 255, 255))

        centerPlaceholder = playPlaceholder.get_rect(center=((x/2), (y/4)))
        centerBack = backText.get_rect(center=((x/2), (y/2.5)))

        selectionOutline = centerBack.inflate(30,30)

        centerPlaceholder.inflate(30,30)
        centerBack.inflate(30, 30)
        selectionOutline.center = centerBack.center

        while self._creditsrunning:
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self._status == "credits":
                            self._status = "main"
                            
                            self._creditsrunning = False
                            self._mainloop()

                    if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                        if self._status == "credits":
                            if self._selected == "back":
                                self._status = "main"
                            
                                self._creditsrunning = False
                                self._mainloop()


            self._window.blit(self.BACKGROUND, (0,0))
            self.displaytext(playPlaceholder, centerPlaceholder)
            self.displaytext(backText, centerBack)

            pg.draw.rect(self._window, (100, 100, 100), selectionOutline, 2, 10, 10, 10, 10)

            pg.display.update()

            self._clock.tick(self.framerate)

game = Game()
game.dimensions = (1920,1080)
game.name = "PatriceSmash"
game.framerate = 60

class Character(pg.sprite.Sprite):
    """
    Represents a character builder
    """
    def __init__(self, name, health, lives):
        self.idle: pg.Surface = None
        self.running: pg.Surface = None
        self.attack: pg.Surface = None 

        self.game = game
        self.health: float = None
        self.name: str = None
        self.alive: bool = True
        self.lives: int = None

    def printgame(self):
        print(self.game.dimensions)


        

def get_game():
    """
    Returns control loop game object
    """
    return game

#img = game.loadimage("./assets/art/icon.jpg")
#game.icon = img

def main():
    game.run()

if __name__=="__main__":
    main()