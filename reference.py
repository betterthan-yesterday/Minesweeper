"""
ROCKET DANCER
William Pol
Spaceship-flying game
"""
# Import all necessary modules
import pygame
from pygame.math import Vector2
import math
import random

# Initialize pygame and pygame.mixer (for sound)
pygame.init()
pygame.mixer.init()

# Set colours
BLACK = 0, 0, 0
WHITE = 255, 255, 255
GREEN = 0, 255, 0
RED = 255, 0, 0
YELLOW = 255, 255, 0

# Set clock
FPS = 60
clock = pygame.time.Clock()

# Set screen and caption
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rocket Dancer")

# Set background
background = pygame.image.load("spaceback.png")

# Load game graphics
rocket = pygame.image.load("rdship.png").convert_alpha()
pygame.display.set_icon(rocket)
rocket = pygame.transform.scale(rocket, (50, 50))
rocket = pygame.transform.rotate(rocket, -90)

stage0 = pygame.image.load("rdstage0.png").convert_alpha()
stage0 = pygame.transform.scale(stage0, (500, 500))

stage1 = pygame.image.load("rdstage1.png").convert_alpha()
stage1 = pygame.transform.scale(stage1, (1400, 450))

stage2 = pygame.image.load("rdstage2.png").convert_alpha()

stage3 = pygame.image.load("rdstage3.png").convert_alpha()

stage4 = pygame.image.load("rdstage4.png").convert_alpha()

# Load game sounds
game_music = pygame.mixer.Sound("rdmusicbyAlexanderNakarada.mp3")
game_music.set_volume(0.2)

# Game variables
stage_count = 0  # Designation for which stage the player is currently on
                 # to load in all necessary functions for that stage
fuel = 20  # Fuel variable for measuring fuel
ghost = 0  # Ghost variable for cheats
end = 0  # End variable to initiate end phase


# Define collisions
def collision(image1, image2):
    offset = image1.rect.x - image2.rect.x, image1.rect.y - image2.rect.y  # Offset is needed for the function
    # Mask collision
    if image2.mask.overlap(image1.mask, offset):
        return True
    else:
        return False


# Define function for what happens when the spaceship collides with something
def collision_reset(stage, count, fuel):
    # Spaceship collision with starting platform
    # If the spaceship collides with the starting platform, the stage just moves out of the way
    if collision(stage.start, rocket):
        stage.acceleration = 0
        stage.speed = Vector2(0, 0)
        stage.pos -= Vector2(1, 0)

    # Collision with the end platform
    # If the spaceship collides with the ending platform, the player advances to the next stage and fuel is added
    if collision(stage.end, rocket):
        count += 1
        fuel += 20
        return count, fuel

    # Collision with the stage
    # If the spaceship collides with the stage walls, the level reverts to the original state
    if collision(stage, rocket):
        stage.speed = Vector2(0, 0)
        stage.acceleration = 0
        stage.pos = Vector2(rocket.rect.left - 16.001, HEIGHT / 2 - stage.height / 2)
        rocket.angle = 0


# Draw text function
def draw_text(surface, text, size, x, y):
    # Set font
    font_name = pygame.font.match_font("lucidaconsole")
    font = pygame.font.Font(font_name, size)
    # Set specifications for text
    text_surface = font.render(text, True, (217, 217, 217))
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)  # Text will be blitted from the top left of its rectangle
    surface.blit(text_surface, text_rect)


# End screen function
def end_screen():
    # Receive hi-scores from a text file
    scores = open("rdscore.txt", "r")
    score_list = scores.readlines()
    # Remove line breaks
    score_list = list(map(lambda x: x.strip(), score_list))  # lamda is used here to strip every element in score_list
    scores.close()

    # Draw hi-scores onto the screen
    screen.fill(BLACK)
    draw_text(screen, "Hi-scores", 30, 100, 50)
    y = 85
    for x in range(5):
        draw_text(screen, score_list[x], 25, 100, y)
        y += 30


# Fade screen function
def fade():
    # Set specifications for the fade screen (black screen)
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BLACK)
    # Fading Loop
    for alpha in range(300):
        fade.set_alpha(alpha)  # With every iteration the screen gets darker and darker
        # Blit the screen that is being faded from
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        pygame.time.delay(3)


# Detect quadrant for black hole class
def quad(rocket_pos, hole_pos):
    if hole_pos[0] - rocket_pos[0] <= 0 and hole_pos[1] - rocket_pos[1] >= 0:
        return 1
    if hole_pos[0] - rocket_pos[0] >= 0 and hole_pos[1] - rocket_pos[1] >= 0:
        return 2
    if hole_pos[0] - rocket_pos[0] >= 0 and hole_pos[1] - rocket_pos[1] <= 0:
        return 3
    if hole_pos[0] - rocket_pos[0] <= 0 and hole_pos[1] - rocket_pos[1] <= 0:
        return 4


# Stage movement function; in this game, it is the stage that moves, not the spaceship
def stage_movement(stage):
    # Trigonometry is used to calculate the direction the stage will move in
    pos_change = stage.acceleration * math.cos(math.radians(rocket.angle)), \
                 stage.acceleration * math.sin(math.radians(rocket.angle))
    stage.speed -= pos_change  # pos_change does not directly change the position of the stage, but instead changes the
                               # speed of which it moves (can be negative) which later alters the position of the stage


# Start screen draw function
def start_screen():
    # Credits
    screen.fill(BLACK)
    draw_text(screen, "Heavily Inspired by Rocket Dancer", 30, 100, 100)
    draw_text(screen, "by Bartłomiej Łakuta", 30, 205, 200)
    draw_text(screen, " Music by Alexander Nakarada", 30, 135, HEIGHT-200)


# Define strafe function; this is used in the class functions to update the rect
def strafe(pos, speed, rect):
    # Velocity of stage changes the position
    pos.x += speed.x
    pos.y -= speed.y
    rect.topleft = pos.x, pos.y  # Rect is updated to new position


# Define spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()  # Call the Sprite constructor/initializer
        self.orig_image = image  # orig_image is needed for proper rotation
        self.image = image  # Define self.image
        self.rect = self.image.get_rect(center=(x, y))  # Define self.rect
        self.angle = 0  # Set angle
        self.mask = pygame.mask.from_surface(self.image)  # Get mask for collision

    def update(self):
        # Rotate the orig image and update rect and mask
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)


# Induct our rocket image into the Rocket class
rocket = Spaceship(400, 300, rocket)


# Define start platform class
class StartPlatform(pygame.sprite.Sprite):
    def __init__(self, stage, offset):
        super().__init__()
        # The start platform is only a green rectangle
        self.image = pygame.Surface((8.5, 100))
        self.image.fill(GREEN)
        self.stage = stage  # Get the stage that it will be used on
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.offset = offset  # Offset is used for specific placement

    def update(self):
        # Placement of platform
        self.rect.midleft = self.stage.rect.left + self.offset, self.stage.rect.midleft[1]


# Define end platform class
class EndPlatform(pygame.sprite.Sprite):
    def __init__(self, stage, offset):
        super().__init__()
        # End platform is a red rectangle
        self.image = pygame.Surface((8.5, 100))
        self.image.fill(RED)
        self.stage = stage
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.offset = offset

    def update(self):
        # Placement of platform
        self.rect.midright = self.stage.rect.right - self.offset, self.stage.rect.midright[1]


# Define stage/maze class as a sprite
class Stages(pygame.sprite.Sprite):
    def __init__(self, image, height, s_offset, e_offset):
        super().__init__()
        self.image = image
        self.height = height  # Height is needed so that the stage is blit in the middle of the screen when starting
        self.speed = Vector2(0, 0)  # Speed variable as a vector; Vector2 allows for operations with tuples
        self.acceleration = 0  # Acceleration variable
        self.rect = self.image.get_rect()
        self.pos = Vector2(rocket.rect.left - 16.001, HEIGHT / 2 - self.height / 2)  # Position of stage as vector
        self.mask = pygame.mask.from_surface(self.image)
        # Get start and end platforms and offset them if needed
        self.start = StartPlatform(self, s_offset)
        self.end = EndPlatform(self, e_offset)

    def update(self):
        # Update rect; rect is all that is needed for the blitting of sprites
        strafe(self.pos, self.speed, self.rect)


# Induct levels into the Stages class
stage0 = Stages(stage0, stage0.get_height(), 8.5, 7)
stage1 = Stages(stage1, stage1.get_height(), 14, 14)
stage2 = Stages(stage2, stage2.get_height(), 14, 16)
stage3 = Stages(stage3, stage3.get_height(), 15, 15)
stage4 = Stages(stage4, stage4.get_height(), 8.5, 7)
stages = [stage0, stage1, stage2, stage3, stage4]


# Define Mob class; just for asteroids
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load and transform image
        self.image = pygame.image.load("rdasteroid.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        # Define horizontal and vertical (mostly diagonal) speed
        self.speedx = random.randrange(-2, 2)
        self.speedy = random.randrange(4, 6)
        self.x = random.randrange(200, 1800)

    def update(self):
        # Placement and movement
        self.rect.y += self.speedy + -stage3.speed[1]  # Vertical movement;
                                                       # the stage speed is added to make the movement constant
        # Horizontal movement in relation to the stage position
        self.rect.left = stage3.rect.left + self.x
        self.x += self.speedx

        # Reset when asteroid is past the screen
        if self.rect.top > HEIGHT + 10:
            self.rect.bottom = 0
            self.speedx = random.randrange(-2, 2)
            self.speedy = random.randrange(4, 6)
            self.x = random.randrange(200, 1800)


# Create Mobs
mobs = [Mob() for x in range(10)]


# Define black hole class
class BlackHole(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        # Black hole surface is a yellow rectangle but it is covered by a black circle
        self.image = pygame.Surface((50, 50))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x  # x position in relation to the stage

    def update(self):
        # Placement in relation to the stage
        self.rect.center = stage4.rect.left + self.x, stage4.rect.top + stage4.height/2


# Create black holes
bh1 = BlackHole(600)
bh2 = BlackHole(1800)
blackholes = [bh1, bh2]


# Fire class for animation
class Fire(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load and transform image
        self.image = pygame.image.load("rdfireanime.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (12, 20))
        self.image = pygame.transform.rotate(self.image, 90)
        self.orig_image = self.image  # orig_image for rotation
        self.rect = self.image.get_rect()

    def update(self):
        # Fire animation
        # No animation actually occurs, the Fire sprite just moves out from behind the rocket the larger the
        # acceleration variable
        fire_animation = -10 - stages[stage_count].acceleration*80
        # Limit for how far the sprite will come out
        if -10 - stages[stage_count].acceleration*80 < -30:
            fire_animation = -30

        self.image = pygame.transform.rotate(self.orig_image, rocket.angle)  # Rotate the image to be in-line with the
                                                                             # rocket
        rotate_offset = Vector2(fire_animation, 1.5).rotate(-rocket.angle)  # Rotate the offset vector
        self.rect = self.image.get_rect(center=Vector2(400, 300) + rotate_offset)  # Update the rect with the offset
        # vector, the offset is used to move the sprite into the desired place


# Create fire
fire = Fire()

# Designate groups for sprites and add sprites to them
all_sprites = pygame.sprite.Group()
all_sprites.add(fire, rocket, stage0, stage0.start, stage0.end)

mobs_group = pygame.sprite.Group()
for mob in mobs:
    mobs_group.add(mob)

blackhole_group = pygame.sprite.Group()
for holes in blackholes:
    blackhole_group.add(holes)


# Game Loop
def main():
    global stage_count, fuel, ghost, end
    running = True
    while running:
        game_music.play()  # Play music
        clock.tick(FPS)  # FPS

        # Time for score
        ticks = pygame.time.get_ticks()

        # Keystrokes
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    stages[stage_count].acceleration = 0  # Acceleration is reset if any key is released; simulates inertia

                if event.key == pygame.K_ESCAPE:
                    running = False

            # Keystrokes from here are for cheats
                if event.key == pygame.K_BACKSPACE:
                    stage_count += 1
                    for c in stages:
                        c.kill()
                        c.start.kill()
                        c.end.kill()
                    all_sprites.add(stages[stage_count], stages[stage_count].start, stages[stage_count].end)

                if event.key == pygame.K_a:
                    ghost = 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    ghost = 1
                    fuel = 100

        # In the first 5 seconds of the game, display the start screen
        if ticks < 5000:
            start_screen()

        else:
            # Check to see if game has ended, if not:
            if end == 0:
                # Update all sprites' variables
                all_sprites.update()

                # Draw background
                screen.blit(background, (0, 0))

                # Rocket rotation
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    rocket.angle += 4.5
                if keys[pygame.K_RIGHT]:
                    rocket.angle -= 4.5
                # "Rocket" acceleration
                if keys[pygame.K_UP]:
                    if fuel > 0:
                        stages[stage_count].acceleration += 0.0025

                # Stage movement
                stage_movement(stages[stage_count])

                # Draw all sprites
                all_sprites.draw(screen)

                # Fuel Meter
                fuel -= stages[stage_count].acceleration
                if fuel > 0:
                    fuel_meter = pygame.Surface(((float(fuel)*2), 20))
                    fuel_meter.fill(YELLOW)
                    screen.blit(fuel_meter, (30, HEIGHT-50))

                # Stage specific functions
                # Stage 0 is just the practice stage for introducing the player to the game
                if stage_count == 0:
                    # Draw text
                    draw_text(screen, "Use the arrow keys to move around", 13, *(stage0.rect.midleft + Vector2(70, -175)))
                    draw_text(screen, "Avoid hitting the side walls", 13, *(stage0.rect.midleft + Vector2(70, -87.5)))
                    draw_text(screen, "Hit the red platform to proceed to the next level", 13,
                              *(stage0.rect.midleft + Vector2(70, 0)))
                    draw_text(screen, "Beat the game in the fastest time possible", 13,
                              *(stage0.rect.midleft + Vector2(70, 87.5)))
                    draw_text(screen, "Watch out for fuel; excess is carried over", 13,
                              *(stage0.rect.midleft + Vector2(70, 175)))

                    # Time starts after player finishes the practice level
                    start_time = ticks

                # Count time after the practice level
                if stage_count != 0:
                    # Score
                    score = (ticks - start_time - stage_count*1500)/1000
                    draw_text(screen, str("{:.1f}".format(score)) + "s", 20, 700, 20)

                # Asteroid movement for stage 3
                if stage_count == 3:
                    mobs_group.update()
                    mobs_group.draw(screen)

                    for m in mobs:
                        if ghost == 0:
                            # Check for collision and if yes, reset
                            if collision(m, rocket):
                                stage3.speed = Vector2(0, 0)
                                stage3.acceleration = 0
                                stage3.pos = Vector2(rocket.rect.left + 15, HEIGHT / 2 - stage3.height / 2)
                                rocket.angle = 0

                # Black hole mechanism for stage 4
                if stage_count == 4:
                    blackhole_group.update()
                    blackhole_group.draw(screen)
                    # Draw circle over the yellow rectangles
                    pygame.draw.circle(screen, BLACK, bh1.rect.center, 36)
                    pygame.draw.circle(screen, BLACK, bh2.rect.center, 36)

                    for bholes in blackholes:
                        # Gravity function
                        dist = math.hypot(400-bholes.rect.center[0], 300-bholes.rect.center[1])
                        # Initiate gravity only when spaceship is in range
                        if dist <= 300:
                            # Find the angle of which to move the stage to simulate gravity
                            # The quadrant is needed because of the ambiguity in using trigonometry
                            quadrant = quad((400, 300), bholes.rect.center)
                            angle = math.asin((bholes.rect.center[1]-300)/dist)
                            angle = math.degrees(angle)
                            # Find the actual angle in degrees
                            if quadrant == 1:
                                pass
                            if quadrant == 2 or quadrant == 3:
                                angle = -angle+180
                            if quadrant == 4:
                                angle = angle+360
                            # Change the stage speed so that it simulates gravity
                            pos_change = 0.04**(dist/400) * math.cos(math.radians(-angle)), \
                                         0.04**(dist/400) * math.sin(math.radians(angle))
                            stage4.speed += pos_change

                        if ghost == 0:
                            # Check for collision, if so, reset
                            if collision(bholes, rocket):
                                stage4.speed = Vector2(0, 0)
                                stage4.acceleration = 0
                                stage4.pos = Vector2(rocket.rect.left + 15, HEIGHT / 2 - stage4.height / 2)
                                rocket.angle = 0

                # Check for collision with stage walls, start platform, and end platform
                if ghost == 0:
                    collision_reset(stages[stage_count], stage_count, fuel)  # Reset stage variables
                    if collision_reset(stages[stage_count], stage_count, fuel) is not None:  # The only time that
                        # collision_reset does not return None is when hitting the end platform
                        fade()  # Fade screen to new level
                        stage_count, fuel = collision_reset(stages[stage_count], stage_count, fuel)  # Update
                        # stage_count and fuel and reset stage variables
                        rocket.angle = 0  # Reset rocket angle

                        # Exit parameter
                        if stage_count+1 > len(stages):
                            end = 1  # Acknowledge that the game has ended

                            # Read and record scores from file
                            score_file = open("rdscore.txt", "r")
                            scores = score_file.readlines()
                            score_file.close()
                            scores = [float(x) for x in scores]

                            # Write new score if conditions are met
                            score_file = open("rdscore.txt", "w")
                            if score < float(scores[-1]):
                                # If the current score is smaller than the largest score in scores, replace it
                                scores.pop()
                                scores.append(float("{:.1f}".format(score)))
                                # Then the list sorts
                                scores.sort()

                            for x in scores:
                                # Update hi-score file
                                line = str(x) + "\n"
                                score_file.writelines(line)
                            score_file.close()

                        # This will run if there is no "if end == 0:" and break because of the Out of Index error
                        if end == 0:
                            # Clear sprite group of completed stage and add next stage to group
                            for c in stages:
                                c.kill()
                                c.start.kill()
                                c.end.kill()
                            all_sprites.add(stages[stage_count], stages[stage_count].start, stages[stage_count].end)

            else:
                # Blit end screen when the game is done
                end_screen()

        pygame.display.flip()


if __name__ == '__main__':
    main()
