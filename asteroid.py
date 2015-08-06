import itertools as it
import math
import random

import pygame as pg
import prepare
import angles


LARGE = [
    (0, 0, 200, 165),
    (200, 0, 187, 183),
    (387, 0, 167, 200),
    (554, 0, 184, 189),
    (738, 0, 200, 165),
    (938, 0, 189, 184),
    (1127, 0, 165, 200),
    (1292, 0, 183, 187)]


MEDIUM = [
    (0, 200, 100, 83),
    (100, 200, 93, 92),
    (193, 200, 83, 101),
    (276, 200, 93, 95),
    (369, 200, 101, 83),
    (470, 200, 95, 92),
    (565, 200, 84, 101),
    (649, 200, 92, 95)]


SMALL = [
    (0, 301, 50, 41),
    (50, 301, 47, 46),
    (97, 301, 41, 51),
    (138, 301, 47, 47),
    (185, 301, 51, 41),
    (236, 301, 47, 46),
    (283, 301, 42, 51),
    (325, 301, 46, 47)]


class Asteroid(pg.sprite.Sprite):
    sheet = prepare.GFX["asteroid_sheet"]
    sizes = ["small", "medium", "large"]
    base_images = {
                "large": [sheet.subsurface(big) for big in LARGE],
                "medium": [sheet.subsurface(m) for m in MEDIUM],
                "small": [sheet.subsurface(s) for s in SMALL]}

    def __init__(self, pos, *groups):
        super(Asteroid, self).__init__(*groups)
        self.pos = pos
        self.size = random.choice(self.sizes)
        self.angle = random.uniform(0.0, 2 * math.pi)
        self.speed = random.uniform(.01, .1)
        self.images = it.cycle(self.base_images[self.size])
        self.base_image = next(self.images)
        self.rect = self.base_image.get_rect(center=self.pos)
        self.frame_time = random.randint(500, 700)
        self.frame_timer = 0
        self.rotation = 0
        self.rotation_speed = random.uniform(.0005, .002)

    def next_frame(self):
        self.image = next(self.images)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.rotation += self.rotation_speed * dt
        if self.rotation >= .25 * math.pi:
            self.base_image = next(self.images)
            self.rotation -= .25 * math.pi
        self.image = pg.transform.rotate(self.base_image, math.degrees(-self.rotation))
        self.rect = self.image.get_rect()
        self.pos = angles.project(self.pos, self.angle, self.speed * dt)
        self.rect.center = self.pos

