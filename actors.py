"""
This module contains the Player class for the user controlled character.
"""

import math
import pygame as pg
import prepare
import angles
import cargo_prices
TWOPI = 2 * math.pi


class Ship(pg.sprite.DirtySprite):
    def __init__(self, pos, start_angle, ship_parts, cargo, *groups):
        super(Ship, self).__init__(*groups)
        self.pos = pos
        self.angle = start_angle
        hull, thruster, retro_thruster, steering, generator, battery_array, fuel_tank, laser, shield = ship_parts
        partnames = ("hull", "thruster", "retro_thruster", "steering",
                            "generator", "battery", "fuel_tank", "laser", "shield")
        self.parts = {k: v for k,v in zip(partnames, ship_parts)}        
        self.cargo = {k: 0 for k in cargo_prices.BASE_PRICES}
        if cargo:
            for item in cargo:
                self.cargo[item[0]] += item[1]
        self.base_image = pg.transform.rotozoom(prepare.GFX["ships"][hull.image], 0, prepare.SCALE_FACTOR)
        self.image = pg.transform.rotate(self.base_image, start_angle)
        self.rect = self.image.get_rect(center=pos)
        w, h = self.rect.size
        self.body_rect = self.rect.inflate(int(-w * .1), int(-h * .1))
        self.speed = 0
        self.redraw = True
        self.docked = False
        self.dockable = None
        self.projectiles = pg.sprite.Group()
        
    @property
    def hull(self):
        return self.parts["hull"]
        
    @property
    def thruster(self):
        return self.parts["thruster"]
        
    @property
    def retro_thruster(self):
        return self.parts["retro_thruster"]
        
    @property
    def steering(self):
        return self.parts["steering"]
        
    @property
    def generator(self):
        return self.parts["generator"]
        
    @property
    def battery(self):
        return self.parts["battery"]
        
    @property
    def fuel_tank(self):
        return self.parts["fuel_tank"]
        
    @property
    def laser(self):
        return self.parts["laser"]
        
    @property
    def shield(self):
        return self.parts["shield"]
        
    def add_part(self, part_type, part):
        self.parts[part_type] = part
        if part_type == "hull":
            self.base_image = pg.transform.rotozoom(prepare.GFX["ships"][part.image],
                                                                          0, prepare.SCALE_FACTOR)
                
    def get_cargo_weight(self):
        weight = 0
        for item in self.cargo:
            weight += self.cargo[item]
        return weight

    def get_weight(self):
        return sum((x.weight for x in self.parts.values())) + self.get_cargo_weight()

    def update_ship(self, dt):
        self.hull.update(dt, self)
        self.generator.update(dt, self)
        self.steering.update(dt, self)
        self.retro_thruster.update(dt, self)
        self.thruster.update(dt, self)
        self.laser.update(dt, self)
        self.shield.update(dt, self)
        self.battery.update(dt, self)

    def update(self, dt):
        self.update_ship(dt)

    def move(self, dt):
        self.pos = angles.project(self.pos, self.angle, self.speed * dt)
        self.rect.center = self.pos



class Player(Ship):
    """
    This class represents our user controlled character.
    """
    def __init__(self, pos, start_angle, ship_parts, cargo, *groups):
        super(Player, self).__init__(pos, start_angle, ship_parts, cargo, *groups)
        self.projectiles = pg.sprite.Group()
        self.cash = 10000

    def dock(self, spaceport):
        self.spaceport = spaceport
        self.docked = True
        
    def update(self, keys, dt, bounding, planets):
        """
        Updates the players position based on currently held keys.
        """
        self.controls = {
                    pg.K_LEFT: (self.steering.rotate, [1]),
                    pg.K_RIGHT: (self.steering.rotate, [-1]),
                    pg.K_UP: (self.thruster.accelerate, []),
                    pg.K_DOWN: (self.retro_thruster.decelerate, []),
                    pg.K_SPACE: (self.laser.fire, [])
                    }
        
        if not self.docked:
            self.update_ship(dt)
            self.check_keys(keys, dt)

            self.move(dt)
            clamped = self.rect.clamp(bounding)
            if clamped != self.rect:
                self.rect.clamp_ip(bounding)
                self.pos = self.rect.center
            self.projectiles.update(dt)
            planet = pg.sprite.spritecollideany(self, planets)
            if planet is not None:
                if planet.rect.collidepoint(self.rect.center) and self.speed < .01:
                    self.dockable = planet
                else:
                    self.dockable = None

    def get_event(self, event):
        if self.docked:
            self.spaceport.ui.get_event(event, self)
        else:    
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.thruster.thrust_sound.stop()
                    self.thruster.running = False
                if event.key == pg.K_d:
                    if self.dockable and not self.docked:
                        self.docked = True
                        self.spaceport = self.dockable.spaceport

    def check_keys(self, keys, dt):
        """
        Find the players movement vector from key presses.
        """
        #move = [0, 0]
        #for key in prepare.DIRECT_DICT:
        #    if keys[key]:
        #        for i in (0, 1):
        #            move[i] += prepare.DIRECT_DICT[key][i]*self.speed
        #return move
        for key in self.controls:
            if keys[key]:
                self.controls[key][0](dt, self, *self.controls[key][1])

    def draw(self, surface):
        """
        Basic draw function. (not  used if drawing via groups)
        """
        surface.blit(self.image, self.rect)
