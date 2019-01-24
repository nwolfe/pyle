import pygame as pg

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# Game settings
TITLE = 'Pyle'
FPS = 60
WIDTH = 1024
HEIGHT = 768
TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE
BGCOLOR = BROWN
WALL_IMG = 'tileGreen_39.png'

# Player settings
PLAYER_HEALTH = 100
PLAYER_SPEED = 300
PLAYER_ROTATION_SPEED = 250
PLAYER_IMG = 'manBlue_gun.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = pg.Vector2(30, 10)

# Gun settings
BULLET_IMG = 'bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
BULLET_RATE = 150
KICKBACK = 200
GUN_SPREAD = 5
BULLET_DAMAGE = 10

# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [150, 175, 200]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400

# Effects
FLASH_DURATION = 50
SPLAT_IMG = 'splat_green.png'
MUZZLE_FLASHES = [
    'whitePuff15.png',
    'whitePuff16.png',
    'whitePuff17.png',
    'whitePuff18.png',
]

# Layers
LAYER_WALL = 1
LAYER_ITEMS = 1
LAYER_PLAYER = 2
LAYER_BULLET = 3
LAYER_MOB = 2
LAYER_EFFECTS = 4

# Items
ITEM_IMAGES = {
    'health': 'health_pack.png'
}
HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 15
BOB_SPEED = 0.4

# Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUND_CHANCE = 0.7
PLAYER_HIT_SOUNDS = [
    'pain/8.wav',
    'pain/9.wav',
    'pain/10.wav',
    'pain/11.wav'
]
ZOMBIE_MOAN_CHANCE = 0.005
ZOMBIE_MOAN_SOUNDS = [
    ['brains2.wav', 0.8],
    ['brains3.wav', 0.8],
    ['zombie-roar-1.wav', 0.2],
    ['zombie-roar-2.wav', 0.2],
    ['zombie-roar-3.wav', 0.2],
    ['zombie-roar-5.wav', 0.2],
    ['zombie-roar-6.wav', 0.2],
    ['zombie-roar-7.wav', 0.2]
]
ZOMBIE_DEATH_SOUNDS = [
    ['splat-15.wav', 0.3]
]
WEAPON_SOUNDS_GUN = [
    ['sfx_weapon_singleshot2.wav', 0.4]
]
EFFECTS_SOUNDS = {
    'level_start': ['level_start.wav', 0.15],
    'health_up': 'health_pack.wav'
}
