import math
import random
from collections import deque
import angles
from actors import Ship


TWOPI = math.pi * 2
ONEDEG = math.pi / 180.


class AIShip(Ship):
    def __init__(self, pos, start_angle, ship_parts, cargo, *groups):
        super(AIShip, self).__init__(pos, start_angle, ship_parts, cargo, *groups)
        self.destination = None
        self.sight_distance = 1000
        
    def new_destination(self, planets):
        if self.destination is None:
            p = random.choice(planets.sprites())
            self.destination = p.pos
            self.angle = angles.get_angle(self.pos, self.destination)
            
    def evade(self, dt, other):
        angle_diff = abs(self.angle - other.angle)
        if angle_diff < .5 * pi:
            if self.speed < self.thruster.max_speed:
                self.accelerate(dt)
    
    def get_rotation(self, angle):
        x = int(math.degrees(self.angle))
        y = int(math.degrees(angle))
        
        d = deque(range(360))
        d.rotate(-x)        
        ticks = 0
        while d[0] != y:
            d.rotate(-1)
            ticks += 1
        if ticks > 180:
            ticks = (360 - ticks) * -1    
        return math.radians(ticks)
        
    def attack(self, dt, other):
        dist = angles.get_distance(self.pos, other.pos)
        to_other = angles.get_angle(self.pos, other.pos)
        rot_diff = self.get_rotation(to_other)
        try:
            direction = rot_diff / abs(rot_diff)
        except ZeroDivisionError:
            direction = 0
        if abs(rot_diff) < ONEDEG * 1.5:
            self.laser.fire(dt, self)
        else:
            self.steering.rotate(dt, self, direction)
            if abs(rot_diff) < (.5 * math.pi):
                if self.speed < self.thruster.max_speed:    
                    self.thruster.accelerate(dt, self)
            else:
                if self.speed > 0:
                    self.retro_thruster.decelerate(dt, self)            
                
        
    def update(self, dt, bounding, planets, player):
        if not self.docked:
            self.update_ship(dt)
            if angles.get_distance(self.pos, player.pos) < self.sight_distance:
                self.attack(dt, player)
            elif self.destination is None:
                self.new_destination(planets)
            elif self.rect.collidepoint(self.destination):
                self.destination = None
            
            self.move(dt)
            clamped = self.rect.clamp(bounding)
            if clamped != self.rect:
                self.rect.clamp_ip(bounding)
                self.pos = self.rect.center
            self.projectiles.update(dt)