"""
     _        _                 _     _     
    / \   ___| |_ ___ _ __ ___ (_) __| |___ 
   / _ \ / __| __/ _ \ '__/ _ \| |/ _` / __|
  / ___ \\__ \ ||  __/ | | (_) | | (_| \__ \
 /_/   \_\___/\__\___|_|  \___/|_|\__,_|___/
                                            
Asteroids clone by Janne Tompuri

Game play:
Your goal is to destroy as many asteroids as possible. 
Each destroyed asteroid gives you 10 points. The game 
is over when the ship collides with an asteroid.

Controls: 
* UP arrow to accelerate the space ship
* LEFT and RIGHT arrows to turn the ship
* SPACE for firing lasers

"""

import pygame
from random import randint, uniform
from math import sin, cos, radians, sqrt

# Initialize Pygame
pygame.init()

# Constant values
GREEN = (25, 210, 9)
BACKGROUND_COLOR = (0, 32, 0)
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# Set up the drawing window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids")
screen.fill(BACKGROUND_COLOR)

# Load sound effect
laser_sound = pygame.mixer.Sound("shoot.wav")
asteroid_hit_sound = pygame.mixer.Sound("asteroid_hit.wav")
asteroid_created = pygame.mixer.Sound("spawn.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")

# Set volume for sound effects (0.0 to 1.0)
for sound in [laser_sound, asteroid_hit_sound, asteroid_created, explosion_sound]:
    sound.set_volume(0.1)

# Fonts
title_font = pygame.font.Font("Hyperspace.otf", 48)
score_font = pygame.font.Font("Hyperspace.otf", 24)

# Timer for blinking text
blink_timer = 0
blink_interval = 500  # Interval in milliseconds
show_text = True

# Clock
clock = pygame.time.Clock()

class Ship:
    def __init__(self):
        self.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.angle = 0
        self.speed = (0, 0)
        self.max_speed = 4
        self.polygon = [(-5.0, -5.0), (10.0, 0.0), (-5.0, 5.0), (-2.0, 0.0)]

    def rotate(self, direction):
        self.angle += 5 * direction

    def accelerate(self):
        new_speed = (self.speed[0] + 0.1 * cos(radians(self.angle)), self.speed[1] + 0.1 * sin(radians(self.angle)))
        if sqrt(new_speed[0] ** 2 + new_speed[1] ** 2) < self.max_speed:
            self.speed = new_speed

    def update_position(self):
        x, y = self.position
        if x < 0:
            self.position = (SCREEN_WIDTH, y)
        if x > SCREEN_WIDTH:
            self.position = (0, y)
        if y < 0:
            self.position = (x, SCREEN_HEIGHT)
        if y > SCREEN_HEIGHT:
            self.position = (x, 0)
        self.position = (self.position[0] + self.speed[0], self.position[1] + self.speed[1])

    def draw(self):
        rotated_ship = rotate_polygon(self.polygon, self.angle)
        transformed_ship = translate_polygon(rotated_ship, self.position)
        pygame.draw.polygon(screen, GREEN, transformed_ship, 1)

class Laser:
    def __init__(self, position, angle):
        self.position = position
        self.angle = angle
        self.polygon = [(10.0, 0.0), (6.0, 0.0)]

    def update_position(self):
        laser_offset = (8 * cos(radians(self.angle)), 8 * sin(radians(self.angle)))
        self.position = (self.position[0] + laser_offset[0], self.position[1] + laser_offset[1])

    def draw(self):
        rotated_laser = rotate_polygon(self.polygon, self.angle)
        laser = translate_polygon(rotated_laser, self.position)
        pygame.draw.polygon(screen, GREEN, laser, 1)

class Asteroid:
    def __init__(self):
        edge = randint(0, 3)
        if edge == 0:  # Top edge
            x = randint(0, SCREEN_WIDTH)
            y = 0
        elif edge == 1:  # Right edge
            x = SCREEN_WIDTH
            y = randint(0, SCREEN_HEIGHT)
        elif edge == 2:  # Bottom edge
            x = randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT
        else:  # Left edge
            x = 0
            y = randint(0, SCREEN_HEIGHT)

        self.position = (x, y)
        self.angle = randint(0, 360)
        self.rotation = self.angle
        self.speed = randint(1, 30) / 10
        self.size = randint(20, 50)
        self.rotation_speed = uniform(-1, 1)
        self.polygon = generate_random_asteroid(self.size)

    def update_position(self):
        x, y = self.position
        x += self.speed * cos(radians(self.angle))
        y += self.speed * sin(radians(self.angle))
        self.position = (x % SCREEN_WIDTH, y % SCREEN_HEIGHT)
        self.rotation += self.rotation_speed

    def draw(self):
        rotated_polygon = rotate_polygon(self.polygon, self.rotation)
        transformed_polygon = translate_polygon(rotated_polygon, self.position)
        pygame.draw.polygon(screen, GREEN, transformed_polygon, 1)

def rotate_polygon(vertices, angle):
    rotated_vertices = []
    angle_rad = radians(angle)
    for x, y in vertices:
        x_new = x * cos(angle_rad) - y * sin(angle_rad)
        y_new = x * sin(angle_rad) + y * cos(angle_rad)
        rotated_vertices.append((x_new, y_new))
    return rotated_vertices

def translate_polygon(vertices, offset):
    dx, dy = offset
    return [(x + dx, y + dy) for x, y in vertices]

def check_screen_boundaries(point):
    return point[0] < 0 or point[0] > SCREEN_WIDTH or point[1] < 0 or point[1] > SCREEN_HEIGHT

def check_collision(polygon1, polygon2):
    def project_polygon(polygon, axis):
        min_proj = float('inf')
        max_proj = float('-inf')
        for x, y in polygon:
            projection = (x * axis[0] + y * axis[1])
            min_proj = min(min_proj, projection)
            max_proj = max(max_proj, projection)
        return min_proj, max_proj

    def polygons_intersect(polygon1, polygon2):
        for polygon in [polygon1, polygon2]:
            for i1 in range(len(polygon)):
                i2 = (i1 + 1) % len(polygon)
                p1 = polygon[i1]
                p2 = polygon[i2]
                normal = (p2[1] - p1[1], p1[0] - p2[0])
                min1, max1 = project_polygon(polygon1, normal)
                min2, max2 = project_polygon(polygon2, normal)
                if max1 < min2 or max2 < min1:
                    return False
        return True

    return polygons_intersect(polygon1, polygon2)

def generate_random_asteroid(size, num_vertices=8):
    angle_step = 360 / num_vertices
    vertices = []
    for i in range(num_vertices):
        asteroid_angle = radians(i * angle_step)
        radius = randint(size // 2, size)
        x = radius * cos(asteroid_angle)
        y = radius * sin(asteroid_angle)
        vertices.append((x, y))
    return vertices

def read_hiscore(file_path="hiscore.txt"):
    try:
        with open(file_path, "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0

def write_hiscore(hiscore, file_path="hiscore.txt"):
    with open(file_path, "w") as file:
        file.write(str(hiscore))

def draw_scores(score, hiscore):
    score_text = (5 - len(str(score))) * "0" + str(score)
    score_surface = score_font.render(score_text, True, GREEN)
    screen.blit(score_surface, (20, 10))

    hiscore_text = "Hi " + (5 - len(str(hiscore))) * "0" + str(hiscore)
    hiscore_surface = score_font.render(hiscore_text, True, GREEN)
    screen.blit(hiscore_surface, (505, 10))

def start_game_loop():
    global show_text, blink_timer, blink_interval
    start_game = False
    while not start_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                start_game = True

        screen.fill(BACKGROUND_COLOR)

        title_text = "Asteroids"
        title_surface = title_font.render(title_text, True, GREEN)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        screen.blit(title_surface, title_rect)

        current_time = pygame.time.get_ticks()
        if current_time - blink_timer > blink_interval:
            show_text = not show_text
            blink_timer = current_time

        if show_text:
            start_text = "Press any key to start"
            start_surface = score_font.render(start_text, True, GREEN)
            start_rect = start_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
            screen.blit(start_surface, start_rect)

        pygame.display.flip()
        clock.tick(60)

def main_game_loop():
    global score, hiscore
    ship = Ship()
    lasers = []
    asteroids = [Asteroid() for _ in range(10)]
    score = 0
    hiscore = read_hiscore()
    running = True
    last_fire = 0
    fire_delay = 50
    asteroid_timer = 0
    asteroid_delay = 3000
    min_asteroid_delay = 200
    delay_decrement = 0.8
    invincibility_duration = 3000  # 3 seconds of invincibility
    invincibility_start_time = pygame.time.get_ticks()
    button_left = False
    button_right = False
    button_up = False
    button_space = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    button_left = True
                if event.key == pygame.K_RIGHT:
                    button_right = True
                if event.key == pygame.K_UP:
                    button_up = True
                if event.key == pygame.K_SPACE:
                    button_space = True

            # Check for key releases
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    button_left = False
                if event.key == pygame.K_RIGHT:
                    button_right = False
                if event.key == pygame.K_UP:
                    button_up = False
                if event.key == pygame.K_SPACE:
                    button_space = False

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if button_left:
            ship.rotate(-1)
        if button_right:
            ship.rotate(1)
        if button_up:
            ship.accelerate()
        if button_space:
            current_time = pygame.time.get_ticks()
            if current_time - last_fire > fire_delay:
                lasers.append(Laser(ship.position, ship.angle))
                last_fire = current_time
                laser_sound.play()

        screen.fill(BACKGROUND_COLOR)

        ship.update_position()
        ship.draw()

        for laser in lasers:
            laser.update_position()
            if check_screen_boundaries(laser.position):
                lasers.remove(laser)  
            else:
                laser.draw()

        for asteroid in asteroids:
            asteroid.update_position()
            asteroid.draw()

        for laser in lasers:
            rotated_laser_polygon = rotate_polygon(laser.polygon, laser.angle)
            translated_laser_polygon = translate_polygon(rotated_laser_polygon, laser.position)
            for asteroid in asteroids:
                rotated_asteroid_polygon = rotate_polygon(asteroid.polygon, asteroid.angle)
                translated_asteroid_polygon = translate_polygon(rotated_asteroid_polygon, asteroid.position)
                if check_collision(translated_laser_polygon, translated_asteroid_polygon):
                    asteroids.remove(asteroid)
                    lasers.remove(laser)
                    score += 10
                    asteroid_hit_sound.play()
                    break

        current_time = pygame.time.get_ticks()
        if current_time - invincibility_start_time > invincibility_duration:
            rotated_ship_polygon = rotate_polygon(ship.polygon, ship.angle)
            translated_ship_polygon = translate_polygon(rotated_ship_polygon, ship.position)
            for asteroid in asteroids:
                rotated_asteroid_polygon = rotate_polygon(asteroid.polygon, asteroid.angle)
                translated_asteroid_polygon = translate_polygon(rotated_asteroid_polygon, asteroid.position)
                if check_collision(translated_ship_polygon, translated_asteroid_polygon):
                    running = False
                    explosion_sound.play()
                    break

        current_time = pygame.time.get_ticks()
        if current_time - asteroid_timer > asteroid_delay:
            asteroids.append(Asteroid())
            asteroid_created.play()
            asteroid_timer = current_time
            if asteroid_delay > min_asteroid_delay:
                asteroid_delay *= delay_decrement

        draw_scores(score, hiscore)
        pygame.display.flip()
        clock.tick(60)

def game_over_loop():
    global show_text, blink_timer, blink_interval, score, hiscore
    new_hiscore = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                main_game_loop()

        screen.fill(BACKGROUND_COLOR)

        game_over_text = "Game Over"
        text_surface = title_font.render(game_over_text, True, GREEN)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        screen.blit(text_surface, text_rect)

        if score > hiscore:
            hiscore = score
            write_hiscore(hiscore)
            new_hiscore = True

        if new_hiscore:
            hiscore_text = "New hiscore"
            hiscore_surface = score_font.render(hiscore_text, True, GREEN)
            hiscore_rect = hiscore_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(hiscore_surface, hiscore_rect)

        current_time = pygame.time.get_ticks()
        if current_time - blink_timer > blink_interval:
            show_text = not show_text
            blink_timer = current_time

        if show_text:
            restart_text = "Press any key to restart"
            restart_surface = score_font.render(restart_text, True, GREEN)
            restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
            screen.blit(restart_surface, restart_rect)

        draw_scores(score, hiscore)
        pygame.display.flip()
        clock.tick(60)

def main():
    start_game_loop()
    main_game_loop()
    game_over_loop()

main()