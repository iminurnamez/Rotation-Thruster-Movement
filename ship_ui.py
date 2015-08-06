import math
import random
import pygame as pg
import prepare
import angles


def render_font(font, text, color):
    return font.render(text, True, color)


class StatusBar(pg.sprite.Sprite):
    def __init__(self, topleft, size, ratio, *groups):
        super(StatusBar, self).__init__(*groups)
        self.rect = pg.Rect(topleft, size)
        self.image = pg.Surface(size).convert_alpha()
        self.image.fill(pg.Color(0, 220, 220, 20))
        bar_length = int(self.rect.w * ratio)
        w, h = self.image.get_size()
        pg.draw.rect(self.image, pg.Color(0, 220, 220, 150), (0, 0, bar_length, self.rect.h))
        pg.draw.rect(self.image, pg.Color(0, 220, 220, 190), (0, 0, w, h), 1)


class Blinker(pg.sprite.Sprite):
    def __init__(self, image, pos, frequency, *groups):
        super(Blinker, self).__init__(*groups)
        self.base_image = image
        self.rect = self.base_image.get_rect(center=pos)
        self.blank = pg.Surface(self.rect.size).convert_alpha()
        self.blank.fill((0,0,0,0))
        self.frequency = frequency
        self.timer = 0
        self.visible = True
        self.active = False

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.frequency:
            self.timer -= self.frequency
            self.visible = not self.visible
        if self.visible and self.active:
            self.image = self.base_image
        else:
            self.image = self.blank


class ShipUI(object):
    compass_ = ("E", "ENE", "NE", "NNE", "N", "NNW", "NW", "WNW",
                       "W", "WSW", "SW", "SSW", "S", "SSE", "SE", "ESE")
    points = (11.25 + (22.5 * x) for x in range(len(compass_)))
    compass_points = zip(points, compass_)

    def __init__(self, level):
        w, h = 200, 200
        self.map_rect = pg.Rect(level.viewport.w - w, 5, w, h)
        self.make_map(level)
        self.map_fill_color = pg.Color(0, 230, 230)
        self.map_bg = pg.Surface(self.map_rect.size).convert()
        self.map_bg.fill(self.map_fill_color)
        self.map_bg.set_alpha(50)
        self.font = pg.font.Font(prepare.FONT, 14)
        self.text_color = pg.Color(0, 200, 200)
        msg_font = pg.font.Font(prepare.FONT, 32)
        dock_msg = render_font(msg_font, "Press D to dock", self.text_color)
        center = prepare.SCREEN_SIZE[0] // 2, 100
        self.blinkers = pg.sprite.Group()
        Blinker(dock_msg, center, 600, self.blinkers)
        
    def get_heading(self, angle):
        if angle > (360 - 11.25):
            return "E"
        for point, heading in self.compass_points:
            if angle < point:
                return heading

    def make_labels_bars(self, level):
        p = level.player
        gen = p.generator
        weight = p.get_cargo_weight()
        laser_cooldown = min(1, p.laser.cooldown / float(p.laser.cooldown_duration))
        speed_ratio = p.speed  / p.thruster.max_speed 
        angle = math.degrees(p.angle)
        heading = self.get_heading(angle)
        pad1 = 16
        pad2 = 16
        info = [
                ("{} {:.2f} / {:.2f}".format("Speed", p.speed * 100, p.thruster.max_speed * 100), speed_ratio),
                ("{} {}".format("Fuel", p.fuel_tank.fuel), p.fuel_tank.fuel / float(p.fuel_tank.capacity)),
                ("{} {}".format("Power", p.battery.power), p.battery.power / float(p.battery.capacity)),
                ("{} {}".format("Cargo", weight), weight / float(p.hull.tonnage)),
                ("{} {}".format("Laser", p.laser.name), laser_cooldown)]
        info2 = [
                ("{:16}{:16}".format("Hull", p.hull.name), p.hull.hit_points / float(p.hull.max_hit_points)),
                ("{:16}{:16}".format("Thruster", p.thruster.name), None),
                ("{:16}{:16}".format("Retro Thruster", p.retro_thruster.name), None),
                ("{:16}{:16}".format("Steering", p.steering.name), None),
                ("{:16}{:16} {}MJ/s, {}% efficient".format("Generator", gen.name, gen.output * 1000,
                                                                                     gen.efficiency * 100), None),
                ("{:16}{:16}".format("Battery", p.battery.name), None),
                ("{:16}{:16}".format("Shield", p.shield.name), None)]
        labels_bars = pg.sprite.Group()
        top = 0
        for text, bar_ratio in info:
            sprite = pg.sprite.Sprite(labels_bars)
            sprite.image = self.font.render(text, True, self.text_color).convert_alpha()
            sprite.rect = sprite.image.get_rect(topleft=(0, top))
            sprite.image.fill((0,0,0,100), None, pg.BLEND_RGBA_SUB)
            if bar_ratio is not None:
                top += sprite.rect.h
                bar_sprite = StatusBar((0, top), (80, 14), bar_ratio, labels_bars)
            top += sprite.rect.h
        top2 = 400    
        for text2, bar_ratio2 in info2:
            sprite = pg.sprite.Sprite(labels_bars)
            sprite.image = self.font.render(text2, True, self.text_color).convert_alpha()
            sprite.image.fill((0,0,0,100), None, pg.BLEND_RGBA_SUB)
            sprite.rect = sprite.image.get_rect(topleft=(0, top2))
            if bar_ratio2 is not None:
                top2 += sprite.rect.h
                bar_sprite = StatusBar((0, top2), (80, 14), bar_ratio, labels_bars)
            top2 += sprite.rect.h            
        return labels_bars

    def make_map(self, level):
        mapw, maph = self.map_rect.size
        worldw, worldh = level.image.get_size()
        self.xscale, self.yscale = mapw / float(worldw), maph / float(worldh)
        self.map_surf = pg.Surface((mapw, maph)).convert()
        self.map_surf.set_colorkey((0,0,0))

    def update_map(self, level):
        player = level.player
        self.map_surf.fill((0,0,0))
        for planet in level.planets:
            mapx = int(planet.pos[0] * self.xscale)
            mapy = int(planet.pos[1] * self.yscale)
            pg.draw.circle(self.map_surf, planet.color,
                                (mapx, mapy), int(planet.radius * self.xscale))
        px, py = int(player.pos[0] * self.xscale), int(player.pos[1] * self.yscale)
        pg.draw.circle(self.map_surf, pg.Color(0, 220, 220), (px, py), 2)
        pg.draw.line(self.map_surf, pg.Color(0, 220, 220), (px, py), angles.project((px, py), player.angle, 4))

    def update(self, dt, level):
        self.update_map(level)
        self.labels_bars = self.make_labels_bars(level)
        self.blinkers.update(dt)
        for blinker in self.blinkers:
            blinker.active = level.player.dockable is not None
        
    def draw(self, surface):
        surface.blit(self.map_bg, self.map_rect)
        surface.blit(self.map_surf, self.map_rect)
        pg.draw.rect(surface, self.map_fill_color, self.map_rect, 2)
        self.labels_bars.draw(surface)
        self.blinkers.draw(surface)
        
