import random
import pygame as pg
import pytweening as tween
import xml.etree.ElementTree as xml
from pyle.settings import PLAYER_SPEED, PLAYER_IMG, PLAYER_ROTATION_SPEED
from pyle.settings import TILESIZE, BLACK, PLAYER_HIT_RECT, KICKBACK
from pyle.settings import MOB_IMG, MOB_SPEEDS, MOB_HIT_RECT, BULLET_SPEED
from pyle.settings import BULLET_LIFETIME, BULLET_RATE, BARREL_OFFSET
from pyle.settings import GUN_SPREAD, MOB_HEALTH, GREEN, YELLOW, RED
from pyle.settings import PLAYER_HEALTH, AVOID_RADIUS, FLASH_DURATION
from pyle.settings import LAYER_WALL, LAYER_PLAYER, LAYER_BULLET, LAYER_MOB
from pyle.settings import LAYER_EFFECTS, LAYER_ITEMS, BOB_RANGE, BOB_SPEED


def collide_hit_rect(a, b):
    return a.hit_rect.colliderect(b.rect)


def collide_with_walls(sprite, group, dir):
    if 'x' == dir:
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    elif 'y' == dir:
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


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
        self._layer = LAYER_PLAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites)
        self.game = game
        self.image = self.game.spritesheet_characters.get_image(PLAYER_IMG)
        self.image_orig = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = pg.Vector2(0, 0)
        self.pos = pg.Vector2(x, y)
        self.rot = 0
        self.rot_speed = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH

    def update(self):
        self._handle_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.image_orig, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

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
        if keys[pg.K_SPACE]:
            self._shoot()

    def _shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > BULLET_RATE:
            self.last_shot = now
            pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
            dir = pg.Vector2(1, 0).rotate(-self.rot)
            Bullet(self.game, pos, dir)
            self.vel = pg.Vector2(-KICKBACK, 0).rotate(-self.rot)
            MuzzleFlash(self.game, pos)


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_WALL
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.walls)
        self.game = game
        self.image = self.game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        pg.sprite.Sprite.__init__(self, game.walls)
        self.game = game
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, width, height)
        self.rect.x = x
        self.rect.y = y


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_MOB
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.mobs)
        self.game = game
        self.image = self.game.spritesheet_characters.get_image(MOB_IMG)
        self.image_orig = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = pg.Vector2(x, y)
        self.vel = pg.Vector2(0, 0)
        self.acc = pg.Vector2(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.health_bar = None
        self.speed = random.choice(MOB_SPEEDS)

    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(pg.Vector2(1, 0))
        self.image = pg.transform.rotate(self.image_orig, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = pg.Vector2(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt \
            + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        if self.health <= 0:
            self.kill()

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def draw_health(self):
        if self.health >= MOB_HEALTH:
            return
        if self.health > 60:
            color = GREEN
        elif self.health > 30:
            color = YELLOW
        else:
            color = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        pg.draw.rect(self.image, color, self.health_bar)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self._layer = LAYER_BULLET
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.bullets)
        self.game = game
        self.image = self.game.bullet_img
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = pos
        self.rect.center = self.pos
        spread = random.uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = LAYER_EFFECTS
        pg.sprite.Sprite.__init__(self, game.all_sprites)
        self.game = game
        size = random.randint(20, 50)
        image = random.choice(self.game.gun_flashes)
        self.image = pg.transform.scale(image, (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = LAYER_ITEMS
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.items)
        self.game = game
        self.image = self.game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1
