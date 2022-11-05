import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 800, 800  # Size of the window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # Size of the window
# Name of the main window
pygame.display.set_caption("Heidius's Space Invader.")

# Load images
RED_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player player
YELLOW_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_yellow.png"))

# Laser
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
# The background is scaled to fill the whole window.
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Ship:  # OOP -> This is the papa class
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.laser = []
        self.cool_down_counter = 0  # Cool down for the lasers
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.laser:
            laser.draw(window)
    
    def move_laser(self, vel, obj):
        self.cooldown()
        for laser in self.laser:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.laser.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.laser.remove(laser)
   
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.laser.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
            return self.ship_img.get_width()
    def get_height(self):
            return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        # This establish the img of the player and the next line the laser
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)  # Mask works with pixel collision
        self.max_health = health  

    def move_laser(self, vel, objs):
        self.cooldown()
        for laser in self.laser:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.laser.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.laser:
                            self.laser.remove(laser) 
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
   
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    #Dictionary that pass the color as a String
    COLOR_MAP = { "red": (RED_SHIP, RED_LASER), "green": (GREEN_SHIP, GREEN_LASER), "blue": (BLUE_SHIP, BLUE_LASER) } 

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.laser.append(laser)
            self.cool_down_counter = 1

class Laser:
    def __init__(self, x, y, img):
        self.x = x 
        self.y = y 
        self.img = img 
        self.mask = pygame.mask.from_surface(self.img)
   
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel
   
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(obj, self)

#This function defines the collision condition
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Main loop
def main():
    run = True
    FPS = 60  # Speed of the game
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 25)
    lost_font = pygame.font.SysFont("comicsans", 25)

    
    #Enemies as a list []
    enemies = []
    wave_length = 5
    enemy_vel = 1
    # Speed of the player
    player_vel = 5 
    laser_vel = 5

    player = Player(300, 400)
    
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # Draw text for Lives and Level
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 0, 0))
        level_label = main_font.render(f"Level: {level}", 1, (0, 255, 0))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        
        #Don't need to define draw method since is inheritances from the father.
        for enemy in enemies:
            enemy.draw(WIN)  

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Meeeeeh!!", 1, (255,0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        # Update display
        pygame.display.update()


    while run:
        # Limit frames per second. Established on 60
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            #Generate the enemies randomly 
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit()

        keys = pygame.key.get_pressed() #Adding player.get_ methods keep the ship within the window.
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:  # Left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:  # Right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:  # Up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() < HEIGHT:  # Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        #Once the enemies reach the bottom, it subtract a life.
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel, player)

            #Enemies will randomly shoot twice every second    
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_laser(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()
