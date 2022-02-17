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

    def loadimage(self, image: str):
        img = pg.image.load(image)
        return img

    def rungame(self):
        """
        Function to run game
        """
        if self._running is not True and self.framerate and self.name and self.dimensions:
            pg.init()
            pg.display.set_mode(self.dimensions)
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

    def _mainloop(self):
        """
        Starts game main loop

        Inits display
        """
        while self._running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
            pg.display.update()
            self._clock.tick(self.framerate)

def main():
    game = Game()
    game.dimensions = (1200, 700)
    game.name = "PatriceSmash"
    game.framerate = 60

    #img = game.loadimage("./assets/art/icon.jpg")
    #game.icon = img

    game.rungame()

if __name__=="__main__":
    main()