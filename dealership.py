import random
import ship_components as sc
import products
import cargo_prices


SIZE_TO_QTY = {
            "tiny": 2,
            "small": 3,
            "medium": 5,
            "large": 8,
            "giant": 12
        }
        
CATEGORIES = {"hull": products.HULLS,
                        "thruster": products.THRUSTERS,
                        "retro_thruster": products.RETRO_THRUSTERS, 
                        "steering": products.STEERING,
                        "generator": products.GENERATORS,
                        "battery": products.BATTERIES,
                        "fuel_tank": products.FUEL_TANKS,
                        "laser": products.LASERS,
                        "shield": products.SHIELDS
        }
        
PRODUCT_CLASSES = {
            "hull": sc.Hull,
            "thruster": sc.Thruster,
            "retro_thruster": sc.RetroThruster, 
            "steering": sc.Steering,
            "generator": sc.Generator,
            "battery": sc.BatteryArray,
            "fuel_tank": sc.FuelTank,
            "laser": sc.Laser,
            "shield": sc.Shield
        }
        

class Dealership(object):
    def __init__(self, starport):
        self.starport = starport
        self.size = starport.size
        self.parts = {k: [] for k in CATEGORIES}
        self.get_new_parts()
        self.parts_refresh_time = 60000
        self.refresh_timer = 0
        
    def get_new_parts(self):
        for k in self.parts:
            self.parts[k] = []

        for _ in range(SIZE_TO_QTY[self.size]):
            part_type, category = random.choice(CATEGORIES.items())
            product_name = random.choice(category.keys())
            product = PRODUCT_CLASSES[part_type](*category[product_name])
            self.parts[part_type].append(product)

    def update(self, dt):
        if self.refresh_timer >= self.parts_refresh_time:
            self.resh_timer -= self.parts_refresh_time
            self.get_new_parts()

