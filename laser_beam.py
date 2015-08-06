import math
import pygame as pg
import prepare
import angles


class LaserBeam(pg.sprite.DirtySprite):
    def __init__(self, center_pos, angle, speed, image, duration, damage, *groups):
        super(LaserBeam, self).__init__(*groups)
        self.pos = center_pos
        self.angle = angle
        self.speed = speed / 1000.
        self.duration = duration
        self.base_image = pg.transform.rotozoom(prepare.GFX[image], math.degrees(self.angle), prepare.SCALE_FACTOR).convert_alpha()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.intensity = 1
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer > self.duration:
            self.kill()
        self.intensity = 1 - (self.timer / float(self.duration))
        alpha = max(0, min(255, 255 * self.intensity))
        self.image = self.base_image.copy()
        self.image.fill((0, 0, 0, 255 - alpha), None, pg.BLEND_RGBA_SUB)
        self.pos = angles.project(self.pos, self.angle, self.speed * dt)
        self.rect.center = self.pos

