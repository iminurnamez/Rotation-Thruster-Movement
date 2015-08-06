import math
import ship_components

PI = math.pi

#lifespan is in minutes
#speeds are in pixels/second


#name, damage_resistance, hit_points, image, cargo_tonnage, weight, reliability, lifespan, price, age=0
HULLS = {
        "Rikkati Ratchet":          ("Rikkati Ratchet", 1,  1000, "bluecargoship", 200, 100, .6, 60, 300),
        "Rikkati Ratchet XL":     ("Rikkati Ratchet XL", 1, 1000, "bluecargoship", 240, 150, .6, 60, 400),
        "Rikkati Rattler":        ("Rikkati Rattler", 1, 1000, "bluecruiser", 20, 60, .6, 60, 400),
        "Rikkati Fizzle":       ("Rikkati Fizzle", 1, 1000, "blueshuttlenoweps", 30, 30, .6, 60, 300),

        "Grindstone Gabbro":  ("Grindstone Gabbro", 2, 1000, "bluecargoship", 220, 100, .7, 60, 400),
        "Grindstone Basalt":    ("Grindstone Basalt", 2,  1000, "bluecargoship", 300, 160, .7, 60, 500),
        "Grindstone Monolith": ("Grindstone Monolith", 3, 1000, "bluecargoship", 200, 120, .7, 60, 600),
        "Grindstone Obelisk":   ("Grindstone Obelisk", 5, 1000, "bluecarrier", 100, 500, .7, 60, 700),
        "Grindstone Monument": ("Grindstone Monument", 6, 1000, "bluecarrier", 100, 500, .7, 60, 800),
        "Grindstone Obsidian": ("Grindstone Obsidian", 4, 1000, "bluedestroyer", 30, 200, .7, 60, 900),
        "Grindstone Electrum": ("Grindstone Electrum", 5, 1000, "bluedestroyer", 30, 200, .7, 60, 1000),

        "Imperial Cruiser":      ("Imperial Cruiser", 2, 1000, "cruiser", 10, 100, .7, 60, 500),
        "Imperial Destroyer":  ("Imperial Destroyer", 4, 1000, "destroyer", 25, 100, .7, 60, 900),
        "Imperial Carrier":      ("Imperial Carrier", 4, 1000, "carrier", 100, 100, .7, 60, 700),
        "Imperial Transport":  ("Imperial Transport", 2, 1000, "cargoship", 200, 100, .7, 60, 400),
        "Imperial Shuttle":     ("Imperial Shuttle", 2, 1000, "shuttlenoweps", 30, 40, .7, 60, 300)
        }


#name, acceleration, max_speed, power_usage, weight_rating, weight, reliability, lifespan, price
THRUSTERS ={
        "Rikkati Everfail 30": ("Rikkati Everfail 30", .05, 210, 30, 100, 10, .6, 15, 300),
        "Rikkati Everfail 50": ("Rikkati Everfail 50", .06, 210, 5, 120, 10, .6, 15, 400),
        "Wonk E-Drive E30": ("Wonk E-Drive E30", .08, 250, 5, 130, 10, .7, 15, 500),

        "Werkhors Taurus": ("Werkhors Taurus", .03, 170, 5, 200, 10, .9, 15, 400),
        "Werkhors Atlas": ("Werkhors Atlas", .03, 190, 5, 200, 10, .9, 15, 500),
        "Werkhors Mercury": ("Werkhors Mercury", .05, 220, 5, 200, 10, .9, 15, 600),

        "Parr Mediocrity Drive": ( "Parr Mediocrity Drive", .1, 370, 5, 145, 10, .8, 15, 700),

        "Luxgo": ("Luxgo", .2, 420, 5, 110, 10, .95, 15, 800)
        }


#deceleration, min_speed, power_usage, wight_rating, weight, reliability, lifespan, age=0
RETRO_THRUSTERS = {
        "Rikkati Screecher": ("Rikkati Screecher", .08, -14, 20, 100, 4, .6, 10, 300),
        "Wonk Reverb": ("Wonk Reverb", .09, -14, 5, 105, 4, .9, 10, 400),
        "Werkhors T-20": ("Werkhors T-20", .06, -14, 5, 200, 4, .9, 20, 400),
        "Werkhors T-25": ("Werkhors T-25", .07, -14, 5, 200, 4, .9, 20, 500),
        "Parr GIR": ("Parr GIR", .1, -14, 4, 145, 4, .8, 10, 600),
        "Parr GIR II": ("Parr GIR II", .13, -14, 4, 145, 4, .8, 10, 700),
        "Ondyme Arrester": ("Ondyme Arrester", .2, -29, 3, 150, 3, .95, 15, 800)
        }


#rotation_speed, power_usage, weight_rating, weight, reliability, lifespan, age=0
STEERING = {
        "Rikkati Slugger": ("Rikkati Slugger", .25 * PI, 3, 100, 2, .6, 10, 300),
        "Ondyme Maverick": ("Ondyme Maverick", .5 * PI, 3, 160, 2, .9, 20, 800)
        }



#name, output, efficiency, weight, reliability, lifespan, age=0
GENERATORS = {
        "Rikkati Flicker": ("Rikkati Flicker", 25, .7, 5, .6, 15, 300),
        "Wonk E-23": ("Wonk E-23", 23, .75, 5, .6, 15, 400),
        "Wonk E-42": ("Wonk E-42", 42, .75, 5, .6, 15, 500),
        "Wonk E-137": ("Wonk E-137", 137, .75, 5, .6, 15, 600),

        "Swank E-Tech": ("Swank E-Tech", 30, .9, 5, .6, 15, 700),
        "Swank E-Tech XR": ("Swank E-Tech XR", 55, .9, 5, .6, 15, 800)
        }



#name, capacity, weight, reliability, life_span, age=0
BATTERIES = {
        "Rikkati Ephemera": ("Rikkati Ephemera", 18, 7, .6, 10, 300),
        "Swank Q-Cell": ("Swank Q-Cell", 30, 7, .85, 10, 400),
        "Swank R-Cell": ("Swank R-Cell", 50, 7.5, .85, 10, 500),
        "Zaptech Z-20": ("Zaptech Z-20", 20, 5, .9, 15, 350)
        }


#name, capacity, weight, reliability, lifespan, age=0
FUEL_TANKS = {
        "Fueltech F-20": ("Fueltech F-20", 2000, 2, .8, 20, 300),
        "Fueltech F-50": ("Fueltech F-50", 5000, 5, .8, 20, 400),
        "Fueltech F-100": ("Fueltech F-100", 10000, 10, .8, 20, 500),
        "Fueltech F-150": ("Fueltech F-150", 15000, 15, .8, 20, 600),
        "Fueltech F-200": ("Fueltech F-200", 20000, 20, .8, 20, 700)
        }


#name, damage, beam_duration, cooldown_duration, beam_speed,
#power_usage, beam_image,  fire_sound, weight, reliability,
#lifespan, price, age=0

LASERS = {
        "Shlocky Spitter": ("Shlocky Spitter", 5, 1500, 500, 500, 10, "smallbeamblue", "laser2", 5, .8, 20, 300),
        "Shlocky Spitray": ("Shlocky Spitray", 10, 1200, 500, 500, 18, "smallbeamgreen", "laser3", 10, .8, 20, 400),
        "Blastech Scorcher": ("Blastech Scorcher", 3, 2000, 600, 500, 6, "smallbeampurple", "laser4", 7, .8, 20, 500),
        "Blastech Annihilator": ("Blastech Annihilator", 20, 2000, 700, 500, 25, "fatbeamyellow", "laser5", 13, .8, 20, 600)
        }


#damage_reduction, power_usage, weight, reliability, lifespan, age=0
SHIELDS = {
        "Rikkati Porosity": ("Rikkati Porosity", 1, 3, 4, .6, 10, 300)
        }


SHIP_PACKAGES = {
    "Player Default": ("Rikkati Fizzle", "Rikkati Everfail 30", "Rikkati Screecher", "Rikkati Slugger", "Rikkati Flicker", "Rikkati Ephemera", "Fueltech F-20", "Shlocky Spitter", "Rikkati Porosity"),
    "Pimpmobile": ("Rikkati Rattler", "Luxgo", "Ondyme Arrester", "Ondyme Maverick", "Swank E-Tech XR", "Swank R-Cell", "Fueltech F-100", "Shlocky Spitray", "Rikkati Porosity"),
    "Imperial Shuttle": ("Imperial Shuttle", "Werkhors Taurus", "Werkhors T-20", "Rikkati Slugger", "Wonk E-23", "Rikkati Ephemera", "Fueltech F-50", "Blastech Scorcher", "Rikkati Porosity"),
    "Imperial Cruiser": ("Imperial Cruiser", "Rikkati Everfail 50", "Wonk Reverb", "Rikkati Slugger", "Wonk E-23", "Swank Q-Cell", "Fueltech F-50", "Blastech Scorcher", "Rikkati Porosity")
    }

SHIPS = {}
for name, args in SHIP_PACKAGES.items():
    SHIPS[name] = (HULLS[args[0]], THRUSTERS[args[1]], RETRO_THRUSTERS[args[2]], STEERING[args[3]],
                            GENERATORS[args[4]], BATTERIES[args[5]], FUEL_TANKS[args[6]], LASERS[args[7]], SHIELDS[args[8]])


def make_ship(name):
    args = SHIPS[name]
    init_args = (
            ship_components.Hull(*args[0]),
            ship_components.Thruster(*args[1]),
            ship_components.RetroThruster(*args[2]),
            ship_components.Steering(*args[3]),
            ship_components.Generator(*args[4]),
            ship_components.BatteryArray(*args[5]),
            ship_components.FuelTank(*args[6]),
            ship_components.Laser(*args[7]),
            ship_components.Shield(*args[8])
        )
    return init_args

