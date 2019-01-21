import os
import sys
import pygame as pg
from pyle.settings import TITLE, WIDTH, HEIGHT, FPS
from pyle.settings import TILESIZE
from pyle.settings import BGCOLOR, LIGHTGREY
from pyle.sprites import Player, Wall, Spritesheet
from pyle.tilemap import Map, Camera


# Support running from single .exe (via PyInstaller)
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

RESOURCE_DIR = os.path.join(os.getcwd(), 'resources')
IMG_DIR = os.path.join(RESOURCE_DIR, 'img')
SND_DIR = os.path.join(RESOURCE_DIR, 'snd')


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        pg.display.set_caption(TITLE)
        pg.key.set_repeat(500, 100)
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.dt = None
        self.playing = False

        # Game variables; see #new()
        self.all_sprites = None
        self.player = None
        self.walls = None
        self.camera = None

        # Resources from disk
        self.spritesheet_characters = None
        self.spritesheet_tiles = None
        self.map = None
        self.load_data()

    def load_data(self):
        self.spritesheet_characters = Spritesheet(
            os.path.join(IMG_DIR, 'spritesheet_characters.png'))
        self.spritesheet_tiles = Spritesheet(
            os.path.join(IMG_DIR, 'spritesheet_tiles.png'))
        self.map = Map(os.path.join(RESOURCE_DIR, 'map2.txt'))

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)
        self.camera = Camera(self.map.width, self.map.height)

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        pg.display.flip()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def show_start_screen(self):
        pass

    def show_gameover_screen(self):
        pass


g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_gameover_screen()
