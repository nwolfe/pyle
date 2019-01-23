import os
import sys
import pygame as pg
from pyle.settings import TITLE, WIDTH, HEIGHT, FPS, GREEN, YELLOW, RED
from pyle.settings import TILESIZE, WALL_IMG, BULLET_IMG, MOB_KNOCKBACK
from pyle.settings import LIGHTGREY, BULLET_DAMAGE, MOB_DAMAGE, CYAN
from pyle.settings import WHITE, PLAYER_HEALTH, MUZZLE_FLASHES
from pyle.sprites import Player, Spritesheet, Mob, Obstacle, collide_hit_rect
from pyle.tilemap import TiledMap, Camera


# Support running from single .exe (via PyInstaller)
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

RESOURCE_DIR = os.path.join(os.getcwd(), 'resources')
IMG_DIR = os.path.join(RESOURCE_DIR, 'img')
SND_DIR = os.path.join(RESOURCE_DIR, 'snd')
MAP_DIR = os.path.join(RESOURCE_DIR, 'maps')


# HUD functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        color = GREEN
    elif pct > 0.3:
        color = YELLOW
    else:
        color = RED
    pg.draw.rect(surf, color, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


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
        self.mobs = None
        self.bullets = None
        self.camera = None
        self.draw_debug = None

        # Resources from disk
        self.spritesheet_characters = None
        self.spritesheet_tiles = None
        self.map = None
        self.map_img = None
        self.wall_img = None
        self.bullet_img = None
        self.gun_flashes = None
        self.load_data()

    def load_data(self):
        self.spritesheet_characters = Spritesheet(
            os.path.join(IMG_DIR, 'spritesheet_characters.png'))
        self.spritesheet_tiles = Spritesheet(
            os.path.join(IMG_DIR, 'spritesheet_tiles.png'))
        # self.map = Map(os.path.join(RESOURCE_DIR, 'map2.txt'))
        self.map = TiledMap(os.path.join(MAP_DIR, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.wall_img = pg.image.load(
            os.path.join(IMG_DIR, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.bullet_img = pg.image.load(
            os.path.join(IMG_DIR, BULLET_IMG)).convert_alpha()
        self.gun_flashes = []
        for file in MUZZLE_FLASHES:
            self.gun_flashes.append(
                pg.image.load(os.path.join(IMG_DIR, file)).convert_alpha())

    def new(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        # for row, tiles in enumerate(self.map.data):
        #     for col, tile in enumerate(tiles):
        #         if tile == '1':
        #             Wall(self, col, row)
        #         if tile == 'M':
        #             Mob(self, col, row)
        #         if tile == 'P':
        #             self.player = Player(self, col, row)
        for tile_object in self.map.tm.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x, tile_object.y)
            elif tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            elif tile_object.name == 'zombie':
                Mob(self, tile_object.x, tile_object.y)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False

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
        # mobs hit player
        hits = pg.sprite.spritecollide(
            self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            hit.vel = pg.Vector2(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            self.player.pos += pg.Vector2(
                MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.health -= BULLET_DAMAGE
            hit.vel = pg.Vector2(0, 0)

    def draw(self):
        pg.display.set_caption("FPS: {:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        # self.draw_grid()
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN,
                             self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN,
                             self.camera.apply_rect(wall.rect), 1)
        # HUD functions
        draw_player_health(self.screen, 10, 10,
                           self.player.health / PLAYER_HEALTH)
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
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug

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
