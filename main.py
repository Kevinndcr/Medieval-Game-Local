import pygame
import sys
import math
import random
from assets.background import ColiseumBackground
from assets.sound_manager import SoundManager
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('assets/background-music.wav')
pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely

# Create sound manager
sound_manager = SoundManager()

# Set up game window
info = pygame.display.Info()
width, height = info.current_w, info.current_h
screen = pygame.display.set_mode((width, height), pygame.NOFRAME)  # Removes the window border
pygame.display.set_caption("Medieval Fighting Game")

# Create background
background = ColiseumBackground(width, height)

# Load sounds (you'll need to add your own sound files)
sound_files = {
    'hit': 'assets/hit.wav',
    'swing': 'assets/swing.wav',
    'victory': 'assets/victory.wav',
    'music': 'assets/background-music.wav',
    'shield-block': 'assets/shield-block.wav',
    'sword-clash': 'assets/sword-clash.wav'
}

# Try to load default sounds, but continue if files don't exist
print("Loading sound files...")
for name, path in sound_files.items():
    print(f"Attempting to load {name} from {path}")
    if os.path.exists(path):
        print(f"Found {path}")
        try:
            if name == 'music':
                if sound_manager.load_music(path):
                    print("Successfully loaded music")
                    sound_manager.play_music(loop=True)
                else:
                    print("Failed to load music")
            else:
                if sound_manager.load_sound(name, path):
                    print(f"Successfully loaded {name} sound")
                else:
                    print(f"Failed to load {name} sound")
        except Exception as e:
            print(f"Error loading {name}: {str(e)}")
    else:
        print(f"File not found: {path}")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BLUE = (135, 206, 235)
DARK_BLUE = (100, 149, 237)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Add these to your global variables/constants at the top
CLASH_BATTLE_DURATION = 360  # 6 seconds at 60 FPS
CLASH_BATTLE_BAR_WIDTH = 300
CLASH_BATTLE_BAR_HEIGHT = 30
CLASH_DAMAGE = 100
CLASHES_NEEDED = 10

class SwingEffect:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.lifetime = 10
        self.size = 40
        self.color = YELLOW

    def update(self):
        self.lifetime -= 1
        self.size -= 2
        return self.lifetime > 0

    def draw(self, screen):
        alpha = int((self.lifetime / 10) * 255)
        effect_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.arc(effect_surface, (*self.color, alpha),
                       (0, 0, self.size * 2, self.size * 2),
                       math.radians(self.angle - 30), math.radians(self.angle + 30), 4)
        screen.blit(effect_surface, (self.x - self.size, self.y - self.size))

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        
    def draw(self, screen):
        color = (min(self.color[0] + 20, 255), 
                min(self.color[1] + 20, 255), 
                min(self.color[2] + 20, 255)) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Draw text
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:
                return True
        return False

class DamageEffect:
    def __init__(self, x, y, amount):
        self.x = x
        self.y = y
        self.amount = amount
        self.lifetime = 30
        self.velocity_y = -3
        self.font = pygame.font.Font(None, 36)
        # Red color for damage
        self.color = (180, 0, 0)
        
    def update(self):
        self.y += self.velocity_y
        self.lifetime -= 1
        return self.lifetime > 0
        
    def draw(self, screen):
        alpha = min(255, self.lifetime * 8)
        text = self.font.render(str(self.amount), True, self.color)
        text.set_alpha(alpha)
        screen.blit(text, (self.x - text.get_width()//2, self.y))

class HitEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 20
        self.particles = []
        # Create spark particles
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': random.uniform(2, 4)
            })
    
    def update(self):
        self.lifetime -= 1
        # Update particle positions
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            # Add gravity effect
            p['dy'] += 0.2
        return self.lifetime > 0
    
    def draw(self, screen):
        # Draw flash
        flash_alpha = int((self.lifetime / 20) * 128)
        flash_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(flash_surface, (255, 255, 200, flash_alpha), (20, 20), 20)
        screen.blit(flash_surface, (self.x - 20, self.y - 20))
        
        # Draw sparks
        spark_alpha = int((self.lifetime / 20) * 255)
        for p in self.particles:
            spark_surface = pygame.Surface((int(p['size'] * 2), int(p['size'] * 2)), pygame.SRCALPHA)
            # Golden sparks
            pygame.draw.circle(spark_surface, (255, 215, 0, spark_alpha), 
                             (p['size'], p['size']), p['size'])
            screen.blit(spark_surface, (p['x'] - p['size'], p['y'] - p['size']))

class BloodEffect:
    def __init__(self, x, y, direction=None):
        self.x = x
        self.y = y
        self.lifetime = 60  # Longer lifetime for blood
        self.particles = []
        # Create blood particles
        num_particles = random.randint(8, 12)
        for _ in range(num_particles):
            if direction is None:
                angle = random.uniform(0, 2 * math.pi)
            else:
                # Spray in the direction of the hit with some spread
                base_angle = math.radians(direction)
                angle = base_angle + random.uniform(-math.pi/3, math.pi/3)
            
            speed = random.uniform(3, 7)
            size = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'original_size': size,  # Store original size for scaling
                'splat': False,  # Whether particle has hit the ground
                'splat_size': size * random.uniform(1.5, 2.5)  # Size after hitting ground
            })
    
    def update(self):
        self.lifetime -= 1
        # Update particle positions
        for p in self.particles:
            if not p['splat']:
                p['x'] += p['dx']
                p['y'] += p['dy']
                p['dy'] += 0.3  # Gravity
                
                # Check if particle hit the ground (you can adjust this height)
                if p['y'] > height - 50:  # Ground level
                    p['splat'] = True
                    p['y'] = height - 50
                    p['size'] = p['splat_size']
                    p['dx'] *= 0.5  # Slow down horizontal movement
            else:
                # Splattered particles still move a bit horizontally
                p['x'] += p['dx']
                p['dx'] *= 0.95  # Friction
        
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = min(255, self.lifetime * 4)
        for p in self.particles:
            particle_surface = pygame.Surface((int(p['size'] * 2), int(p['size'] * 2)), pygame.SRCALPHA)
            
            if p['splat']:
                # Draw elongated splat
                color = (140, 0, 0, alpha)  # Darker red for splats
                height = p['size'] * 0.6
                pygame.draw.ellipse(particle_surface, color,
                                  (0, p['size'] - height/2,
                                   p['size'] * 2, height))
            else:
                # Draw round drop
                color = (180, 0, 0, alpha)  # Brighter red for drops
                pygame.draw.circle(particle_surface, color,
                                 (p['size'], p['size']), p['size'])
            
            screen.blit(particle_surface, 
                       (p['x'] - p['size'], p['y'] - p['size']))

class Player:
    def __init__(self, x, y, color=DARK_BLUE, body_color=BLUE):
        self.x = x
        self.y = y
        self.size = 20
        self.speed = 5
        self.color = color
        self.body_color = body_color
        self.direction = 0  # Angle in degrees
        self.health = 500
        self.is_dead = False
        self.hit_cooldown = 0
        self.hit_cooldown_duration = 20
        self.damage_numbers = []
        self.swing_effects = []
        self.hit_effects = []  # Add hit effects list
        self.blood_effects = []  # Add blood effects list
        
        # Sword parameters
        self.sword_length = 40
        self.sword_width = 8
        self.handle_length = 15
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_duration = 20
        self.attack_cooldown = 0
        self.attack_cooldown_duration = 30
        
        # Medieval warrior details
        self.helmet_size = self.size * 0.8
        self.armor_plates = 4
        self.shield_size = self.size * 1.2
        
        # Animation
        self.walking_cycle = 0
        self.body_wobble = 0
        
        # Effects
        self.swing_effects = []
        self.damage_effects = []
        self.base_sword_angle = 45  # Initial sword angle
        self.sword_angle = self.base_sword_angle  # Current sword angle
        
        # Guarding
        self.is_guarding = False
        self.guard_cooldown = 0
        self.guard_cooldown_duration = 30
        self.knockback_dx = 0  # For sword clash knockback
        self.knockback_dy = 0
        
        # Clash battle
        self.clash_count = 0
        self.clash_power = 0  # For the clash battle minigame
        
    def draw(self, screen):
        # Get view angle
        is_side_view = 135 <= self.direction <= 225 or (self.direction >= 315 or self.direction <= 45)
        facing_left = 135 <= self.direction <= 225
        
        # Base measurements
        helmet_size = self.size * 0.8
        body_length = self.size * 1.4
        shoulder_width = self.size * 1.4
        
        # Calculate positions
        body_y = self.y
        
        # Draw shield (if not attacking)
        if not self.is_attacking and is_side_view:
            shield_x = self.x + (-20 if facing_left else 20)
            pygame.draw.circle(screen, self.body_color, (int(shield_x), int(body_y)), 
                             int(self.shield_size))
            pygame.draw.circle(screen, self.color, (int(shield_x), int(body_y)), 
                             int(self.shield_size - 4))
        
        # Draw body
        if is_side_view:
            # Side view body
            body_width = shoulder_width * 0.8
            body_x = self.x + (body_width * 0.2 if facing_left else -body_width * 0.2)
            
            # Draw armor plates
            for i in range(self.armor_plates):
                plate_y = body_y - body_length/2 + (body_length * i / self.armor_plates)
                pygame.draw.rect(screen, self.color,
                               (body_x - body_width/2, plate_y,
                                body_width, body_length/self.armor_plates))
        else:
            # Front/back view body
            pygame.draw.rect(screen, self.color,
                           (self.x - shoulder_width/2, body_y - body_length/2,
                            shoulder_width, body_length))
        
        # Draw sword
        if self.is_attacking:
            # Calculate sword angle for attack
            swing_progress = self.attack_frame / self.attack_duration
            swing_range = 180  # Full swing range
            
            # Adjust swing for view
            if is_side_view:
                base_angle = -90 if facing_left else 90
            else:
                base_angle = self.direction
            
            # Use easing function for smoother swing
            swing_offset = swing_range * (1 - (1 - swing_progress) ** 2)
            sword_angle = math.radians(base_angle - swing_offset)
            
            # Draw sword with handle
            handle_x = self.x + math.cos(sword_angle) * self.handle_length
            handle_y = self.y + math.sin(sword_angle) * self.handle_length
            
            blade_x = handle_x + math.cos(sword_angle) * self.sword_length
            blade_y = handle_y + math.sin(sword_angle) * self.sword_length
            
            # Draw handle
            pygame.draw.line(screen, (139, 69, 19), 
                           (self.x, self.y), (handle_x, handle_y), 6)
            
            # Draw blade
            pygame.draw.line(screen, (192, 192, 192), 
                           (handle_x, handle_y), (blade_x, blade_y), self.sword_width)
            
            # Add swing trail
            if len(self.swing_effects) < 5:
                self.swing_effects.append({
                    'x': blade_x,
                    'y': blade_y,
                    'alpha': 255,
                    'width': self.sword_width
                })
        else:
            # Draw sword in rest position
            if is_side_view:
                sword_angle = math.radians(-45 if facing_left else 45)
            else:
                sword_angle = math.radians(self.direction + 45)
            
            handle_x = self.x + math.cos(sword_angle) * self.handle_length
            handle_y = self.y + math.sin(sword_angle) * self.handle_length
            
            blade_x = handle_x + math.cos(sword_angle) * self.sword_length
            blade_y = handle_y + math.sin(sword_angle) * self.sword_length
            
            pygame.draw.line(screen, (139, 69, 19), 
                           (self.x, self.y), (handle_x, handle_y), 6)
            pygame.draw.line(screen, (192, 192, 192), 
                           (handle_x, handle_y), (blade_x, blade_y), self.sword_width)
        
        # Draw guard symbol when guarding
        if self.is_guarding:
            shield_radius = 15
            shield_y = self.y - self.size - 30  # Position above player
            # Draw shield circle
            pygame.draw.circle(screen, (192, 192, 192), (int(self.x), int(shield_y)), shield_radius)
            # Draw shield cross
            pygame.draw.line(screen, (128, 128, 128), 
                           (self.x - shield_radius, shield_y),
                           (self.x + shield_radius, shield_y), 3)
            pygame.draw.line(screen, (128, 128, 128),
                           (self.x, shield_y - shield_radius),
                           (self.x, shield_y + shield_radius), 3)
        
        # Draw helmet
        helmet_y = body_y - body_length/2 - helmet_size * 0.6
        if is_side_view:
            # Side view helmet
            helmet_x = self.x + (helmet_size * 0.2 if facing_left else -helmet_size * 0.2)
            
            # Draw helmet shape
            pygame.draw.ellipse(screen, self.color,
                              (helmet_x - helmet_size/2, helmet_y - helmet_size/2,
                               helmet_size, helmet_size))
            
            # Draw helmet details (visor)
            visor_y = helmet_y - helmet_size * 0.1
            pygame.draw.line(screen, self.body_color,
                           (helmet_x - helmet_size/3, visor_y),
                           (helmet_x + helmet_size/3, visor_y), 3)
        else:
            # Front view helmet
            pygame.draw.circle(screen, self.color,
                             (int(self.x), int(helmet_y)), int(helmet_size))
            # Draw helmet details
            visor_y = helmet_y - helmet_size * 0.1
            pygame.draw.line(screen, self.body_color,
                           (self.x - helmet_size/2, visor_y),
                           (self.x + helmet_size/2, visor_y), 3)
        
        # Draw swing effects
        effect_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for effect in self.swing_effects:
            pygame.draw.circle(effect_surface, (*self.color, effect['alpha']),
                             (int(effect['x']), int(effect['y'])), 5)
        screen.blit(effect_surface, (0, 0))
        
        # Draw hit effects
        for effect in self.hit_effects:
            effect.draw(screen)
        
        # Draw blood effects
        for effect in self.blood_effects:
            effect.draw(screen)
        
        # Clean up old effects
        self.swing_effects = [e for e in self.swing_effects if e['alpha'] > 0]

    def draw_health_bar(self, screen, x, y):
        # Health bar dimensions
        bar_width = 200  # Made wider
        bar_height = 25  # Made taller
        border_width = 4
        
        # Calculate health percentage
        health_percent = self.health / 500
        health_width = bar_width * health_percent
        
        # Colors
        border_color = (101, 67, 33)  # Dark brown
        bg_color = (80, 0, 0)  # Dark red
        health_colors = [
            (200, 0, 0),    # Red (low health)
            (200, 150, 0),  # Orange (medium health)
            (0, 200, 0)     # Green (high health)
        ]
        
        # Determine health bar color based on percentage
        if health_percent > 0.6:
            health_color = health_colors[2]  # Green
        elif health_percent > 0.3:
            health_color = health_colors[1]  # Orange
        else:
            health_color = health_colors[0]  # Red
        
        # Draw decorative outer border
        pygame.draw.rect(screen, border_color, 
                        (x - border_width - 2, y - border_width - 2,
                         bar_width + (border_width * 2) + 4, 
                         bar_height + (border_width * 2) + 4))
        
        # Draw inner black border
        pygame.draw.rect(screen, (0, 0, 0),
                        (x - border_width, y - border_width,
                         bar_width + (border_width * 2),
                         bar_height + (border_width * 2)))
        
        # Draw background
        pygame.draw.rect(screen, bg_color, (x, y, bar_width, bar_height))
        
        # Draw health
        if health_width > 0:
            pygame.draw.rect(screen, health_color, (x, y, health_width, bar_height))
            
            # Add shine effect
            shine_height = bar_height // 3
            shine_alpha = 128
            shine_surface = pygame.Surface((int(health_width), shine_height), pygame.SRCALPHA)
            pygame.draw.rect(shine_surface, (*health_color, shine_alpha), 
                           (0, 0, int(health_width), shine_height))
            screen.blit(shine_surface, (x, y))
        
        # Draw segments
        num_segments = 10
        segment_width = bar_width / num_segments
        for i in range(1, num_segments):
            seg_x = x + (i * segment_width)
            pygame.draw.line(screen, border_color, 
                           (seg_x, y), (seg_x, y + bar_height), 2)
        
        # Draw health text
        font = pygame.font.Font(None, 28)
        health_text = f"{int(self.health)}/500"
        text_surface = font.render(health_text, True, (255, 255, 255))
        text_x = x + (bar_width - text_surface.get_width()) // 2
        text_y = y + (bar_height - text_surface.get_height()) // 2
        
        # Draw text shadow
        shadow_surface = font.render(health_text, True, (0, 0, 0))
        screen.blit(shadow_surface, (text_x + 2, text_y + 2))
        screen.blit(text_surface, (text_x, text_y))

    def update(self):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        if self.guard_cooldown > 0:
            self.guard_cooldown -= 1
            
        # Apply knockback
        if abs(self.knockback_dx) > 0.1 or abs(self.knockback_dy) > 0.1:
            self.x += self.knockback_dx
            self.y += self.knockback_dy
            # Dampen knockback
            self.knockback_dx *= 0.8
            self.knockback_dy *= 0.8
        
        # Update attack animation
        if self.is_attacking:
            self.attack_frame += 1
            # Make the sword swing faster and more responsive
            swing_speed = 15  # Increased swing speed
            
            # Calculate sword angle based on attack frame
            progress = self.attack_frame / self.attack_duration
            if progress <= 0.5:
                # Wind up
                self.sword_angle = self.base_sword_angle - (90 * progress * 2)
            else:
                # Swing through
                self.sword_angle = self.base_sword_angle - 90 + (180 * (progress - 0.5) * 2)
            
            # Add trail effect during the swing
            if 0.2 <= progress <= 0.8:
                sword_tip_x = self.x + math.cos(math.radians(self.sword_angle)) * self.sword_length
                sword_tip_y = self.y + math.sin(math.radians(self.sword_angle)) * self.sword_length
                self.swing_effects.append({
                    'x': sword_tip_x,
                    'y': sword_tip_y,
                    'alpha': 200
                })
            
            if self.attack_frame >= self.attack_duration:
                self.is_attacking = False
                self.attack_frame = 0
                self.sword_angle = self.base_sword_angle
        
        # Update damage numbers
        self.damage_numbers = [d for d in self.damage_numbers if d.update()]
        
        # Update swing effects
        for effect in self.swing_effects:
            effect['alpha'] = max(0, effect['alpha'] - 25)  # Faster fade
        
        # Update hit effects
        self.hit_effects = [effect for effect in self.hit_effects if effect.update()]
        
        # Update blood effects
        self.blood_effects = [effect for effect in self.blood_effects if effect.update()]
        
        # Clean up old effects
        self.swing_effects = [e for e in self.swing_effects if e['alpha'] > 0]

    def move(self, controls, attack_key=pygame.K_SPACE):
        dx = 0
        dy = 0
        
        # Movement controls
        if controls[pygame.K_w]:
            dy -= self.speed
            self.direction = 270
        if controls[pygame.K_s]:
            dy += self.speed
            self.direction = 90
        if controls[pygame.K_a]:
            dx -= self.speed
            self.direction = 180
        if controls[pygame.K_d]:
            dx += self.speed
            self.direction = 0

        # Attack handling
        if controls[attack_key] and not self.is_attacking and self.attack_cooldown == 0:
            self.is_attacking = True
            self.attack_frame = 0
            sound_manager.play_sound('swing')

        # Diagonal movement
        if dx != 0 and dy != 0:
            if dx > 0 and dy < 0:  # Up-right
                self.direction = 315
            elif dx > 0 and dy > 0:  # Down-right
                self.direction = 45
            elif dx < 0 and dy > 0:  # Down-left
                self.direction = 135
            elif dx < 0 and dy < 0:  # Up-left
                self.direction = 225

        # Normalize diagonal movement speed
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/sqrt(2)
            dy *= 0.707

        # Update base sword angle to match player direction
        self.base_sword_angle = self.direction

        # Update position with boundary checking
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 0 + self.size < new_x < width - self.size:
            self.x = new_x
        if 0 + self.size < new_y < height - self.size:
            self.y = new_y

    def take_damage(self, amount, hit_angle=None):
        """Take damage and create effects"""
        if self.hit_cooldown <= 0:
            if self.is_guarding:
                # Successful block
                sound_manager.play_sound('shield-block')
                # Minimal knockback when blocking
                if hit_angle is not None:
                    self.knockback_dx = math.cos(math.radians(hit_angle)) * 2
                    self.knockback_dy = math.sin(math.radians(hit_angle)) * 2
            else:
                self.health = max(0, self.health - amount)
                self.hit_cooldown = self.hit_cooldown_duration
                
                # Create multiple smaller damage numbers
                num_effects = 3
                spread = 20
                for i in range(num_effects):
                    offset_x = (i - num_effects//2) * spread
                    offset_y = random.randint(-10, 10)
                    self.damage_numbers.append(DamageEffect(
                        self.x + offset_x, 
                        self.y + offset_y, 
                        amount//num_effects))
                
                # Add hit effect
                self.hit_effects.append(HitEffect(self.x, self.y))
                
                # Add blood effect with direction
                self.blood_effects.append(BloodEffect(self.x, self.y, hit_angle))
                
                if self.health <= 0:
                    self.is_dead = True

    def check_hit(self, other_player):
        if self.is_attacking and self.attack_frame == self.attack_duration // 2:
            # Calculate sword tip position based on player's direction
            attack_angle = math.radians(self.direction)
            if self.attack_frame <= self.attack_duration // 2:
                # During wind-up and strike
                swing_progress = self.attack_frame / (self.attack_duration // 2)
                attack_angle = math.radians(self.direction - 45 + swing_progress * 90)
            
            sword_tip_x = self.x + math.cos(attack_angle) * (self.size * 1.1 + self.sword_length)
            sword_tip_y = self.y + math.sin(attack_angle) * (self.size * 1.1 + self.sword_length)
            
            # Create a larger hitbox area around the sword
            hitbox_size = 40
            
            # Calculate distance from sword tip to opponent's center
            dx = other_player.x - sword_tip_x
            dy = other_player.y - sword_tip_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # If opponent is within hitbox range
            if distance < hitbox_size + other_player.size/2:
                hit_angle = math.degrees(math.atan2(dy, dx))
                
                # Check for sword clash
                if other_player.is_attacking and other_player.attack_frame > 0:
                    # Sword clash occurred!
                    sound_manager.play_sound('sword-clash')
                    self.clash_count += 1
                    other_player.clash_count += 1
                    
                    # Check if this is the tenth clash
                    if self.clash_count >= CLASHES_NEEDED and other_player.clash_count >= CLASHES_NEEDED:
                        return ClashBattle(self, other_player, 
                                        pygame.display.get_surface().get_width(),
                                        pygame.display.get_surface().get_height())
                        
                    # Strong knockback for both players
                    knockback_force = 10
                    self.knockback_dx = -math.cos(math.radians(hit_angle)) * knockback_force
                    self.knockback_dy = -math.sin(math.radians(hit_angle)) * knockback_force
                    other_player.knockback_dx = math.cos(math.radians(hit_angle)) * knockback_force
                    other_player.knockback_dy = math.sin(math.radians(hit_angle)) * knockback_force
                else:
                    # Normal hit
                    other_player.take_damage(20, hit_angle)
                    sound_manager.play_sound('hit')
                
                # Add swing effect at the hit location
                hit_x = (sword_tip_x + other_player.x) / 2
                hit_y = (sword_tip_y + other_player.y) / 2
                self.swing_effects.append({
                    'x': hit_x,
                    'y': hit_y,
                    'alpha': 255
                })

class ClashBattle:
    def __init__(self, player1, player2, screen_width, screen_height):
        self.player1 = player1
        self.player2 = player2
        self.duration = CLASH_BATTLE_DURATION
        self.active = True
        self.winner = None
        self.battle_ended = False
        
        # Center positions
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        
        # Reset player positions and face each other
        self.player1.x = self.center_x - 100
        self.player1.y = self.center_y
        self.player1.direction = 0  # Face right
        
        self.player2.x = self.center_x + 100
        self.player2.y = self.center_y
        self.player2.direction = 180  # Face left
        
        # Reset clash powers
        self.player1.clash_power = CLASH_BATTLE_BAR_WIDTH // 2
        self.player2.clash_power = CLASH_BATTLE_BAR_WIDTH // 2
        
        # Camera zoom effect
        self.zoom = 1.0
        self.target_zoom = 1.5
        
        # Initialize font for timer and instructions
        self.font = pygame.font.Font(None, 36)
        
    def update(self, keys):
        if not self.active:
            return
            
        # Update zoom
        self.zoom += (self.target_zoom - self.zoom) * 0.1
        
        # Update clash powers based on button mashing (reverted to original values)
        if keys[pygame.K_SPACE]:
            self.player1.clash_power += 2
        if keys[pygame.K_RETURN]:
            self.player2.clash_power += 2
            
        # Natural decay of power (reverted to original values)
        self.player1.clash_power -= 1
        self.player2.clash_power -= 1
            
        # Keep powers within bounds
        self.player1.clash_power = min(max(0, self.player1.clash_power), CLASH_BATTLE_BAR_WIDTH)
        self.player2.clash_power = min(max(0, self.player2.clash_power), CLASH_BATTLE_BAR_WIDTH)
        
        # Update duration
        if not self.battle_ended:
            self.duration -= 1
            if self.duration <= 0:
                self.end_battle()
            
    def draw(self, screen):
        if not self.active:
            return
            
        # Draw the clash power bar
        bar_x = (screen.get_width() - CLASH_BATTLE_BAR_WIDTH) // 2
        bar_y = screen.get_height() // 4
        
        # Background bar
        pygame.draw.rect(screen, (50, 50, 50), 
                        (bar_x, bar_y, CLASH_BATTLE_BAR_WIDTH, CLASH_BATTLE_BAR_HEIGHT))
        
        # Calculate power percentages with safeguard against division by zero
        total_power = self.player1.clash_power + self.player2.clash_power
        if total_power > 0:
            split_point = int((self.player1.clash_power / total_power) * CLASH_BATTLE_BAR_WIDTH)
        else:
            split_point = CLASH_BATTLE_BAR_WIDTH // 2
        
        # Player 1's power (left side)
        pygame.draw.rect(screen, self.player1.color,
                        (bar_x, bar_y, split_point, CLASH_BATTLE_BAR_HEIGHT))
        
        # Player 2's power (right side)
        pygame.draw.rect(screen, self.player2.color,
                        (bar_x + split_point, bar_y, 
                         CLASH_BATTLE_BAR_WIDTH - split_point, CLASH_BATTLE_BAR_HEIGHT))
        
        # Create a black background for text to make it more readable
        def draw_text_with_background(text, position):
            text_surface = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=position)
            padding = 5
            bg_rect = text_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
            screen.blit(text_surface, text_rect)
            return text_rect.bottom + padding
        
        # Draw timer with background
        if not self.battle_ended:
            time_left = max(0, self.duration // 60)  # Convert frames to seconds, minimum 0
            timer_pos = (bar_x + CLASH_BATTLE_BAR_WIDTH // 2, bar_y - 30)
            draw_text_with_background(f"Time: {time_left}", timer_pos)
        
        # Draw instructions with background
        if not self.battle_ended:
            instruction_y = bar_y + CLASH_BATTLE_BAR_HEIGHT + 20
            draw_text_with_background("P1: Mash SPACE!", 
                                   (bar_x + 100, instruction_y))
            draw_text_with_background("P2: Mash ENTER!", 
                                   (bar_x + CLASH_BATTLE_BAR_WIDTH - 100, instruction_y))
        
        # Draw who's winning with background
        if not self.battle_ended:
            status_y = bar_y + CLASH_BATTLE_BAR_HEIGHT + 60
            if self.player1.clash_power > self.player2.clash_power:
                status_text = "P1 is winning!"
                status_color = self.player1.color
            elif self.player2.clash_power > self.player1.clash_power:
                status_text = "P2 is winning!"
                status_color = self.player2.color
            else:
                status_text = "It's even!"
                status_color = (255, 255, 255)
            
            text_surface = self.font.render(status_text, True, status_color)
            text_rect = text_surface.get_rect(center=(bar_x + CLASH_BATTLE_BAR_WIDTH // 2, status_y))
            padding = 5
            bg_rect = text_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
            screen.blit(text_surface, text_rect)
        
    def end_battle(self):
        if not self.battle_ended:  # Only run this once
            self.battle_ended = True
            # Determine winner and deal damage
            if self.player1.clash_power > self.player2.clash_power:
                self.winner = self.player1
                self.player2.take_damage(CLASH_DAMAGE)
            elif self.player2.clash_power > self.player1.clash_power:
                self.winner = self.player2
                self.player1.take_damage(CLASH_DAMAGE)
            
            # Reset clash counts
            self.player1.clash_count = 0
            self.player2.clash_count = 0
            
            # Set a short delay before deactivating
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # 1 second delay

# Initialize Pygame font
pygame.font.init()

# Game states
PLAYING = 0
GAME_OVER = 1
ROUND_OVER = 2
game_state = PLAYING

# Timer settings
ROUND_TIME = 5 * 60  # 5 minutes in seconds
timer = ROUND_TIME
last_second = pygame.time.get_ticks() // 1000

# Score tracking
player1_wins = 0
player2_wins = 0

def reset_round():
    global player1, player2, game_state, timer
    pygame.mixer.music.stop()  # Stop the music when there's a winner
    player1 = Player(width // 4, height // 2)
    player2 = Player(3 * width // 4, height // 2, 
                    color=(255, 192, 203),  # Pink
                    body_color=(219, 112, 147))  # Darker pink
    game_state = PLAYING
    timer = ROUND_TIME
    pygame.mixer.music.load('assets/background-music.wav')
    pygame.mixer.music.play(-1)  # Play the music on loop

def draw_timer(screen):
    minutes = timer // 60
    seconds = timer % 60
    font = pygame.font.Font(None, 74)
    timer_text = font.render(f"{minutes:02d}:{seconds:02d}", True, (0, 0, 0))
    timer_rect = timer_text.get_rect(center=(width//2, 40))
    screen.blit(timer_text, timer_rect)

def draw_score(screen):
    font = pygame.font.Font(None, 48)
    # Player 1 score
    score1_text = font.render(f"P1 Wins: {player1_wins}", True, DARK_BLUE)
    screen.blit(score1_text, (20, 60))
    # Player 2 score
    score2_text = font.render(f"P2 Wins: {player2_wins}", True, (219, 112, 147))
    score2_rect = score2_text.get_rect(right=width-20, top=60)
    screen.blit(score2_text, score2_rect)

def draw_game_over(screen, winner):
    font = pygame.font.Font(None, 74)
    text = font.render(f"{winner} Wins!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    
    # Draw text background
    padding = 20
    bg_rect = text_rect.inflate(padding * 2, padding * 2)
    pygame.draw.rect(screen, (0, 0, 0), bg_rect)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
    
    screen.blit(text, text_rect)
    
    # Draw restart instruction
    font_small = pygame.font.Font(None, 36)
    restart_text = font_small.render("Press R to Restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(screen.get_width()//2, text_rect.bottom + 40))
    screen.blit(restart_text, restart_rect)

def draw_round_over(screen, winner):
    font = pygame.font.Font(None, 74)
    text = font.render("Round Over!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    
    # Draw text background
    padding = 20
    bg_rect = text_rect.inflate(padding * 2, padding * 2)
    pygame.draw.rect(screen, (0, 0, 0), bg_rect)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
    
    screen.blit(text, text_rect)
    
    # Draw winner text if there is one
    if winner:
        font_small = pygame.font.Font(None, 48)
        winner_text = font_small.render(f"{winner} wins the round!", True, (255, 255, 255))
        winner_rect = winner_text.get_rect(center=(screen.get_width()//2, text_rect.bottom + 40))
        screen.blit(winner_text, winner_rect)
    
    # Draw restart instruction
    font_small = pygame.font.Font(None, 36)
    restart_text = font_small.render("Press R to Continue", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(screen.get_width()//2, text_rect.bottom + 80))
    screen.blit(restart_text, restart_rect)

# Create try again button
try_again_btn = Button(width//2 - 100, height//2 - 25, 200, 50, "Next Round!", (102, 255, 102))

# Create players
player1 = Player(width // 4, height // 2)
player2 = Player(3 * width // 4, height // 2, 
                color=(255, 192, 203),  # Pink
                body_color=(219, 112, 147))  # Darker pink

# Game loop
clock = pygame.time.Clock()
running = True
clash_battle = None

while running:
    current_time = pygame.time.get_ticks() // 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (game_state == GAME_OVER or game_state == ROUND_OVER):
                reset_round()
                game_state = PLAYING
        # Add clash battle end timer event
        if event.type == pygame.USEREVENT + 1:  # This is our battle end timer
            if clash_battle:
                clash_battle.active = False
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Stop the timer

    # Update background
    background.update()

    # Clear the screen and draw background
    screen.fill(BLACK)
    background.draw(screen)
    
    keys = pygame.key.get_pressed()
    
    if game_state == PLAYING:
        if clash_battle and clash_battle.active:
            clash_battle.update(keys)
        else:
            # Normal game updates
            if clash_battle and clash_battle.winner:
                clash_battle = None  # Reset after battle is done
                
            # Handle player movement
            if not player1.is_dead:
                # Create player 1's control dictionary
                player1_keys = {
                    pygame.K_w: keys[pygame.K_w],
                    pygame.K_s: keys[pygame.K_s],
                    pygame.K_a: keys[pygame.K_a],
                    pygame.K_d: keys[pygame.K_d],
                    pygame.K_SPACE: keys[pygame.K_SPACE]  # Attack key
                }
                player1.move(player1_keys, pygame.K_SPACE)
                player1.is_guarding = keys[pygame.K_g] and player1.guard_cooldown <= 0
            
            if not player2.is_dead:
                # Create player 2's control dictionary
                player2_keys = {
                    pygame.K_w: keys[pygame.K_UP],
                    pygame.K_s: keys[pygame.K_DOWN],
                    pygame.K_a: keys[pygame.K_LEFT],
                    pygame.K_d: keys[pygame.K_RIGHT],
                    pygame.K_RETURN: keys[pygame.K_RETURN]  # Attack key
                }
                player2.move(player2_keys, pygame.K_RETURN)
                player2.is_guarding = keys[pygame.K_n] and player2.guard_cooldown <= 0
            
            # Check for hits and possible clash battle trigger
            result = player1.check_hit(player2)
            if isinstance(result, ClashBattle):
                clash_battle = result
            result = player2.check_hit(player1)
            if isinstance(result, ClashBattle):
                clash_battle = result
            
            # Update players
            player1.update()
            player2.update()
            
            # Check win condition
            if player1.health <= 0:
                player1.is_dead = True
                game_state = GAME_OVER
                winner = "Player 2"
            elif player2.health <= 0:
                player2.is_dead = True
                game_state = GAME_OVER
                winner = "Player 1"
    
    # Draw game elements
    player1.draw(screen)
    player2.draw(screen)
    
    if clash_battle and clash_battle.active:
        clash_battle.draw(screen)
    
    # Draw UI
    player1.draw_health_bar(screen, 10, 10)
    player2.draw_health_bar(screen, screen.get_width() - 210, 10)
    
    if game_state == GAME_OVER:
        draw_game_over(screen, winner)
    elif game_state == ROUND_OVER:
        draw_round_over(screen, winner)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()