import pygame as pg
import xml.etree.ElementTree as xml
from pyle.settings import PLAYER_SPEED, PLAYER_IMG, PLAYER_ROTATION_SPEED
from pyle.settings import TILESIZE, GREEN, BLACK, PLAYER_HIT_RECT


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
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = pg.Vector2(0, 0)
        self.pos = pg.Vector2(x, y) * TILESIZE
        self.rot = 0
        self.rot_speed = 0

    def update(self):
        self._handle_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.orig_image, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        self._collide_with_walls('x')
        self.hit_rect.centery = self.pos.y
        self._collide_with_walls('y')
        self.rect.center = self.hit_rect.center

    def _handle_keys(self):
        self.rot_speed = 0
        self.vel = pg.math.Vector2(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROTATION_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROTATION_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = pg.Vector2(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = pg.Vector2(-PLAYER_SPEED / 2, 0).rotate(-self.rot)

    def move(self, dx=0, dy=0):
        if not self._collide_with_walls(dx, dy):
            self.x += dx
            self.y += dy

    @staticmethod
    def _collide_hit_rect(a, b):
        return a.hit_rect.colliderect(b.rect)

    def _collide_with_walls(self, dir):
        if 'x' == dir:
            hits = pg.sprite.spritecollide(self, self.game.walls,
                                           False, Player._collide_hit_rect)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.hit_rect.width / 2
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right + self.hit_rect.width / 2
                self.vel.x = 0
                self.hit_rect.centerx = self.pos.x
        elif 'y' == dir:
            hits = pg.sprite.spritecollide(self, self.game.walls,
                                           False, Player._collide_hit_rect)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.hit_rect.height / 2
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom + self.hit_rect.height / 2
                self.vel.y = 0
                self.hit_rect.centery = self.pos.y


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
