import random
import os
import pygame

# get the absolute path to the folder containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'Assets')

# helper function to load assets
def load_asset(filename):
    return pygame.image.load(os.path.join(ASSETS_DIR, filename)).convert_alpha()
import pygame
import random

# collision with hit probability
def check_collision(attacking_rect, target_rect, hit_chance=1.0):
    """Returns True if there's a hit based on rect overlap and probability."""
    if attacking_rect.colliderect(target_rect):
        return random.random() <= hit_chance
    return False

# adding text
def draw_text(text, size, x, y, color=(255, 0, 0)):
    font = pygame.font.SysFont("Arial", size, bold=True)
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)

# fighter class
class Fighter():
    def __init__(self, x, y, data, sprite_sheet, animation_steps, controls):
        self.size = data[0]
        self.scale = data[1]
        self.flip = False
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect(x, y, 80, 180)
        self.vel_y = 0
        self.jump = False
        self.health = 100
        self.controls = controls
        # combat features
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 30
        self.attack_cooldown_counter = 0
        self.blocking = False
        self.block_duration = 60  # half second block
        self.block_counter = 0
        self.block_cooldown = 240  # 2 seconds cooldown
        self.block_cooldown_counter = 0


#loading images & extracting from spritesheet 
  ## animations will be done if time allows, but this code sets up for potential animation
    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, frame_count in enumerate(animation_steps):
            temp_img_list = []
            for x in range(frame_count):
                # Skip frame 1 and 2 from idle animation (row 0)
                if y == 0 and x in [1, 2]:
                    continue
                temp_img = sprite_sheet.subsurface(
                    x * self.size, y * self.size, self.size, self.size)
                scaled_img = pygame.transform.scale(temp_img, (self.size * self.scale, self.size * self.scale))
                temp_img_list.append(scaled_img)

            animation_list.append(temp_img_list)
        return animation_list
    
   # control movement with key pressing. wasd for left fighter, arrows for right
    def move(self, screen_width, screen_height, surface, target):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0

        # reduce cooldown if active  
        if self.attack_cooldown_counter>0:
            self.attack_cooldown_counter-=1
        

        key = pygame.key.get_pressed()

        if self.block_cooldown_counter > 0:
            self.block_cooldown_counter -= 1

        if self.blocking:
            self.block_counter -= 1
            if self.block_counter <= 0:
                self.blocking = False
                self.block_cooldown_counter = self.block_cooldown
        else:
            if self.controls.get('block') and key[self.controls['block']] and self.block_cooldown_counter == 0:
                self.blocking = True
                self.block_counter = self.block_duration

        # can only perform other actions if not currently attacking or blocking
        # set animation actions
        if self.attacking:
            if self.attack_type == 1:
                self.set_action(4)  # attack 1 = row 5
            elif self.attack_type == 2:
                self.set_action(5)  # attack 2 = row 6
        elif self.jump:
            self.set_action(2)  # jump = row 2
        elif self.blocking:
            self.set_action(1)  # block = row 4 (or change as needed)
            
        elif dx != 0:
            self.set_action(1)  # run = row 1
        else:
            self.set_action(0)  # idle = row 0
        if not self.attacking and not self.blocking:
            #movement
            key = pygame.key.get_pressed()
            if key[self.controls['left']]:
                dx = -SPEED
            if key[self.controls['right']]:
                dx = SPEED
            if key[self.controls['jump']] and not self.jump:
                self.vel_y = -30
                self.jump = True
            #only attack if not attacking and cooldown is 0
            if key[self.controls['attack1']] and self.attack_cooldown_counter == 0:
                self.attack_type = 1
                self.attack(surface, target)
            elif key[self.controls['attack2']] and self.attack_cooldown_counter == 0:
                self.attack_type = 2
                self.attack(surface, target)
            #only block if not blocking and cooldown is 0
            
    
       # apply gravity 
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure player stay on screen
        # change with background
        if self.rect.left + dx < -80:
            dx = -self.rect.left - 80
        if self.rect.right + dx > screen_width - 135: 
            dx = screen_width - 135 - self.rect.right 
        if self.rect.bottom + dy > screen_height - 230:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 230 - self.rect.bottom
        
        # ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True
    
        # update fighter position
        self.rect.x += dx
        self.rect.y += dy

    # this is something we can vary between different characters if we give more than two options!
    def attack(self, surface, target):
        self.attacking = True
        attack_offset = -2 * self.rect.width if self.flip else 0
        attacking_rect = pygame.Rect(
            self.rect.centerx + attack_offset, self.rect.y,
            2 * self.rect.width, self.rect.height
        )

        # set different hit chances for each attack type
        hit_chance = 0.9 if self.attack_type == 1 else 0.6
        if check_collision(attacking_rect, target.rect, hit_chance=hit_chance):
            target.take_damage(10)

        pygame.draw.rect(surface, (0, 255, 0), attacking_rect)
        self.attack_cooldown_counter=self.attack_cooldown
       
    
    def take_damage(self, amount):
        if self.blocking:
            amount = 0  # no damage if blocking
        self.health -= amount
        if self.health < 0:
            self.health = 0
    def set_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update(self):
        ANIMATION_COOLDOWN = 100  # milliseconds per frame

        self.image = self.animation_list[self.action][self.frame_index]

        # advance frame if enough time has passed
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        # reset to idle after attack animation completes
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
                self.attack_type = 0
                self.set_action(0)
    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        
        # If blocking, apply a blue tint overlay
        if self.blocking:
        # Create a copy of the image and tint it blue
            blue_overlay = img.copy()
            blue_overlay.fill((0, 0, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(blue_overlay, (self.rect.x, self.rect.y))
        else:
            surface.blit(img, (self.rect.x, self.rect.y))


## ACTUAL GAME SET UP STARTS HERE

pygame.init()

# game window initialization
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cat Fighter")

# set frame rate
clock = pygame.time.Clock()
FPS = 120

# define colors
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# load assets (updated so that it works globally)
bg_image = load_asset('City_Street.png')
warrior_sheet = load_asset('cat_fighter_sprite1.png')
ranger_sheet = load_asset('cat_fighter_sprite2.png')


# define sprite sizes and animation steps
warrior_data = [50, 6]
ranger_data = [50, 6]
warrior_animation_steps = [8, 4, 1, 7, 7, 10, 10]  
ranger_animation_steps = [8, 8, 1, 8, 8, 10, 10]


# draw background
def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

# draw health bar
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 402, 32))   # outline
    pygame.draw.rect(screen, RED, (x, y, 400, 30))             # red background
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))  # yellow fill

# controls for each fighter
controls_left = {
    'left': pygame.K_a,
    'right': pygame.K_d,
    'jump': pygame.K_w,
    'attack1': pygame.K_1,
    'attack2': pygame.K_2,
    'block': pygame.K_s,
    }

controls_right = {
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'jump': pygame.K_UP,
    'attack1': pygame.K_PERIOD,
    'attack2': pygame.K_SLASH,
    'block': pygame.K_DOWN
    }

# create fighters
fighter_left = Fighter(200, 310, warrior_data, warrior_sheet, warrior_animation_steps, controls_left)
fighter_right = Fighter(500, 310, ranger_data, ranger_sheet, ranger_animation_steps, controls_right)

# game state
game_over = False
winner_text = ""

# main loop
run = True
while run:
    clock.tick(FPS)
    draw_bg()

    # draw health bars
    draw_health_bar(fighter_left.health, 20, 20)
    draw_health_bar(fighter_right.health, 580, 20)
     
    if not game_over:
        fighter_left.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_right)
        fighter_left.update()
        fighter_right.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_left)
        fighter_right.update()

    # check for KO
    if fighter_left.health <= 0:
        game_over = True
        winner_text = "Player 2 Wins!"
    elif fighter_right.health <= 0:
        game_over = True
        winner_text = "Player 1 Wins!"

    # draw fighters (always, even when KO'd)
    fighter_left.draw(screen)
    fighter_right.draw(screen)

    if game_over:
        draw_text(winner_text, 60, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text("Press Enter to Restart", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)

    # quit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                fighter_left.health=100
                fighter_right.health=100
                game_over=False
                winner_text=""

    pygame.display.update()

pygame.quit()