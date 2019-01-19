import os
import sys
import pygame as pg

# Support running from single .exe (via PyInstaller)
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
    RESOURCE_DIR = os.path.join(os.getcwd(), 'resources')
else:
    RESOURCE_DIR = os.path.join(os.getcwd(), '..', 'resources')

IMG_DIR = os.path.join(RESOURCE_DIR, 'img')
SND_DIR = os.path.join(RESOURCE_DIR, 'snd')
