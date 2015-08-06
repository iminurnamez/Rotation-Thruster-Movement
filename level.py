"""
This module contains the Level class.
Drawing and updating of actors should occur here.
"""
import math
import random
import pygame as pg

import prepare
import tools
import planet
import ship_ui
import asteroid
import products
import ai_ship


class Level(object):
    """
    This class represents the whole starscape.  The starscape consists of
    three star layers.  The player is drawn and updated by this class.
    The player is contained in a pg.sprite.GroupSingle group.
    """
    def __init__(self, viewport, player):
        self.image = prepare.GFX["big stars"].copy()
        self.rect = self.image.get_rect()
        player.rect.midbottom = self.rect.centerx, self.rect.bottom-50
        self.player_singleton = pg.sprite.GroupSingle(player)
        self.player = player
        self.make_layers()
        self.viewport = viewport
        self.update_viewport(True)
        self.mid_viewport = self.viewport.copy()
        
        self.planets = pg.sprite.Group()
        self.make_planets()
        self.blitters = pg.sprite.OrderedUpdates()
        self.ship_ui = ship_ui.ShipUI(self)

        self.asteroids = pg.sprite.Group()
        for _ in range(10):
            self.add_asteroid()
        self.ai_ships = pg.sprite.Group()
        self.ai_ship_choices = ["Imperial Shuttle"]
        for _ in range(prepare.NUM_ENEMIES):
            self.add_ship((400, 400))
        
    def add_asteroid(self, pos=None):
        if pos:
            pos = pos
        else:
            pos =random.randint(100, self.rect.w - 100), random.randint(100, self.rect.h - 100)
        asteroid.Asteroid((pos), self.asteroids)
        
    def add_ship(self, pos=None, cargo=None):
        if pos:
            pos = pos
        else:
            pos = (random.randint(100, self.rect.w - 100),
                      random.randint(100, self.rect.h - 100))
        start_angle = random.uniform(0, math.pi * 2)
        parts = random.choice(self.ai_ship_choices)
        ai_ship.AIShip(pos, start_angle, products.make_ship(parts), cargo, self.ai_ships)
        
        
        
    def divide_screen(self):
        w, h = self.rect.size
        return  {(x, y)
                    for x in range(500, w + 1, 1000)
                    for y in range(500, h + 1, 1000)}

    def make_planets(self, num_planets=9):
        img_names = ["planet{}".format(x) for x in range(1, 11)]
        images = [random.choice(img_names) for _ in range(num_planets)]
        colors = random.sample(planet.PLANET_COLORS, num_planets)
        spots = random.sample(self.divide_screen(), num_planets)
        for image, color, spot in zip(images, colors, spots):
            x, y = (coord + random.randint(-200, 200) for coord in spot)
            radius = random.randint(60, 200)
            spin = random.uniform(.5, 2.0)
            planet.Planet((x, y), prepare.GFX[image], radius, spin, color, self.planets)
        for p in self.planets:
            p.spaceport.update_prices(self.planets)
        with open("planet_info.txt", "w") as f:
            for p in self.planets:
                f.write("POS: {}".format(p.pos))
                for item, price in p.spaceport.prices.items():
                    f.write("{}: {:.2f}".format(item, price))
                f.write("\n")
                
    def make_layers(self):
        """
        Create the middle and base image of the stars.
        self.image scrolls with the player, self.mid_image scrolls at
        half the speed, and self.base always stays fixed.
        """
        w, h = self.image.get_size()
        shrink = pg.transform.smoothscale(self.image, (w//2, h//2))
        self.mid_image = tools.tile_surface((w,h), shrink, True)
        shrink = pg.transform.smoothscale(self.image, (w//4, h//4))
        self.base = tools.tile_surface(prepare.SCREEN_SIZE, shrink, True)

    def update(self, keys, dt):
        """
        Updates the player and then adjusts the viewport with respect to the
        player's new position.
        """
        if not self.player.docked:
            self.player_singleton.update(keys, dt, self.rect, self.planets)
            self.ai_ships.update(dt, self.rect, self.planets, self.player)
            self.planets.update(dt, self.viewport, self.planets)
            self.asteroids.update(dt)
            self.update_viewport(dt)
            self.ship_ui.update(dt, self)
        else:
            self.player.spaceport.ui.update(dt, self.player)

    def update_viewport(self, start=False):
        """
        The viewport will stay centered on the player unless the player
        approaches the edge of the map.
        """
        old_center = self.viewport.center
        self.viewport.center = self.player_singleton.sprite.rect.center
        self.viewport.clamp_ip(self.rect)
        change = (self.viewport.centerx-old_center[0],
                  self.viewport.centery-old_center[1])
        if not start:
            self.mid_viewport.move_ip(change[0]*0.5, change[1]*0.5)

    def draw(self, surface):
        """
        Blit and clear actors on the self.image layer.
        Then blit appropriate viewports of all layers.
        """
        if not self.player.docked:
            self.blitters.clear(self.image, clear_callback)
            self.blitters.empty()
            self.blitters = pg.sprite.OrderedUpdates(*(x for x in self.planets if x.rect.colliderect(self.viewport)))
            onscreen_ships = [ai for ai in self.ai_ships if ai.rect.colliderect(self.viewport)]
            for ship in onscreen_ships:
                self.blitters.add(*(proj for proj in ship.projectiles if proj.rect.colliderect(self.viewport)))
            self.blitters.add(*onscreen_ships)
            self.blitters.add(*(p for p in self.player.projectiles if p.rect.colliderect(self.viewport)))
            self.blitters.add(self.player)
            self.blitters.add(*(a for a in self.asteroids if a.rect.colliderect(self.viewport)))
            self.blitters.draw(self.image)
            surface.blit(self.base, (0,0))
            surface.blit(self.mid_image, (0,0), self.mid_viewport)
            surface.blit(self.image, (0,0), self.viewport)
            self.ship_ui.draw(surface)
        else:
            surface.blit(self.base, (0,0))
            surface.blit(self.mid_image, (0,0), self.mid_viewport)
            self.player.spaceport.ui.draw(surface)
            
def clear_callback(surface, rect):
    """
    We need this callback because the clearing background contains
    transparency.  We need to fill the rect with transparency first.
    """
    surface.fill((0,0,0,0), rect)
    surface.blit(prepare.GFX["big stars"], rect, rect)
