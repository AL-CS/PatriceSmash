from concurrent.futures import thread
import csv
from re import I
import threading
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
    _characterselectlooprunning = False
    _mapselectlooprunning = False

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

    _selectedChars = {
        "p1": None,
        "p2": None
    }

    _selectedMap = None

    def __init__(self) -> None:
        self.dimensions: tuple = (1920,1080)
        self._window = pg.display.set_mode(self.dimensions, pg.RESIZABLE)

        pg.mixer.init()  
        with open('../assets/resources/json/userSettings.json', 'r') as f:
            self.dictData = json.loads(f.read())
            f.close()

        self.mainMenuSong = pg.mixer.Sound("../assets/sounds/songs/menu.wav")
        self.channel = pg.mixer.Channel(0)


        self._clickSoundEffect = pg.mixer.Sound("../assets/sounds/mainmenu/select.wav")
        self.swishSoundEffect = pg.mixer.Sound("../assets/sounds/mainmenu/swish.wav")
        self._punchSoundEffect = pg.mixer.Sound("../assets/sounds/punch.wav")
        self._gameOverSoundEffect = pg.mixer.Sound("../assets/sounds/gameover.wav")
        self._deathSoundEffect = pg.mixer.Sound("../assets/sounds/death.wav")
        self._quackSoundEffect = pg.mixer.Sound("../assets/sounds/quack.wav")
        self._squeakSoundEfect = pg.mixer.Sound("../assets/sounds/squeak.wav")
        self._kickSoundEffect = pg.mixer.Sound("../assets/sounds/kick.wav")
        self._SOUNDENABLED = self.dictData["audio"]
        self._VOLUME = self.dictData["volume"]

        self.SOUNDS = [self._clickSoundEffect, self.swishSoundEffect, self._punchSoundEffect, self._gameOverSoundEffect]

        self.BACKGROUND = self.loadimage("../assets/art/backgrounds/Background1.png")
        self.selectedmapimage = None

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

    def __initCollisionBoxes__(self) -> None:
        plat = cc.Platform(self._selectedMap)
        self.collisionBoxes.add(plat)
        self.all_sprites.add(plat)

    def __initChars__(self, p1dict, p2dict) -> None:
        char = cc.Character(p1dict["name"], p1dict["desc"], p1dict["imgpath"] + "/" + p1dict["filepathname"] + "_", "wasd")
        self._characterList["alive"].add(char)
        self.all_sprites.add(char)
        self._binding["wasd"] = char
        char.bind = "wasd"
        char.initChar() 

        char2 = cc.Character(p2dict["name"], p2dict["desc"], p2dict["imgpath"] + "/" + p2dict["filepathname"] + "_", "arrow")
        self._characterList["alive"].add(char2)
        self.all_sprites.add(char2)
        self._binding["arrow"] = char2
        char2.bind = "arrow"
        char2.initChar()

    def updateAudioListAndWriteToJSON(self, boolVal: bool) -> None:
        self._SOUNDENABLED = boolVal
        with open('../assets/resources/json/userSettings.json', "w") as f:
            compiled = json.dumps(self.dictData)
            f.write(compiled)
    
    def getMapsFromCSV(self):
        maps = self.loadcsv('../assets/resources/csv/maps.csv')
        compiliedMaps = self.compileCSVList(maps)
        return compiliedMaps

    def getCharactersFromCSV(self):
        characters = self.loadcsv('../assets/resources/csv/characters.csv')
        compiliedCharacters = self.compileCSVList(characters)
        return compiliedCharacters

    def playIfActive(self, sound: pg.mixer.Sound, loops: int = 0, channel: pg.mixer.Channel = None) -> None:
        if channel is None:
            if self._SOUNDENABLED is True: sound.play(loops=loops)
        else:
            channel.play(sound, loops)

    def changeVolume(self, volume: float) -> None:
        pg.mixer.music.set_volume(volume)
        for sound in self.SOUNDS:
            sound.set_volume(volume)
        
    def draw_rect_alpha(self, surface, color, rect) -> None:
        shape_surf = pg.Surface(pg.Rect(rect).size, pg.SRCALPHA)
        pg.draw.rect(shape_surf, color, shape_surf.get_rect())
        surface.blit(shape_surf, rect)

    def loadimage(self, image: str, size: tuple = None) -> pg.surface.Surface:
        """
        Function to return an image by filename passed a string in the pygame Surface format
        """
        img = pg.image.load(image).convert_alpha()

        if size is not None:
            img = pg.transform.scale(img, size)
            
        return img
    
    def loadcsv(self, location) -> list:
        """
        Loads CSV file as dictonary list from relative or absolute location
        """
        final = []
        with open(location, 'r') as data:
            for line in csv.DictReader(data):
                final.append(line)
        return final

    def compileCSVList(self, loadedcsv: list) -> list:
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
    
    def convertSeconds(self, seconds) -> str:
        min, sec = divmod(seconds, 60)
        hour, min = divmod(min, 60)
        return "%02d:%02d" % (min, sec)

    def run(self) -> None:
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

    def getfont(self, fontname: str, size: int) -> pg.font.Font:
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

        overlay = cc.GameOverOverlay()

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

        if self.channel.get_busy() is False:
            self.playIfActive(self.mainMenuSong, 999, self.channel)

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

                                self._status = "select"

                                self._characterselectlooprunning = True
                                self._characterAndMapSelectionLoop()

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


            self._window.blit(self.BACKGROUND, (175,0))

            overlay.draw()

            self.displaytext(mainmenu, centerMainText)
            self.displaytext(playText, centerPlayText)
            self.displaytext(optionsText, centerOptionsText)
            self.displaytext(creditsText, centerCreditsText)

            pg.draw.rect(self._window, (150, 150, 150), selectionOutline, 3, 10, 10, 10, 10)
            pg.display.update()

            self._clock.tick(self.framerate)

    def _mapSelectionLoop(self):

        self._selected = "submit"

        overlay = cc.GameOverOverlay()

        maps = self.getMapsFromCSV()
        mapsLayoutMap = []

        for map in maps:
            dicte = {"name": map[0], "character": map[1], "imgpath": map[2], "songpath": map[3]}
            mapsLayoutMap.append(dicte)

        index = 0

        pg.mouse.set_visible(False)
        x, y = self.dimensions

        funkmaster = self.getfont("../assets/resources/fonts/SFFunkMaster-Oblique.ttf", 90)
        arcade_32 = self.getfont("../assets/resources/fonts/arcade.ttf", 32)

        playPlaceholder = self.renderfont(funkmaster, "Select Map", True, (255, 255, 255))
        centerPlaceholder = playPlaceholder.get_rect(center=((x/2), (y/5)))

        submitButton = self.renderfont(arcade_32, "Continue", True, (255,255,255))
        centerSubmit = submitButton.get_rect(center=((x/2), (y/1.25)))

        selectionOutline = centerSubmit.inflate(30, 30)
        selectionOutline.center = centerSubmit.center

        horizontalRect = centerPlaceholder.inflate(1000, 10)

        centerPlaceholder.inflate(30,30)

        photo = self.loadimage(mapsLayoutMap[index]["imgpath"])
        photo = pg.transform.scale(photo, (350, 244)) 
        photoCenter = photo.get_rect(center=((x /2), (y-600))) 

        while self._mapselectlooprunning:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self._status == "select":
                            self._status = "main"
                            
                            self._mapselectlooprunning = False
                            self._mainloop()

                    if event.key == pg.K_RETURN:
                        if self._status == "select":
                            if self._selected == "submit":

                                self._selectedMap = mapsLayoutMap[index]

                                self._status = "play"

                                self._playrunning = True

                                self._mapselectlooprunning = False
                                self._selectloop()

                                #self._status = "selectm"

                                #self._mapselectlooprunning = True

                                #self._characterselectlooprunning = False
                                #self._characterAndMapSelectionLoop()

                    if event.key == pg.K_s:
                        if self._status == "select":
                            if index < len(mapsLayoutMap) - 1:
                                index += 1
                            elif index == len(mapsLayoutMap) - 1:
                                index = 0
                            photo = self.loadimage(mapsLayoutMap[index]["imgpath"])
                            photo = pg.transform.scale(photo, (350, 244)) 
                            photoCenter = photo.get_rect(center=((x /2), (y-600))) 

                    if event.key == pg.K_w:
                        if self._status == "select":
                            if index > 0:
                                index -= 1
                            elif index == 0:
                                index = len(mapsLayoutMap) - 1 
                            photo = self.loadimage(mapsLayoutMap[index]["imgpath"])
                            photo = pg.transform.scale(photo, (350, 244)) 
                            photoCenter = photo.get_rect(center=((x /2), (y-600))) 
    
                      
            selectedMap = self.renderfont(arcade_32, mapsLayoutMap[index]["name"], True, (255,255,255))

            centerSelection = selectedMap.get_rect(center=((x / 2), (y-400)))

            self._window.blit(self.BACKGROUND, (175,0))
            overlay.draw()
            self._window.blit(photo, photoCenter)

            self.displaytext(playPlaceholder, centerPlaceholder)
            self.displaytext(selectedMap, centerSelection)
            self.displaytext(submitButton, centerSubmit)


            pg.draw.rect(self._window, (150, 150, 150), selectionOutline, 3, 10, 10, 10, 10)
            self.draw_rect_alpha(self._window, (225, 225, 225, 50), horizontalRect)

            pg.display.update()

            self._clock.tick(self.framerate)

    def _characterAndMapSelectionLoop(self):

        self._selected = "submit"

        overlay = cc.GameOverOverlay()

        chars = self.getCharactersFromCSV()
        characterLayoutMap = []

        for char in chars:
            dicte = {"name": char[0], "desc": char[3], "imgpath": char[1], "filepathname": char[2]}

            characterLayoutMap.append(dicte)

        indexP1 = 0
        indexP2 = 0

        pg.mouse.set_visible(False)
        x, y = self.dimensions

        funkmaster = self.getfont("../assets/resources/fonts/SFFunkMaster-Oblique.ttf", 90)
        arcade_32 = self.getfont("../assets/resources/fonts/arcade.ttf", 32)

        playPlaceholder = self.renderfont(funkmaster, "Select Character", True, (255, 255, 255))
        centerPlaceholder = playPlaceholder.get_rect(center=((x/2), (y/5)))

        submitButton = self.renderfont(arcade_32, "Continue", True, (255,255,255))
        centerSubmit = submitButton.get_rect(center=((x/2), (y/1.25)))

        selectionOutline = centerSubmit.inflate(30, 30)
        selectionOutline.center = centerSubmit.center
 
        #beginSelectP1 = characterLayoutMap[indexP1]["name"]
        #beginSelectP2 = characterLayoutMap[indexP2]["name"]
        #P1SelectedChar = self.renderfont(arcade_32, f"{beginSelectP1}", True, (255,255,255))
        #P2SelectedChar = self.renderfont(arcade_32, f"{beginSelectP2}", True, (255,255,255))
        #centerP1Selection = P1SelectedChar.get_rect(center=((x / 2 - 350), (y-250)))
        #centerP2Selection = P2SelectedChar.get_rect(center=((x / 2 + 350), (y-250)))

        horizontalRect = centerPlaceholder.inflate(1000, 10)

        centerPlaceholder.inflate(30,30)

        while self._characterselectlooprunning:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        if self._status == "select":
                            self._status = "main"
                            
                            self._characterselectlooprunning = False
                            self._mainloop()

                    if event.key == pg.K_RETURN:
                        if self._status == "select":
                            if self._selected == "submit":

                                self._selectedChars["p1"] = characterLayoutMap[indexP1]
                                self._selectedChars["p2"] = characterLayoutMap[indexP2]

                                self._mapselectlooprunning = True

                                self._characterselectlooprunning = False
                                self._mapSelectionLoop()

                                #self._status = "selectm"

                                #self._mapselectlooprunning = True

                                #self._characterselectlooprunning = False
                                #self._characterAndMapSelectionLoop()

                    if event.key == pg.K_DOWN:
                        if self._status == "select":
                            if indexP2 < len(characterLayoutMap) - 1:
                                indexP2 += 1
                            elif indexP2 == len(characterLayoutMap) - 1:
                                indexP2 = 0

                    if event.key == pg.K_UP:
                        if self._status == "select":
                            if indexP2 > 0:
                                indexP2 -= 1
                            elif indexP2 == 0:
                                indexP2 = len(characterLayoutMap) - 1 

                    if event.key == pg.K_s:
                        if self._status == "select":
                            if indexP1 < len(characterLayoutMap) - 1:
                                indexP1 += 1
                            elif indexP1 == len(characterLayoutMap) - 1:
                                indexP1 = 0

                    if event.key == pg.K_w:
                        if self._status == "select":
                            if indexP1 > 0:
                                indexP1 -= 1
                            elif indexP1 == 0:
                                indexP1 = len(characterLayoutMap) - 1 

            photoP1EXT = characterLayoutMap[indexP1]["imgpath"] + "/" + characterLayoutMap[indexP1]["filepathname"] + "_left.png"
            photoP2EXT = characterLayoutMap[indexP2]["imgpath"] + "/" + characterLayoutMap[indexP2]["filepathname"] + "_left.png"
            photoP1 = self.loadimage(photoP1EXT)
            photoP2 = self.loadimage(photoP2EXT)

            P1SelectedChar = self.renderfont(arcade_32, characterLayoutMap[indexP1]["name"], True, (255,255,255))
            P2SelectedChar = self.renderfont(arcade_32, characterLayoutMap[indexP2]["name"], True, (255,255,255))

            centerP1Selection = P1SelectedChar.get_rect(center=((x / 2 - 350), (y-400)))
            centerP2Selection = P2SelectedChar.get_rect(center=((x / 2 + 350), (y-400)))

            self._window.blit(self.BACKGROUND, (175,0))
            overlay.draw()
            if characterLayoutMap[indexP1]["filepathname"] == "patrice":
                updatedsize = pg.transform.scale(photoP1, (165, 134))
                self._window.blit(updatedsize, ((x / 2 - 425), (y-600)))
            elif characterLayoutMap[indexP1]["filepathname"] == "chemistry":
                self._window.blit(photoP1, ((x / 2 - 425), (y-700)))
            else:
                self._window.blit(photoP1, ((x / 2 - 425), (y-650)))
            if characterLayoutMap[indexP2]["filepathname"] == "patrice":
                updatedsize = pg.transform.scale(photoP2, (165, 134))
                self._window.blit(updatedsize, ((x / 2 + 275), (y-600)))
            elif characterLayoutMap[indexP2]["filepathname"] == "chemistry":
                self._window.blit(photoP2, ((x / 2 + 275), (y-700)))
            else:
                self._window.blit(photoP2, ((x / 2 + 275), (y-650)))
            
            self.displaytext(playPlaceholder, centerPlaceholder)
            self.displaytext(P1SelectedChar, centerP1Selection)
            self.displaytext(P2SelectedChar, centerP2Selection)
            self.displaytext(submitButton, centerSubmit)


            pg.draw.rect(self._window, (150, 150, 150), selectionOutline, 3, 10, 10, 10, 10)
            self.draw_rect_alpha(self._window, (225, 225, 225, 50), horizontalRect)

            pg.display.update()

            self._clock.tick(self.framerate)

    def _selectloop(self):
        self.channel.fadeout(1)

        overlay = cc.GameOverOverlay()

        gameover = False
        playerWon = "NO ONE"
        counter = 300
        self.__initChars__(self._selectedChars["p1"], self._selectedChars["p2"])
        self.__initCollisionBoxes__()

        BASE = {"healthValues": {"P1": 250, "P2": 250}, "lives": {"P1": 3, "P2": 3}}
        with open("../assets/resources/json/gameValues.json", "w") as f:
            f.write(json.dumps(BASE))
            f.close()

        self._selected = "back"
        pg.mouse.set_visible(False)
        x, y = self.dimensions

        mapSong = pg.mixer.Sound(self._selectedMap["songpath"])

        arcade_72 = self.getfont("../assets/resources/fonts/arcade.ttf", 72)
        arcade_32 = self.getfont("../assets/resources/fonts/arcade.ttf", 32)
        
        #if self._selectedMap["name"].lower() != "classroom":
            #color = (255, 255, 255)
        #else:
            #color = (0, 0, 0)
        timerText = self.renderfont(arcade_32, f"Time Left: {self.convertSeconds(counter)}", True, (255, 255, 255))
        backText = self.renderfont(arcade_72, "Back", True, (255, 255, 255))

        centerBack = backText.get_rect(center=((x/2), (y/2.5)))

        selectionOutline = centerBack.inflate(30,30)

        centerBack.inflate(30, 30)
        selectionOutline.center = centerBack.center

        image = self.loadimage(self._selectedMap["imgpath"])

        self.playIfActive(mapSong, 999)

        startTicks = pg.time.get_ticks()

        timerEvent = pg.USEREVENT + 1 

        pg.time.set_timer(timerEvent, 1000)

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

                            mapSong.stop()
                            
                            self._playrunning = False
                            self._mainloop()

                    if event.key == pg.K_w:
                        if self._status == "play" and gameover is False:
                            char = self._binding["wasd"]
                            
                            char.jump()

                    if event.key == pg.K_UP:
                        if self._status == "play" and gameover is False:
                            char = self._binding["arrow"]

                            char.jump()

                    if event.key == pg.K_x:
                        if self._status == "play" and gameover is False:
                            char = self._binding["wasd"]
                            data = char.attk(self._binding)
                            if data is not None:
                                if data[0] is True:
                                    if char.name.lower() == "patrice":
                                        self.playIfActive(self._quackSoundEffect)
                                    elif char.name.lower() == "captain chemistry":
                                        self.playIfActive(self._punchSoundEffect)
                                    elif char.name.lower() == "roger the kangaroo":
                                        self.playIfActive(self._kickSoundEffect)
                                    elif char.name.lower() == "sir. lancelot":
                                        self.playIfActive(self._squeakSoundEfect)

                                if data[1] is True:
                                    gameover = True
                                    playerWon = "Player 1"

                    if event.key == pg.K_KP_PERIOD:
                        if self._status == "play" and gameover is False:
                            char = self._binding["arrow"]
                            data = char.attk(self._binding)
                            if data is not None:
                                if data[0] is True:
                                    if char.name.lower() == "patrice":
                                        self.playIfActive(self._quackSoundEffect)
                                    elif char.name.lower() == "captain chemistry":
                                        self.playIfActive(self._punchSoundEffect)
                                    elif char.name.lower() == "roger the kangaroo":
                                        self.playIfActive(self._kickSoundEffect)
                                    elif char.name.lower() == "sir. lancelot":
                                        self.playIfActive(self._squeakSoundEfect)

                                if data[1] is True:
                                    gameover = True
                                    playerWon = "Player 2"

                elif event.type == timerEvent:
                    counter -=1
                    timerText = self.renderfont(arcade_32, f"Time Left: {self.convertSeconds(counter)}", True, (255, 255, 255))
                    
                    if counter == 0:
                        pg.time.set_timer(timerEvent, 0)
                        mapSong.fadeout(1)
                        self._gameOverSoundEffect.play()    

                        gameover = True
                        playerWon = "NO ONE"

            with open("../assets/resources/json/gameValues.json", "r") as f:
                jsonValues = json.loads(f.read())
                f.close()

            P1_health = jsonValues["healthValues"]["P1"]
            P2_health = jsonValues["healthValues"]["P2"]
            P1_lives = jsonValues["lives"]["P1"]
            P2_lives = jsonValues["lives"]["P2"]

            playPlaceholder = self.renderfont(arcade_32, f"P2 ({P2_lives}): {round(P2_health)}%", True, (255, 255, 255))
            centerPlaceholder = playPlaceholder.get_rect(center=((1525), (y/5.25)))

            playPlaceholder2 = self.renderfont(arcade_32, f"P1 ({P1_lives}): {round(P1_health)}%", True, (255, 255, 255))
            centerPlaceHolder2 = playPlaceholder2.get_rect(center=((1525), (y/6.5)))

            self._window.blit(image, (190,0))

            for entity in self._characterList["alive"]:
                entity.move(gameover)
                entity.update(self.collisionBoxes, self._characterList)

            for entity in self.all_sprites:
                entity.draw()

            #for entity in self._characterList["alive"]:
                #entity.move(gameover)
               # entity.update(self.collisionBoxes, self._characterList)

            #for entity in self.all_sprites:
                #entity.draw()

            centerTimer = timerText.get_rect(center=((450), (y/6.5)))

            self.displaytext(playPlaceholder, centerPlaceholder)
            self.displaytext(playPlaceholder2, centerPlaceHolder2)
            self.displaytext(timerText, centerTimer)

            
            
            if gameover is True:
                mapSong.fadeout(1)
                pg.time.set_timer(timerEvent, 0)
                self._gameOverSoundEffect.play()

                gameOverText = self.renderfont(arcade_72, f"{playerWon} WINS", True, (255, 255, 255))
                centerGameOver = gameOverText.get_rect(center=((x/2), (y/2)))
                overlay.draw()
                self.displaytext(gameOverText, centerGameOver)

            pg.display.update()

            self._clock.tick(self.framerate)
    
    def _optionsloop(self):
        self._selected = "toggleAudio"
        pg.mouse.set_visible(False)
        x, y = self.dimensions

        overlay = cc.GameOverOverlay()

        arcade_60 = self.getfont("../assets/resources/fonts/arcade.ttf", 60)
        arcade_72 = self.getfont("../assets/resources/fonts/arcade.ttf", 72)
        funkmaster = self.getfont("../assets/resources/fonts/SFFunkMaster-Oblique.ttf", 90)

        playPlaceholder = self.renderfont(funkmaster, "Game Options", True, (255, 255, 255))
        soundToggle = self.renderfont(arcade_60, f"Audio Enabled:{self._SOUNDENABLED}", True, (255, 255, 255))
        volumeSelector = self.renderfont(arcade_60, f"Volume: {self._VOLUME}", True, (255, 255, 255))
        backText = self.renderfont(arcade_72, "Back", True, (255, 255, 255))

        centerPlaceholder = playPlaceholder.get_rect(center=((x/2), (y/5)))
        horizontalRect = centerPlaceholder.inflate(1000, 10)

        centerAudioToggle = soundToggle.get_rect(center=((x/2), (y/1.75)))
        centerVolumeSelector = volumeSelector.get_rect(center=((x/2), (y/3)))
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
                                    self.channel.fadeout(1)

                                elif CURRENT_TOGGLE_STATUS == False:
                                    self.updateAudioListAndWriteToJSON(True)
                                    soundToggle = self.renderfont(arcade_60, f"Audio Enabled:{self._SOUNDENABLED}", True, (255, 255, 255))
                                    centerAudioToggle = soundToggle.get_rect(center=((x/2), (y/1.75)))
                                    selectionOutline = centerAudioToggle.inflate(30,30)

                            if self._selected == "back":
                                self._status = "main"
                            
                                self._optionsrunning = False
                                self._mainloop()


            self._window.blit(self.BACKGROUND, (175,0))
            overlay.draw()
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

        overlay = cc.GameOverOverlay()

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
        music = self.renderfont(arcade_60, "Composer: Seth Wiley", True, (255,255,255))
        
        centerProjectManager = projectManager.get_rect(center=((x/2), (y-725)))
        centerBusinessAnalyst = businessAnalyst.get_rect(center=((x/2), (y-625)))
        centerGraphicalArtist = graphicalArtist.get_rect(center=((x/2), (y-525)))
        centerDeveloper = developer.get_rect(center=((x/2), (y-425)))
        centerMusic = music.get_rect(center=((x/2), (y-325)))

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


            self._window.blit(self.BACKGROUND, (175,0))
            overlay.draw()
            self.displaytext(backText, centerBack)
            self.displaytext(projectManager, centerProjectManager)
            self.displaytext(businessAnalyst, centerBusinessAnalyst)
            self.displaytext(graphicalArtist, centerGraphicalArtist)
            self.displaytext(developer, centerDeveloper)
            self.displaytext(music, centerMusic)

            pg.draw.rect(self._window, (150, 150, 150), selectionOutline, 3, 10, 10, 10, 10)
            self.draw_rect_alpha(self._window, (225, 225, 225, 50), horizontalRect)

            self.displaytext(playPlaceholder, centerPlaceholder)

            pg.display.update()

            self._clock.tick(self.framerate)

game = Game()
game.dimensions = (1920,1080)
game.name = "PatriceSmash"
game.framerate = 60

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