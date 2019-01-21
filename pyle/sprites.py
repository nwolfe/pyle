import pygame as pg
import xml.etree.ElementTree as xml
from pyle.settings import TILESIZE, PLAYER_SPEED, PLAYER_IMG
from pyle.settings import GREEN, BLACK


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()
        try:
            self.coords = xml.parse(filename.replace('png', 'xml')).getroot()
        except Exception:
            self.coords = None

    def get_image_at(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        # image = pg.transform.scale(image, (width // 2, height // 2))
        image.set_colorkey(BLACK)
        return image

    def get_image(self, name):
        props = self.coords.find(".//SubTexture[@name='%s']" % name).attrib
        x = int(props['x'])
        y = int(props['y'])
        width = int(props['width'])
        height = int(props['height'])
        return self.get_image_at(x, y, width, height)


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self, game.all_sprites)
        self.game = game
        self.image = self.game.spritesheet_characters.get_image(PLAYER_IMG)
        self.rect = self.image.get_rect()
        self.vel = pg.math.Vector2(0, 0)
        self.pos = pg.math.Vector2(x, y) * TILESIZE

    def update(self):
        self._handle_keys()
        self.pos += self.vel * self.game.dt
        self.rect.x = self.pos.x
        self._collide_with_walls('x')
        self.rect.y = self.pos.y
        self._collide_with_walls('y')

    def _handle_keys(self):
        self.vel = pg.math.Vector2(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def move(self, dx=0, dy=0):
        if not self._collide_with_walls(dx, dy):
            self.x += dx
            self.y += dy

    def _collide_with_walls(self, dir):
        if 'x' == dir:
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        elif 'y' == dir:
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.walls)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
