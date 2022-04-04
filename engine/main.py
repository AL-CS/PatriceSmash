import csv
import time
from numpy import random
import pygame as pg
import json
from pygame.rect import *  
import characterController as cc

class Game():
    
    """
    Main game class holding major functions and variables
    """
    _running = False
    _playrunning = False
    _optionsrunning = False
    _creditsrunning = False

    ACC = 4
    FRIC = -0.2
    vec = pg.math.Vector2

    _characterList = {
        "alive": pg.sprite.Group(),
        "dead": pg.sprite.Group()
    }

    _binding = {
        "wasd": None,
        "arrow": None
    }

    def __init__(self):
        self.dimensions: tuple = (1920,1000)
        self._window = pg.display.set_mode(self.dimensions, pg.RESIZABLE)

        pg.mixer.init()  
        with open('../assets/resources/userSettings.json', 'r') as f:
            self.dictData = json.loads(f.read())
        
        self._clickSoundEffect = pg.mixer.Sound("../assets/sounds/mainmenu/select.wav")
        self.swishSoundEffect = pg.mixer.Sound("../assets/sounds/mainmenu/swish.wav")
        self._SOUNDENABLED = self.dictData["audio"]

        self.BACKGROUND = self.loadimage("../assets/art/backgrounds/background.png")
        self.PLAYSCREEN = self.loadimage("../assets/art/backgrounds/playscreen.png")
        self.framerate: int = None
        self.name: str = None
        self.icon: pg.Surface = None

        self.collisionBoxes = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()

        self._clock = pg.time.Clock()

        self._status = "main"
        self._selected = "play"
        self._previously_selected = "play"

    class Colors():
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        GREEN = (0, 225, 0)
        BLUE = (0, 0, 225)

    def __initCollisionBoxes__(self):
        plat = cc.Platform()
        self.collisionBoxes.add(plat)
        self.all_sprites.add(plat)

    def __initChars__(self):
        char = cc.Character("Test", "power", "desc", "cube.png")
        self._characterList["alive"].add(char)
        self.all_sprites.add(char)
        self._binding["wasd"] = char
        char.bind = "wasd"
        char.initChar()

        char2 = cc.Character("Test2", "", "", "cube.png")
        self._characterList["alive"].add(char2)
        self.all_sprites.add(char2)
        self._binding["arrow"] = char2
        char2.bind = "arrow"
        char2.initChar()

        #characters = self.loadcsv('../assets/resources/characters.csv')
        #compiliedCharacters = self.compileCSVList(characters)

        #for character in compiliedCharacters:
            #char = cc.Character(character[0], character[1], character[2])
            #self._characterList["alive"].add(char)
            #self.all_sprites.add(char)

        #for char in self._characterList["alive"].sprites():
           # print(char.name)

    def updateAudioListAndWriteToJSON(self, boolVal: bool):
        self._SOUNDENABLED = boolVal
        with open('../assets/resources/userSettings.json', "w") as f:
            compiled = json.dumps(self.dictData)
            f.write(compiled)

    def playIfActive(self, sound: pg.mixer.Sound):
        if self._SOUNDENABLED is True: sound.play()
        
    def draw_rect_alpha(self, surface, color, rect):
        shape_surf = pg.Surface(pg.Rect(rect).size, pg.SRCALPHA)
        pg.draw.rect(shape_surf, color, shape_surf.get_rect())
        surface.blit(shape_surf, rect)

    def loadimage(self, image: str):
        """
        Function to return an image by filename passed a string in the pygame Surface format
        """
        img = pg.image.load(image).convert()
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
            pg.display.set_caption(self.name)
            pg.display.set_icon(self.icon)
            self._running = True
            self._mainloop()
            print("Game loop started.")
        else:
            print("You have not initialized the game correctly, or the game is already running!")

    def get(self, var: str):
        """                                                                                                                m            
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

        funkmaster = self.getfont("../assets/resources/fonts/SFFunkMaster-Oblique.ttf", 120)
        arcade_90 = self.getfont("../assets/resources/fonts/arcade.ttf", 90)
        arcade_72 = self.getfont("../assets/resources/fonts/arcade.ttf", 72)


        mainmenu = self.renderfont(funkmaster, "Patrice Smash", True, (255, 255, 255))
        playText = self.renderfont(arcade_72, "Play", True, (255, 255, 255))
        optionsText = self.renderfont(arcade_72, "Options", True, (255, 255, 255))
        creditsText = self.renderfont(arcade_72, "Credits", True, (255, 255, 255))

        centerMainText = mainmenu.get_rect(center=((x/2), (y/4.25)))
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
                            exit()

                    elif event.key == pg.K_DOWN:
                        self.playIfActive(self.swishSoundEffect)
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
                        self.playIfActive(self.swishSoundEffect)
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
                        self.playIfActive(self._clickSoundEffect)
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

            pg.draw.rect(self._window, (150, 150, 150), selectionOutline, 3, 10, 10, 10, 10)

            pg.display.update()

            self._clock.tick(self.framerate)

    def _physicsEngineGameLoop(self):
        pg.mouse.set_visible(False)
        x, y = self.dimensions

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
        
        self._window.blit(self.Colors.BLACK, (0,0))
        pg.display.update()

        self._clock.tick(self.framerate)

    def _selectloop(self):
        self.__initChars__()
        self.__initCollisionBoxes__()
        self._selected = "back"
        pg.mouse.set_visible(False)
        x, y = self.dimensions

        maps = self.loadcsv('../assets/resources/maps.csv')
        compiliedMaps = self.compileCSVList(maps)

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

                            for char in self.all_sprites:
                                char.kill()
                            
                            self._playrunning = False
                            self._mainloop()

                    if event.key == pg.K_w:
                        if self._status == "play":
                            char = self._binding["wasd"]
                            char.jump()

                    if event.key == pg.K_UP:
                        if self._status == "play":
                            char = self._binding["arrow"]
                            char.jump()

                    if event.key == pg.K_x:
                        if self._status == "play":
                            char = self._binding["wasd"]
                            char.attk(self._binding)

                    if event.key == pg.K_KP_PERIOD:
                        if self._status == "play":
                            char = self._binding["arrow"]
                            char.attk(self._binding)

                    if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                        self.playIfActive(self._clickSoundEffect)
                        if self._status == "play":
                            if self._selected == "back":
                                self._status = "main"

                                for char in self.all_sprites:
                                    char.kill()
                            
                                self._playrunning = False
                                self._mainloop()

            self._window.blit(self.PLAYSCREEN, (190,0))
        

            for entity in self._characterList["alive"]:
                entity.move()
                entity.update(self.collisionBoxes, self._characterList)

            for entity in self.all_sprites:
                entity.draw()
            #self.displaytext(playPlaceholder, centerPlaceholder)
            #self.displaytext(backText, centerBack)

            #pg.draw.rect(self._window, (150, 150, 150), selectionOutline, 3, 10, 10, 10, 10)

            pg.display.update()

            self._clock.tick(self.framerate)
    
    def _optionsloop(self):
        self._selected = "toggleAudio"
        pg.mouse.set_visible(False)
        x, y = self.dimensions

        arcade_60 = self.getfont("../assets/resources/fonts/arcade.ttf", 60)
        arcade_72 = self.getfont("../assets/resources/fonts/arcade.ttf", 72)
        funkmaster = self.getfont("../assets/resources/fonts/SFFunkMaster-Oblique.ttf", 90)

        playPlaceholder = self.renderfont(funkmaster, "Game Options", True, (255, 255, 255))
        soundToggle = self.renderfont(arcade_60, f"Audio Enabled:{self._SOUNDENABLED}", True, (255, 255, 255))
        backText = self.renderfont(arcade_72, "Back", True, (255, 255, 255))

        centerPlaceholder = playPlaceholder.get_rect(center=((x/2), (y/5)))
        horizontalRect = centerPlaceholder.inflate(1000, 10)

        centerAudioToggle = soundToggle.get_rect(center=((x/2), (y/1.75)))
        centerBack = backText.get_rect(center=((x/2), (y/1.25)))

        selectionOutline = centerAudioToggle.inflate(30,30)

        centerAudioToggle.inflate(30, 30)
        centerPlaceholder.inflate(30,30)
        centerBack.inflate(30, 30)
        selectionOutline.center = centerAudioToggle.center

        while self._optionsrunning:
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.playIfActive(self._clickSoundEffect)
                        if self._status == "options":
                            self._status = "main"
                            
                            self._optionsrunning = False
                            self._mainloop()

                    if event.key == pg.K_UP:
                        self.playIfActive(self.swishSoundEffect)
                        if self._status == "options":
                            if self._selected == "back":
                                selectionOutline = centerAudioToggle.inflate(30, 30)
                                self._selected = "toggleAudio"

                            elif self._selected == "toggleAudio":
                                selectionOutline = centerBack.inflate(30, 30)
                                self._selected = "back"
                    
                    if event.key == pg.K_DOWN:
                        self.playIfActive(self.swishSoundEffect)
                        if self._status == "options":
                            if self._selected == "back":
                                selectionOutline = centerAudioToggle.inflate(30, 30)
                                self._selected = "toggleAudio"

                            elif self._selected == "toggleAudio":
                                selectionOutline = centerBack.inflate(30, 30)
                                self._selected = "back"

                    if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                        self.playIfActive(self._clickSoundEffect)
                        if self._status == "options":
                            if self._selected == "toggleAudio":
                                CURRENT_TOGGLE_STATUS = self._SOUNDENABLED
                                if CURRENT_TOGGLE_STATUS == True:
                                    self.updateAudioListAndWriteToJSON(False)
                                    soundToggle = self.renderfont(arcade_60, f"Audio Enabled:{self._SOUNDENABLED}", True, (255, 255, 255))
                                    centerAudioToggle = soundToggle.get_rect(center=((x/2), (y/1.75)))
                                    selectionOutline = centerAudioToggle.inflate(30,30)

                                elif CURRENT_TOGGLE_STATUS == False:
                                    self.updateAudioListAndWriteToJSON(True)
                                    soundToggle = self.renderfont(arcade_60, f"Audio Enabled:{self._SOUNDENABLED}", True, (255, 255, 255))
                                    centerAudioToggle = soundToggle.get_rect(center=((x/2), (y/1.75)))
                                    selectionOutline = centerAudioToggle.inflate(30,30)

                            if self._selected == "back":
                                self._status = "main"
                            
                                self._optionsrunning = False
                                self._mainloop()


            self._window.blit(self.BACKGROUND, (0,0))
            self.displaytext(playPlaceholder, centerPlaceholder)
            self.displaytext(soundToggle, centerAudioToggle)
            self.displaytext(backText, centerBack)

            pg.draw.rect(self._window, (150, 150, 150), selectionOutline, 3, 10, 10, 10, 10)
            self.draw_rect_alpha(self._window, (225, 225, 225, 50), horizontalRect)

            pg.display.update()

            self._clock.tick(self.framerate)

    def _creditsloop(self):
        self._selected = "back"
        pg.mouse.set_visible(False)
        x, y = self.dimensions

        arcade_90 = self.getfont("../assets/resources/fonts/arcade.ttf", 90)
        arcade_72 = self.getfont("../assets/resources/fonts/arcade.ttf", 72)
        arcade_60 = self.getfont("../assets/resources/fonts/arcade.ttf", 45)
        shocap = self.getfont("../assets/resources/fonts/Sho-CardCapsNF.ttf", 72)
        funkmaster = self.getfont("../assets/resources/fonts/SFFunkMaster-Oblique.ttf", 90)

        playPlaceholder = self.renderfont(funkmaster, "Game Credits", True, (255, 255, 255))
        backText = self.renderfont(arcade_72, "Back", True, (255, 255, 255))

        projectManager = self.renderfont(arcade_60, "Project Manager: Howie Turner", True, (255,255,255))
        businessAnalyst = self.renderfont(arcade_60, "Business Analyst: Sean Pettenger", True, (255,255,255))
        graphicalArtist = self.renderfont(arcade_60, "Graphical Artist: Joshua Walker", True, (255,255,255))
        developer = self.renderfont(arcade_60, "Developer: Aidan Lelliott", True, (255,255,255))
        
        centerProjectManager = projectManager.get_rect(center=((x/2), (y/2.75)))
        centerBusinessAnalyst = businessAnalyst.get_rect(center=((x/2), (y/2.15)))
        centerGraphicalArtist = graphicalArtist.get_rect(center=((x/2), (y/1.75)))
        centerDeveloper = developer.get_rect(center=((x/2), (y/1.5)))

        centerPlaceholder = playPlaceholder.get_rect(center=((x/2), (y/5)))
        horizontalRect = centerPlaceholder.inflate(1000, 10)

        centerBack = backText.get_rect(center=((x/2), (y/1.25)))

        selectionOutline = centerBack.inflate(30,30)

        centerPlaceholder.inflate(30,30)
        centerBack.inflate(30, 30)
        selectionOutline.center = centerBack.center

        while self._creditsrunning:
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                elif event.type == pg.KEYDOWN:
                    self.playIfActive(self._clickSoundEffect)
                    if event.key == pg.K_ESCAPE:
                        if self._status == "credits":
                            self._status = "main"
                            
                            self._creditsrunning = False
                            self._mainloop()

                    if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                        self.playIfActive(self._clickSoundEffect)
                        if self._status == "credits":
                            if self._selected == "back":
                                self._status = "main"
                            
                                self._creditsrunning = False
                                self._mainloop()


            self._window.blit(self.BACKGROUND, (0,0))
            self.displaytext(backText, centerBack)
            self.displaytext(projectManager, centerProjectManager)
            self.displaytext(businessAnalyst, centerBusinessAnalyst)
            self.displaytext(graphicalArtist, centerGraphicalArtist)
            self.displaytext(developer, centerDeveloper)

            pg.draw.rect(self._window, (150, 150, 150), selectionOutline, 3, 10, 10, 10, 10)
            self.draw_rect_alpha(self._window, (225, 225, 225, 50), horizontalRect)

            self.displaytext(playPlaceholder, centerPlaceholder)

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

def get_game():
    """
    Returns control loop game object
    """
    return game

img = game.loadimage("../assets/art/icon.png")
game.icon = img

def main():
    game.run()

if __name__=="__main__":
    main()