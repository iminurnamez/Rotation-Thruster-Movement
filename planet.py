import math
import pygame as pg
import spaceport

#images from http://wwwtyro.github.io/procedural.js/planet1/


PLANET_COLORS = [
            (12, 93, 47),# emeraldish green
            (113, 78, 24),# tannish
            (113, 78, 24),# lilacish
            (101, 31, 28),# red desert
            (136, 163, 24),# eerie light green
            (201, 74, 0),# orange
            (131, 191, 198),# pale milky blue
            (209, 174, 0),# yellow
            (0,206,168),# venus blue
            (145, 190, 198),# icy blue
            (128, 128, 128),# medium moon grey
            (255, 127, 182),# pink
            (0, 74, 127),# vivid blue
            (0, 12, 62),# dark blue
            (127, 255, 142),# moon chees green
            (112, 93, 0),# dark mustard
            (38, 127, 0),# lime green
            (255, 178, 127),# pale desert
            (127, 51, 0),# orangey brown
            (119, 28, 101),# bold lilac
            (119, 28, 51),# deep milky rose
            (139, 69, 19),# brown desert
            (0, 0, 128),# very vivid blue
            (110,139, 61)# pale olive
            ]

class Planet(pg.sprite.DirtySprite):
    def __init__(self, pos, image, radius, rotations_per_minute, color, *groups):
        super(Planet, self).__init__(*groups)
        self.redraw = False
        self.pos = pos
        self.radius = radius
        self.circum = int(2 * math.pi * self.radius)
        self.sheet = pg.transform.smoothscale(image, (self.circum, self.radius * 2))

        try:
            self.color = pg.Color(color)
        except ValueError:
            self.color = pg.Color(*color)
        self.sheet.fill(self.color, None, pg.BLEND_RGB_ADD)
        self.make_cover()
        self.rotation_speed = (rotations_per_minute / 60.) * self.circum / 1000.
        self.subsurf = pg.Surface((self.radius*2, self.radius*2))
        self.subsurf.set_colorkey(pg.Color("purple"))
        self.source_pos = (self.radius, self.radius)
        self.int_pos = (self.radius, self.radius)
        self.image = pg.Surface((radius * 2, radius * 2)).convert()
        self.image.set_colorkey(pg.Color("purple"))
        self.rect = self.image.get_rect(center=self.pos)
        self.spaceport = spaceport.Spaceport(self)

    def make_cover(self):
        """
        Create a surface with a transparent hole in the center.
        """
        r = self.radius
        self.cover = pg.Surface((r*2, r*2)).convert()
        self.cover.fill(pg.Color("purple"))
        self.cover.set_colorkey(pg.Color("black"))
        pg.draw.circle(self.cover, pg.Color("black"), (r, r), r)

    def update(self, dt, viewport, planets):
        redraw = False
        self.redraw = False
        self.source_pos = (self.source_pos[0] + self.rotation_speed * dt,
                                   self.source_pos[1])
        if int(self.source_pos[0]) - self.radius > self.circum:
            self.source_pos = self.source_pos[0] - self.circum, self.source_pos[1]
        if (int(self.source_pos[0]), self.source_pos[1]) != self.int_pos:
            self.int_pos = int(self.source_pos[0]), int(self.source_pos[1])
            redraw = True
        if redraw and self.rect.colliderect(viewport):
            self.make_image()
            
        self.spaceport.update(dt, planets)

    def make_image(self):
        rect = pg.Rect((0,0), (self.radius * 2, self.radius * 2))
        rect.center = self.int_pos
        if rect.right > self.circum:
            left = pg.Rect(rect.left, rect.top, self.circum - rect.left, self.radius * 2)
            right = pg.Rect(0, rect.top, rect.right - self.circum, self.radius * 2)
            self.subsurf.blit(self.sheet.subsurface(left), (0, 0))
            self.subsurf.blit(self.sheet.subsurface(right), (left.width, 0))
        else:
            self.subsurf.blit(self.sheet.subsurface(rect), (0, 0))
        self.subsurf.blit(self.cover, (0, 0))
        self.image.fill(pg.Color("purple"))
        self.image.blit(self.subsurf, (0, 0))
        self.redraw = True


