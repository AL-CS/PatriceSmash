import pygame as pg

class Game():
    """
    Main game class holding major functions and variables
    """

    def __init__(self):
        self.framerate: int = None
        self.name: str = None
        self.dimensions: tuple = None
        # self.icon: pg.Surface = None
        self._running = False
        self._clock = pg.time.Clock()

        self._WHITE = (255, 255, 255)
        self._BLACK = (0, 0, 0)

    def loadimage(self, image: str):
        """
        Function to return an image by filename passed a string in the pygame Surface format
        """
        img = pg.image.load(image)
        return img

    def rungame(self):
        """
        Function to run game
        """
        if self._running is not True and self.framerate and self.name and self.dimensions:
            pg.init()
            self._window = pg.display.set_mode(self.dimensions, pg.FULLSCREEN)
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
        status = pg.font.get_init()

        if (status is False):
            pg.font.init()

        font = pg.font.SysFont(fontname, size)
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
        self._window.blit(text, position)

    def _mainloop(self):
        """
        Starts game main loop

        Inits display
        """
        verdana = self.getfont('Verdana.ttf', 72)
        text = self.renderfont(verdana, 'test', True, self._WHITE, self._BLACK)
        while self._running:
            
            self.displaytext(text, (0,0))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
            pg.display.update()
            self._drawwindow()

            self._clock.tick(self.framerate)

        self._clock.tick(self.framerate)
    def _drawwindow(self):
        self._window.fill(self._BLACK)
        pg.display.update()

game = Game()
game.dimensions = (1920,1080)
game.name = "PatriceSmash"
game.framerate = 60

#img = game.loadimage("./assets/art/icon.jpg")
#game.icon = img

def main():
    game.rungame()

if __name__=="__main__":
    main()