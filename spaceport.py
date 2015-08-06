import random
import pygame as pg
import prepare
import angles
import cargo_prices
import dealership


def render_font(font, text, color):
    return font.render(text, True, color)

class Spaceport(object):
    def __init__(self, planet):
        self.planet = planet
        self.size = random.choice(("tiny", "small", "medium", "large", "giant"))
        self.prices = {k: v for k, v in cargo_prices.BASE_PRICES.items()}
        self.economy_timer = 0
        self.economy_update_time = 15000
        self.cargo = {k: 0 for k in self.prices}
        self.products = random.sample(self.prices.keys(), dealership.SIZE_TO_QTY[self.size])
        self.ui = SpaceportUI(self)
        self.dealership = dealership.Dealership(self)
        self.create_products()
        
    def nearest_producer_distance(self, cargo_item, planets):
        nearest = None
        for planet in planets:
            if planet is not self.planet:
                if cargo_item in planet.spaceport.products:
                    dist = angles.get_distance(self.planet.pos, planet.pos)
                    if nearest is None or dist < nearest:
                        nearest = dist
        return nearest

    def get_price(self, cargo_item, planets):
        base = cargo_prices.BASE_PRICES[cargo_item]    
        if cargo_item in self.products:
            price = base * random.uniform(.95, 1.05)
        else:
            dist = self.nearest_producer_distance(cargo_item, planets)
            if dist is None:
                dist_mod = 4
            else:    
                dist_mod = max(1, dist / 1000.)
            price = base * dist_mod * random.uniform(.95, 1.05)
        return price

    def update_prices(self, planets):
        for cargo_name in self.prices:
            self.prices[cargo_name] = self.get_price(cargo_name, planets)
                    
    def create_products(self):
        for item in self.products:
            self.cargo[item] += 1 #####
            
    def update(self, dt, planets):
        self.economy_timer += dt
        if self.economy_timer >= self.economy_update_time:
            self.economy_timer -= self.economy_update_time
            self.update_prices(planets)
            self.create_products()            
        self.dealership.update(dt)
            
            
class Button(object):
    def __init__(self, topleft, size, font, text, color, callback, args):
        self.label = render_font(font, text, color)
        
        self.rect = pg.Rect(topleft, size)
        self.label_rect = self.label.get_rect(center=self.rect.center)
        self.image = pg.Surface(size).convert()
        self.image.fill((0, 200, 200))
        self.image.set_alpha(100)
        pg.draw.rect(self.image, pg.Color(0, 220, 220), ((0, 0), size), 1)
        
        self.callback = callback
        self.args = args
        
    def get_event(self, event, player):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback(*self.args)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        surface.blit(self.label, self.label_rect)
        
        
class SpaceportUI(object):
    def __init__(self, spaceport):
        self.port = spaceport
        w, h = prepare.SCREEN_SIZE
        self.rect = pg.Rect(0, 0, w, h)
        self.font = pg.font.Font(prepare.FONT, 12)
        self.big_font = pg.font.Font(prepare.FONT, 18)
        self.surf = pg.Surface(self.rect.size)
        self.surf.fill(pg.Color(0, 220, 220))
        self.surf.set_alpha(90)
        self.bg = pg.Surface(self.rect.size)
        self.bg.fill(prepare.BACKGROUND_COLOR)
        self.bg.set_alpha(90)
        
    def sell_part(self, player, part_type, part):
        if player.cash >= part.price:
            player.add_part(part_type, part)
            player.cash -= part.price
            self.port.dealership.parts[part_type].remove(part)
                    
    def buy(self, player, item):
        price = self.port.prices[item]
        if player.cargo[item] > 0:
            player.cargo[item] -= 1
            self.port.cargo[item] += 1
            player.cash += price
        
    def buy_all(self, player, item):
        price = self.port.prices[item]
        qty = player.cargo[item]
        tot_price = price * qty
        player.cargo[item] = 0
        player.cash += tot_price
        self.port.cargo[item] += qty
    
    def sell(self, player, item):
        price = self.port.prices[item]
        max_load = player.parts["hull"].tonnage - player.get_cargo_weight()
        if player.cash > price and max_load > 0:
            player.cash -= price
            player.cargo[item] += 1
            self.port.cargo[item] -= 1

    def sell_all(self, player, item):
        qty = self.port.cargo[item]
        price = self.port.prices[item]
        max_load = player.parts["hull"].tonnage - player.get_cargo_weight()
        qty = min(max_load, qty)
        tot_price = qty * price
        if player.cash >= tot_price:
            self.port.cargo[item] -= qty
            player.cargo[item] += qty
            player.cash -= tot_price
            
    def depart(self, player):
        player.docked = None
        player.dockable = None
        
    def update(self, dt, player):
        self.planet_image = player.dockable.image
        w, h = prepare.SCREEN_SIZE
        self.planet_rect = self.planet_image.get_rect(center=(w//2, h//2))
        text_color = pg.Color(0, 240, 240)
        self.labels = []
        port_name = render_font(self.big_font, "Spaceport", text_color)
        ship_name = render_font(self.big_font, "Spaceship", text_color)
        self.labels.append((port_name, (20, 5)))
        self.labels.append((ship_name, (365, 5)))
        leave_button = Button((self.rect.centerx + (self.rect.w//4), self.rect.bottom - 30), (70, 30),
                                          self.font, "Depart", text_color, self.depart, (player,)) 
        self.buttons = [leave_button]
        left1 = 4
        left2 = 123
        left3 = 158
        left4 = 235
        left5 = 270
        top = 30
        for item in sorted(self.port.prices.keys()):
            price = "{:.2f}".format(self.port.prices[item])
            qty = self.port.cargo[item]
            if qty > 0:
                button1 = Button((left4, top), (28, 16), self.font, "Buy", text_color,
                                          self.sell, (player, item))
                button2 = Button((left5, top), (50, 16), self.font, "Buy All", text_color,
                                          self.sell_all, (player, item))
                self.buttons.extend([button1, button2])
            for text, pos in ((item, (left1, top)), (qty, (left2, top)), (price, (left3, top))):
                label = render_font(self.font, "{}".format(text), text_color)
                self.labels.append((label, label.get_rect(topleft=pos)))
            top += 18
        shift = 345
        top = 30
        for item in sorted(player.cargo.keys()):
            price = "{:.2f}".format(self.port.prices[item])
            qty = player.cargo[item]
            if qty > 0:
                button1 = Button((left4 + shift, top), (28, 16), self.font, "Sell", text_color, self.buy, (player, item))
                button2 = Button((left5 + shift, top), (60, 16), self.font, "Sell All", text_color, self.buy_all, (player, item))
                self.buttons.extend([button1, button2])
            for text, pos in ((item, (left1 + shift, top)), (qty, (left2 + shift, top)), (price, (left3 + shift, top))):
                label = render_font(self.font, "{}".format(text), text_color)
                self.labels.append((label, label.get_rect(topleft=pos)))
            top += 18
        top = 316
        part_types = sorted(self.port.dealership.parts.keys())
        for part_type in part_types:
            parts = self.port.dealership.parts[part_type]

            for part in parts:
                name = render_font(self.font, "{:16}{:24}{:,}".format(part_type.replace("_", " ").title(), part.name, part.price), text_color)
                self.labels.append((name, name.get_rect(topleft=(left1, top))))
                butt = Button((340, top), (28, 16), self.font, "Buy", text_color, self.sell_part, (player, part_type, part))
                self.buttons.append(butt)
                top += 18
        cash_label = render_font(self.big_font, "GEC {:,.2f}".format(player.cash), text_color)
        self.labels.append((cash_label, cash_label.get_rect(topleft=(420, 320))))
        
    def get_event(self, event, player):
        for button in self.buttons:
            button.get_event(event, player)
            
    def draw(self, surface):
        surface.blit(self.planet_image, self.planet_rect)
        surface.blit(self.bg, (0, 0))
        surface.blit(self.surf, self.rect)
        pg.draw.rect(surface, pg.Color(0, 240, 240), self.rect, 2)
        for label, rect in self.labels:
            surface.blit(label, rect)
        for button in self.buttons:
            button.draw(surface)
    
    
    