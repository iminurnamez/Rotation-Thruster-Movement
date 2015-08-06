"""
This module initializes useful constants, initializes the display,
and loads necessary resources.
"""

import os
import sys
import pygame as pg
import tools

launch_args = sys.argv
if "-ENEMIES" in launch_args:
    NUM_ENEMIES = 1
else:
    NUM_ENEMIES = 0
if "-PIMPMOBILE" in launch_args:
    PLAYER_DEFAULT = "Pimpmobile"
else:
    PLAYER_DEFAULT = "Player Default"

CAPTION = "Space"
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN_SIZE = (700, 525) #(960, 540)
BACKGROUND_COLOR = (5, 10, 15)
SCALE_FACTOR = 0.3 # For scaleing down ship images.


DIRECT_DICT = {pg.K_UP   : ( 0,-1),
               pg.K_DOWN : ( 0, 1),
               pg.K_RIGHT: ( 1, 0),
               pg.K_LEFT : (-1, 0)}


# Set up environment.
pg.mixer.pre_init(44100, -16, 8, 512)
os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
pg.display.set_caption(CAPTION)
SCREEN = pg.display.set_mode(SCREEN_SIZE)

pg.mixer.music.load(os.path.join("resources", "WeltHerrschererTheme1.ogg"))
pg.mixer.music.play(-1)

FONT = os.path.join("resources", "DOS.ttf")
# Display a message while prepare prepares
font = pg.font.Font(FONT, 64)
label = font.render("Generating Galaxy", True, pg.Color(0, 220, 220), BACKGROUND_COLOR)
label_rect = label.get_rect(center=SCREEN.get_rect().center)
label.set_alpha(200)
SCREEN.fill(BACKGROUND_COLOR)
SCREEN.blit(label, label_rect)
pg.display.update()

# Load sound effects.
SFX = tools.load_all_sounds(os.path.join("resources", "sounds"))

# Load all graphics.
GFX = {}
GFX = tools.load_all_gfx("resources")
GFX["ships"] = tools.load_all_gfx(os.path.join("resources", "ships"))
colors = ("blue",  "orange", "red", "green", "yellow", "purple")
imgs = tools.split_sheet(GFX["lasersheetsmall"], (48, 16), 6, 1)
imgs2 = tools.split_sheet(GFX["lasersheetfat"], (48, 16), 6, 1)
for color, img in zip(colors, *imgs):
    GFX["smallbeam{}".format(color)] = img
for color2, img2 in zip(colors, *imgs2):
    GFX["fatbeam{}".format(color2)] = img2
    
    
#bigger space image
stars = GFX["stars"]
w, h = stars.get_size()
big_stars = pg.Surface((w * 8, h * 8)).convert_alpha()
big_stars.fill((0, 0, 0, 0))
for x in range(0, w*8 + 1, w):
    for y in range(0, h*8 + 1, h):
        big_stars.blit(stars, (x, y))
GFX["big stars"] = big_stars
