import pygame
from random import randint, uniform
from math import sin, cos, radians, sqrt 

# Initialize Pygame
pygame.init()

# Constant values
GREEN = (25, 210, 9)
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# Set up the drawing window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids")
screen.fill((0, 32, 0))

# Ship variables
ship_position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
ship_angle = 0
ship_speed = (0, 0)
max_speed = 4

# Ship polygon
ship_polygon = [(-5, -5), (10, 0), (-5, 5), (-2, 0)]

# Laser polygon
laser_polygon = [(10, 0), (6, 0)]

# Laser time delay
last_fire = 0
fire_delay = 50

# Load laser sound effect
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

# Clock
clock = pygame.time.Clock()

# Buttons
button_left = False
button_right = False
button_up = False
button_space = False


# Asteroid variables
num_asteroids = 10
min_asteroid_delay = 200    # Minimum delay in milliseconds
delay_decrement = 0.8       # Amount to decrease the delay each time

# Timer for blinking text
blink_timer = 0
blink_interval = 500  # Interval in milliseconds
show_text = True

def reset_game():
    global ship_position, ship_angle, ship_speed, score, asteroids, asteroid_timer, asteroid_delay, lasers, button_left, button_right, button_up, button_space, new_hiscore 
    button_left = False
    button_right = False
    button_up = False
    button_space = False
    ship_position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    ship_angle = 0
    ship_speed = (0, 0)
    score = 0
    new_hiscore = False
    lasers = []
    asteroids = []
    asteroid_timer = 0
    asteroid_delay = 3000
    num_asteroids = 10
    for _ in range(num_asteroids):
        create_asteroid()

def generate_random_asteroid(size, num_vertices=8):
    """Generate a random asteroid polygon with a given size and number of vertices."""
    angle_step = 360 / num_vertices
    vertices = []
    for i in range(num_vertices):
        asteroid_angle = radians(i * angle_step)
        radius = randint(size // 2, size)
        x = radius * cos(asteroid_angle)
        y = radius * sin(asteroid_angle)
        vertices.append((x, y))
    return vertices

def create_asteroid():
    """Create a new asteroid at a random edge of the screen."""
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

    asteroid_angle = randint(0, 360)
    asteroid_speed = randint(1, 30) / 10
    size = randint(20, 50)
    rotation_speed = uniform(-1, 1)  # Random rotation speed between -1 and 1 degrees per frame
    polygon = generate_random_asteroid(size)
    asteroids.append({'position': (x, y), 'speed' : asteroid_speed, 'rotation' : asteroid_angle, 'angle': asteroid_angle, 'size': size, 'polygon': polygon, 'rotation_speed': rotation_speed})

def rotate_polygon(vertices, angle):
    """Rotates a list of vertices around the origin by a given angle."""
    rotated_vertices = []
    angle_rad = radians(angle)  # Convert angle to radians
    for x, y in vertices:
        x_new = x * cos(angle_rad) - y * sin(angle_rad)
        y_new = x * sin(angle_rad) + y * cos(angle_rad)
        rotated_vertices.append((x_new, y_new))
    return rotated_vertices

def translate_polygon(vertices, offset):
    """Translates a list of vertices by an offset (dx, dy)."""
    dx, dy = offset
    return [(x + dx, y + dy) for x, y in vertices]

def check_screen_boundaries(point):
    """Check if a point is out of the screen boundaries."""
    if point[0] < 0 or point[0] > SCREEN_WIDTH or point[1] < 0 or point[1] > SCREEN_HEIGHT:
        return True
    return False

def check_collision(polygon1, polygon2):
    """Check if two polygons collide using the Separating Axis Theorem (SAT)."""
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

def read_hiscore(file_path="hiscore.txt"):
    try:
        with open(file_path, "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0

# Score variables
score = 0
new_hiscore = False
hiscore = read_hiscore()  # Read the high score from the file

def write_hiscore(hiscore, file_path="hiscore.txt"):
    with open(file_path, "w") as file:
        file.write(str(hiscore))


def draw_scores(score, hiscore):
    # Draw the score text
    score_text = (5 - len(str(score))) * "0" + str(score) 
    score_surface = score_font.render(score_text, True, GREEN)
    screen.blit(score_surface, (20, 10))

    # Draw the hiscore text
    hiscore_text = "Hi " + (5 - len(str(hiscore))) * "0" + str(hiscore) 
    hiscore_surface = score_font.render(hiscore_text, True, GREEN)
    screen.blit(hiscore_surface, (505, 10))

# Starting screen loop
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

        screen.fill((0, 32, 0))

        # Draw the title text
        title_text = "Asteroids"
        title_surface = title_font.render(title_text, True, GREEN)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
        screen.blit(title_surface, title_rect)

        # Blink the start prompt text
        current_time = pygame.time.get_ticks()
        if current_time - blink_timer > blink_interval:
            show_text = not show_text
            blink_timer = current_time

        if show_text:
            start_text = "Press any key to start"
            start_surface = score_font.render(start_text, True, GREEN)
            start_rect = start_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
            screen.blit(start_surface, start_rect)

        pygame.display.flip()
        clock.tick(60)

# Main game loop
def main_game_loop():
    reset_game()
    global button_left, button_right, button_up, button_space, ship_angle, ship_speed, ship_position, score, asteroids, asteroid_timer, asteroid_delay, last_fire
    running = True
    while running:
        for event in pygame.event.get():
            # Check for key presses
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

            # Close window
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Clear the screen
        screen.fill((0, 32, 0))

        # Rotate the ship
        if button_left:
            ship_angle -= 5
        if button_right:
            ship_angle += 5

        # Accelerate the ship
        if button_up:
            new_speed = (ship_speed[0] + 0.1 * cos(radians(ship_angle)), ship_speed[1] + 0.1 * sin(radians(ship_angle)))
            if sqrt(new_speed[0] ** 2 + new_speed[1] ** 2) < max_speed:
                ship_speed = new_speed

        # Check if the ship is out of the screen
        x, y = ship_position
        if x < 0:
            ship_position = (SCREEN_WIDTH, y)
        if x > SCREEN_WIDTH:
            ship_position = (0, y)
        if y < 0:
            ship_position = (x, SCREEN_HEIGHT)
        if y > SCREEN_HEIGHT:
            ship_position = (x, 0)
        
        # Update the ship position
        ship_position = (ship_position[0] + ship_speed[0], ship_position[1] + ship_speed[1])

        # Rotate the ship 
        rotated_ship = rotate_polygon(ship_polygon, ship_angle)

        # Translate the ship to its position
        transformed_ship = translate_polygon(rotated_ship, ship_position)

        # Draw the ship
        pygame.draw.polygon(screen, GREEN, transformed_ship, 1)

        # Update the lasers position
        if button_space:
            current_time = pygame.time.get_ticks()
            if current_time - last_fire > fire_delay:
                rotated_laser = rotate_polygon(laser_polygon, ship_angle)
                laser = translate_polygon(rotated_laser, ship_position)
                lasers.append((laser, ship_angle))
                last_fire = current_time
                laser_sound.play()  # Play the laser sound effect

        # Move the lasers
        for i, (laser, laser_angle) in enumerate(lasers):
            laser_offset = (8 * cos(radians(laser_angle)), 8 * sin(radians(laser_angle)))
            lasers[i] = (translate_polygon(laser, laser_offset), laser_angle)

        # Check if the lasers are out of the screen
        for i, (laser, laser_angle) in enumerate(lasers):
            if check_screen_boundaries(laser[0]):
                lasers.pop(i)  # Remove the laser from the list

        # Draw the lasers
        for laser, _ in lasers:
            pygame.draw.polygon(screen, GREEN, laser, 1)

        # Update the asteroids position
        for asteroid in asteroids:
            x, y = asteroid['position']
            asteroid_angle = asteroid['angle']
            asteroid_speed = asteroid['speed']
            x += asteroid_speed * cos(radians(asteroid_angle))
            y += asteroid_speed * sin(radians(asteroid_angle))
            asteroid['position'] = (x % SCREEN_WIDTH, y % SCREEN_HEIGHT)
            asteroid['rotation'] += asteroid['rotation_speed']  # Update the rotation based on the rotation speed

        # Check for collisions between lasers and asteroids
        for laser in lasers:
            for asteroid in asteroids:
                rotated_polygon = rotate_polygon(asteroid['polygon'], asteroid['rotation'])
                transformed_polygon = translate_polygon(rotated_polygon, asteroid['position'])
                if check_collision(laser[0], transformed_polygon):
                    asteroids.remove(asteroid)
                    lasers.remove(laser)
                    score += 10
                    asteroid_hit_sound.play()  # Play the asteroid hit sound effect
                    break

        # Check for collisions between the ship and asteroids
        for asteroid in asteroids:
            rotated_polygon = rotate_polygon(asteroid['polygon'], asteroid['rotation'])
            transformed_polygon = translate_polygon(rotated_polygon, asteroid['position'])
            if check_collision(transformed_ship, transformed_polygon):
                running = False
                explosion_sound.play()
                break

        # Create new asteroids based on the timer
        current_time = pygame.time.get_ticks()
        if current_time - asteroid_timer > asteroid_delay:
            create_asteroid()
            asteroid_created.play()  # Play the asteroid created sound effect
            asteroid_timer = current_time
            if asteroid_delay > min_asteroid_delay:
                asteroid_delay *= delay_decrement  # Decrease the delay

        # Draw the asteroids
        for asteroid in asteroids:
            x, y = asteroid['position']
            polygon = asteroid['polygon']
            rotated_polygon = rotate_polygon(polygon, asteroid['rotation'])
            transformed_polygon = translate_polygon(rotated_polygon, (x, y))
            pygame.draw.polygon(screen, GREEN, transformed_polygon, 1)

        # Draw the score texts
        draw_scores(score, hiscore)

        pygame.display.flip()
        clock.tick(60)

# Game over loop
def game_over_loop():
    global show_text, blink_timer, blink_interval, hiscore, new_hiscore

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                reset_game()
                main_game_loop()

        screen.fill((0, 32, 0))

        # Draw the game over text
        game_over_text = "Game Over"
        text_surface = title_font.render(game_over_text, True, GREEN)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
        screen.blit(text_surface, text_rect)

        # Draw the hiscore text
        if score > hiscore:
            hiscore = score # Update the hiscore
            write_hiscore(hiscore)  # Write the new hiscore to the file
            new_hiscore = True

        if new_hiscore:
            hiscore_text = "New hiscore"
            hiscore_surface = score_font.render(hiscore_text, True, GREEN)
            hiscore_rect = hiscore_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(hiscore_surface, hiscore_rect)

        # Blink the restart prompt text
        current_time = pygame.time.get_ticks()
        if current_time - blink_timer > blink_interval:
            show_text = not show_text
            blink_timer = current_time

        # Draw the restart prompt text
        if show_text:
            restart_text = "Press any key to restart"
            restart_surface = score_font.render(restart_text, True, GREEN)
            restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
            screen.blit(restart_surface, restart_rect)

        # Draw the score texts
        draw_scores(score, hiscore)

        pygame.display.flip()
        clock.tick(60)

def main():
    start_game_loop()
    main_game_loop()
    game_over_loop()

main()