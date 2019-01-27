import os
import sys
import random
import pygame as pg
from pyle.settings import TITLE, WIDTH, HEIGHT, FPS, GREEN, YELLOW, RED
from pyle.settings import TILESIZE, WALL_IMG, BULLET_IMG, MOB_KNOCKBACK
from pyle.settings import LIGHTGREY, MOB_DAMAGE, CYAN, WEAPONS
from pyle.settings import WHITE, PLAYER_HEALTH, MUZZLE_FLASHES, ITEM_IMAGES
from pyle.settings import HEALTH_PACK_AMOUNT, MOB_IMG, PLAYER_IMG
from pyle.settings import BG_MUSIC, EFFECTS_SOUNDS, WEAPON_SOUNDS
from pyle.settings import ZOMBIE_MOAN_SOUNDS, ZOMBIE_DEATH_SOUNDS, SPLAT_IMG
from pyle.settings import PLAYER_HIT_SOUNDS, PLAYER_HIT_SOUND_CHANCE
from pyle.sprites import Player, Spritesheet, Mob, Obstacle, collide_hit_rect
from pyle.sprites import Item
from pyle.tilemap import TiledMap, Camera


# Support running from single .exe (via PyInstaller)
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

RESOURCE_DIR = os.path.join(os.getcwd(), 'resources')
IMG_DIR = os.path.join(RESOURCE_DIR, 'img')
SND_DIR = os.path.join(RESOURCE_DIR, 'snd')
MUSIC_DIR = os.path.join(RESOURCE_DIR, 'music')
MAP_DIR = os.path.join(RESOURCE_DIR, 'maps')


def load_image(file, scale=None):
    i = pg.image.load(os.path.join(IMG_DIR, file)).convert_alpha()
    if scale:
        return pg.transform.scale(i, scale)
    else:
        return i


def load_sound(file_and_volume):
    volume = 1.0
    if type(file_and_volume) is list:
        file, volume = file_and_volume
    else:
        file = file_and_volume

    # class DebugSound(pg.mixer.Sound):
    #     def __init__(self, name):
    #         pg.mixer.Sound.__init__(self, name)
    #         self.name = name

    #     def play(self):
    #         pg.mixer.Sound.play(self)
    #         print("%s [%s]" % (self.name, self.get_volume()))
    # sound = DebugSound(os.path.join(SND_DIR, file))

    sound = pg.mixer.Sound(os.path.join(SND_DIR, file))
    sound.set_volume(volume)
    return sound


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
        pg.mixer.pre_init(44100, -16, 1, 2048)
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
        self.items = None
        self.draw_debug = None
        self.paused = None

        # Resources from disk
        self.title_font = None
        self.dim_screen = None
        self.spritesheet_characters = None
        self.map = None
        self.map_img = None
        self.player_img = None
        self.mob_img = None
        self.wall_img = None
        self.bullet_images = None
        self.splat_img = None
        self.gun_flashes = None
        self.item_images = None
        self.effect_sounds = None
        self.weapon_sounds = None
        self.zombie_moan_sounds = None
        self.zombie_death_sounds = None
        self.player_hit_sounds = None
        self.load_data()

    def load_data(self):
        # Images and maps
        self.title_font = os.path.join(IMG_DIR, 'ZOMBIE.TTF')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        self.spritesheet_characters = Spritesheet(
            os.path.join(IMG_DIR, 'spritesheet_characters.png'))
        self.map = TiledMap(os.path.join(MAP_DIR, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.player_img = self.spritesheet_characters.get_image(PLAYER_IMG)
        self.mob_img = self.spritesheet_characters.get_image(MOB_IMG)
        self.wall_img = load_image(WALL_IMG, scale=(TILESIZE, TILESIZE))
        self.bullet_images = dict(
            large=load_image(BULLET_IMG),
            small=load_image(BULLET_IMG, scale=(10, 10))
        )
        self.splat_img = load_image(SPLAT_IMG, scale=(64, 64))
        self.gun_flashes = []
        for i in MUZZLE_FLASHES:
            self.gun_flashes.append(load_image(i))
        self.item_images = {}
        for i in ITEM_IMAGES:
            self.item_images[i] = load_image(ITEM_IMAGES[i])

        # Sounds and music
        pg.mixer_music.load(os.path.join(MUSIC_DIR, BG_MUSIC))
        self.effect_sounds = {}
        for s in EFFECTS_SOUNDS:
            self.effect_sounds[s] = load_sound(EFFECTS_SOUNDS[s])
        self.zombie_moan_sounds = []
        for s in ZOMBIE_MOAN_SOUNDS:
            self.zombie_moan_sounds.append(load_sound(s))
        self.zombie_death_sounds = []
        for s in ZOMBIE_DEATH_SOUNDS:
            self.zombie_death_sounds.append(load_sound(s))
        self.player_hit_sounds = []
        for s in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(load_sound(s))
        self.weapon_sounds = {}
        for w in WEAPON_SOUNDS:
            self.weapon_sounds[w] = []
            for s in WEAPON_SOUNDS[w]:
                self.weapon_sounds[w].append(load_sound(s))

    def new(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.items = pg.sprite.Group()
        # for row, tiles in enumerate(self.map.data):
        #     for col, tile in enumerate(tiles):
        #         if tile == '1':
        #             Wall(self, col, row)
        #         if tile == 'M':
        #             Mob(self, col, row)
        #         if tile == 'P':
        #             self.player = Player(self, col, row)
        for tile_object in self.map.tm.objects:
            obj_center = pg.Vector2(tile_object.x + tile_object.width / 2,
                                    tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            elif tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            elif tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            elif tile_object.name in ITEM_IMAGES.keys():
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.effect_sounds['level_start'].play()

    def run(self):
        self.playing = True
        pg.mixer_music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        # player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                self.effect_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
                hit.kill()

        # mobs hit player
        hits = pg.sprite.spritecollide(
            self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random.random() < PLAYER_HIT_SOUND_CHANCE:
                random.choice(self.player_hit_sounds).play()
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
            damage = WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            hit.health -= damage
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
                if hasattr(sprite, 'hit_rect'):
                    pg.draw.rect(self.screen, CYAN,
                                 self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN,
                             self.camera.apply_rect(wall.rect), 1)
        # HUD functions
        draw_player_health(self.screen, 10, 10,
                           self.player.health / PLAYER_HEALTH)
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self._draw_text("Paused", self.title_font, 105, RED,
                            WIDTH / 2, HEIGHT / 2, align="center")
        pg.display.flip()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def _draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused

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
