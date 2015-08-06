import random
import math
import pygame as pg
import prepare
import laser_beam


TWOPI = 2 * math.pi


class ShipComponent(object):
    """Base class for all ship components."""
    def __init__(self, name, weight, reliability, lifespan, price, repair_time=5, age=0):
        self.name = name
        self.weight = weight
        self.reliability = reliability
        self.lifespan = lifespan * 60000 #lifespan in ms
        self.price = price
        self.repair_time = repair_time * 1000 #repair time in ms
        self.age = age
        self.repair_timer = 0
        self.broken_down = False


    def breakdown_check(self, dt):
        """Check component for breakdown based on reliability and age."""
        breakdown_chance = (self.age / float(self.lifespan)) * dt * (1 - self.reliability)
        if random.randint(0, 1000 * dt) < breakdown_chance:
            self.breakdown()

    def breakdown(self):
        self.broken_down = True
        self.repair_timer = 0


class Hull(ShipComponent):
    """The body of the ship."""
    def __init__(self, name, damage_resistance, hit_points, image, cargo_tonnage, weight, reliability, lifespan, price, age=0):
        super(Hull, self).__init__(name, weight, reliability, lifespan, price, age)
        self.damage_resistance = damage_resistance
        self.max_hit_points = hit_points
        self.hit_points = hit_points
        self.image = image
        self.tonnage = cargo_tonnage

    def update(self, dt, ship):
        self.age += dt
        if self.hit_points <= 0:
            ship.dead = True


class Thruster(ShipComponent):
    def __init__(self, name, acceleration, max_speed, power_usage, weight_rating, weight, reliability, lifespan, price, age=0):
        super(Thruster, self).__init__(name, weight, reliability, lifespan, price, age)
        self.acceleration = acceleration / 1000. #per ms @ 100 tons
        self.max_speed = max_speed / 1000. #per ms
        self.power_usage = power_usage / 1000. #per ms @ 100 tons
        self.weight_rating = weight_rating
        self.thrust_sound = prepare.SFX["engine_loop"]
        self.running = False

    def accelerate(self, dt, ship):
        if self.broken_down:
            return
        if ship.battery.power >= self.power_usage * dt:
            if not self.running and self.thrust_sound is not None:
                self.thrust_sound.play()
            weight = ship.get_weight()
            if weight > self.weight_rating:
                overload = weight / float(self.weight_rating)
                accel = (self.acceleration * dt) / overload
            else:
                accel = self.acceleration * dt
            ship.speed = min(self.max_speed, ship.speed + accel)
            ship.battery.power -= self.power_usage * dt
            self.running = True

    def update(self, dt, ship):
        self.age += dt
        self.repair_timer += dt
        if self.broken_down:
            if self.repair_timer >= self.repair_time:
                self.broken_down = False
        self.breakdown_check(dt)


class RetroThruster(ShipComponent):
    def __init__(self, name, deceleration, min_speed, power_usage, weight_rating, weight, reliability, lifespan, price, age=0):
        super(RetroThruster, self).__init__(name, weight, reliability, lifespan, price, age)
        self.deceleration = deceleration / 1000. #per ms @ 100 tons
        self.min_speed = min_speed / 1000. #per ms
        self.power_usage = power_usage / 1000. #per ms @ 100 tons
        self.weight_rating = weight_rating

    def decelerate(self, dt, ship):
        if ship.battery.power >= self.power_usage * dt:
            weight = ship.get_weight()
            if weight > self.weight_rating:
                over = weight - self.weight_rating
                overload = over / float(self.weight_rating)
                decel = (self.deceleration * dt) / overload
            else:
                decel = self.deceleration * dt
            ship.speed = max(self.min_speed, ship.speed - decel)
            ship.battery.power -= self.power_usage * dt

    def update(self, dt, ship):
        self.age += dt
        self.repair_timer += dt
        if self.broken_down:
            if self.repair_timer >= self.repair_time:
                self.broken_down = False
        self.breakdown_check(dt)


class Steering(ShipComponent):
    def __init__(self, name, rotation_speed, power_usage, weight_rating, weight, reliability, lifespan, price, age=0):
        super(Steering, self).__init__(name, weight, reliability, lifespan, price, age)
        self.rotation_speed = rotation_speed / 1000. #per ms
        self.power_usage = power_usage / 1000. #per ms
        self.weight_rating = weight_rating

    def rotate(self, dt, ship, direction):
        """"
        Rotate the ship by the ship's rotation speed. Direction should
        be 1 (left rotation) or -1 (right).
        """
        if ship.battery.power >= self.power_usage * dt:
            weight = ship.get_weight()
            if weight > self.weight_rating:
                overload = weight / float(self.weight_rating)
                rot_speed = (self.rotation_speed * dt * direction) / overload
            else:
                rot_speed = self.rotation_speed * dt * direction
            ship.angle += rot_speed
            ship.angle = ship.angle % TWOPI
            ship.image = pg.transform.rotate(ship.base_image, math.degrees(ship.angle))
            ship.rect = ship.image.get_rect(center=ship.pos)
            ship.battery.power -= self.power_usage * dt

    def update(self, dt, ship):
        self.age += dt
        self.repair_timer += dt
        if self.broken_down:
            if self.repair_timer >= self.repair_time:
                self.broken_down = False
        self.breakdown_check(dt)


class Generator(ShipComponent):
    def __init__(self, name, output, efficiency, weight, reliability, lifespan, price, age=0):
        super(Generator, self).__init__(name, weight, reliability, lifespan, price, age)
        self.max_output = output / 1000. #Megajoules per ms
        self.max_efficiency = efficiency
        self.efficiency = efficiency

    def update(self, dt, ship):
        self.age += dt
        self.repair_timer += dt
        self.efficiency = self.max_efficiency * (1 - (max(1, self.age)/self.lifespan))
        self.output = self.max_output * (1 - (max(1, self.age)/self.lifespan))
        if self.broken_down:
            if self.repair_timer >= self.repair_time:
                self.broken_down = False
        else:
            self.generate_power(dt, ship)
        self.breakdown_check(dt)

    def generate_power(self, dt, ship):
        battery = ship.battery
        power_need = min(battery.capacity - battery.power, self.output * dt)
        consumption_rate = 1 / float(self.efficiency)
        fuel_need = power_need * consumption_rate
        if ship.fuel_tank.fuel >= fuel_need:
            used = power_need * consumption_rate
            battery.power += power_need
            ship.fuel_tank.fuel -= used
        else:
            used = ship.fuel_tank.fuel
            ship.fuel_tank.fuel = 0
            battery.power += used * self.efficiency


class BatteryArray(ShipComponent):
    """
    Power generated by generator is fed to batteries for use. Batteries
    lose capacity over time.
    """
    def __init__(self, name, capacity, weight, reliability, lifespan, price, age=0):
        super(BatteryArray, self).__init__(name, weight, reliability, lifespan, price, age)
        self.max_capacity = capacity
        self.capacity = capacity #Megajoules
        self.power = capacity


    def update(self, dt, ship):
        self.age += dt
        self.capacity = int(self.max_capacity * (1 - (self.age/self.lifespan)))


class FuelTank(ShipComponent):
    """Just a tank for holding fuel."""
    def __init__(self, name, capacity, weight, reliability, lifespan, price, age=0):
        super(FuelTank, self).__init__(name, weight, reliability, lifespan, price, age)
        self.max_capacity = capacity
        self.capacity = capacity
        self.fuel = capacity

    def update(self, dt, ship):
        pass


class Laser(ShipComponent):
    def __init__(self, name, damage, beam_duration, cooldown_duration, beam_speed,
                        power_usage, beam_image,  fire_sound, weight, reliability,
                        lifespan, price, age=0):
        super(Laser, self).__init__(name, weight, reliability, lifespan, price, age)
        self.damage = damage
        self.beam_duration = beam_duration
        self.cooldown_duration = cooldown_duration
        self.cooldown = cooldown_duration
        self.beam_speed = beam_speed
        self.beam_image = beam_image
        self.power_usage = power_usage

        self.fire_sound = prepare.SFX[fire_sound]

    def update(self, dt, ship):
        self.cooldown += dt
        
    def fire(self, dt, ship):
        if (self.cooldown >= self.cooldown_duration and
                ship.battery.power >= self.power_usage):
            beam = laser_beam.LaserBeam(ship.pos, ship.angle, self.beam_speed,
                                                           self.beam_image, self.beam_duration,
                                                           self.damage)
            ship.projectiles.add(beam)
            self.cooldown = 0
            self.fire_sound.play()
            ship.battery.power -= self.power_usage


class Shield(ShipComponent):
    def __init__(self, name, damage_reduction, power_usage, weight, reliability, lifespan, price, age=0):
        super(Shield, self).__init__(name, weight, reliability, lifespan, price, age)
        self.damage_reduction = damage_reduction
        self.power_usage = power_usage

    def update(self, dt, ship):
        pass