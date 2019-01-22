import pygame as pg
import pytmx
from pyle.settings import TILESIZE, WIDTH, HEIGHT


class TiledMap:
    def __init__(self, filename):
        self.tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = self.tm.width * self.tm.tilewidth
        self.height = self.tm.height * self.tm.tileheight

    def render(self, surface):
        for layer in self.tm.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tm.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(tile, (x * self.tm.tilewidth,
                                            y * self.tm.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'r') as file:
            for line in file:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        # limit scrolling to map size
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH), x)
        y = max(-(self.height - HEIGHT), y)
        self.camera = pg.Rect(x, y, self.width, self.height)
