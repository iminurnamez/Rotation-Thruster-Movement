"""
This module contains utilities that are often useful.
"""

import os
import pygame as pg


def load_all_gfx(directory, colorkey=None, accept=(".png",".jpg",".bmp")):
    """
    Load all graphics with extensions in the accept argument.  If alpha
    transparency is found in the image the image will be converted using
    convert_alpha().  If no alpha transparency is detected image will be
    converted using convert() and colorkey will be set to colorkey.
    """
    graphics = {}
    for pic in os.listdir(directory):
        name,ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                if colorkey:
                    img.set_colorkey(colorkey)
            graphics[name]=img
    return graphics

def load_all_sounds(directory, accept=(".ogg", ".wav", ".mp3")):
    """
    Load sounds as mixer.Sound objects.
    """
    sounds = {}
    for sound in os.listdir(directory):
        name,ext = os.path.splitext(sound)
        if ext.lower() in accept:
            sounds[name]=pg.mixer.Sound(os.path.join(directory, sound))
    return sounds

def split_sheet(sheet, size, columns, rows):
    """
    Divide a loaded sprite sheet into subsurfaces.

    The argument size is the width and height of each frame (w,h)
    columns and rows are the integer number of cells horizontally and
    vertically.
    """
    subsurfaces = []
    for y in range(rows):
        row = []
        for x in range(columns):
            rect = pg.Rect((x*size[0], y*size[1]), size)
            row.append(sheet.subsurface(rect))
        subsurfaces.append(row)
    return subsurfaces


def tile_surface(size, tile, transparent=False):
    """
    Fill a surface of the given size with a surface tile.
    """
    if transparent:
        surface = pg.Surface(size).convert_alpha()
        surface.fill((0,0,0,0))
    else:
        surface = pg.Surface(size).convert()
    tile_size = tile.get_size()
    for i in range(0, tile_size[0]+size[0], tile_size[0]):
        for j in range(0, tile_size[1]+size[1], tile_size[1]):
            surface.blit(tile, (i,j))
    return surface
