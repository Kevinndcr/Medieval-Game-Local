import pygame
import math
import random

class ColiseumBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Keep the coliseum size fixed while allowing for wider window
        self.coliseum_width = min(1000, width)  # Fixed coliseum width
        self.center_x = width // 2  # Center of the window
        
        # Create the base background with a gradient sunset sky
        self.base_bg = pygame.Surface((width, height))
        self.create_gradient((255, 164, 27), (135, 206, 235))  # Sunset orange to sky blue
        
        # Coliseum parameters
        self.pillar_color = (210, 180, 140)  # Tan stone color
        self.arch_color = (180, 150, 110)    # Darker stone
        self.ground_color = (194, 178, 128)   # Sandy ground
        self.shadow_color = (160, 130, 90)    # Shadow color
        
        # Crowd parameters
        self.crowd_colors = [
            (139, 69, 19),   # Brown
            (160, 82, 45),   # Sienna
            (205, 133, 63),  # Peru
            (210, 180, 140), # Tan
        ]
        self.crowd_positions = self.generate_crowd()
    
    def create_gradient(self, color1, color2):
        """Create a vertical gradient from color1 to color2"""
        for y in range(self.height):
            ratio = y / (self.height * 0.7)  # Adjust sky height
            ratio = min(1.0, ratio)
            color = [int(color1[i] + (color2[i] - color1[i]) * ratio) for i in range(3)]
            pygame.draw.line(self.base_bg, color, (0, y), (self.width, y))
    
    def generate_crowd(self):
        """Generate crowd positions in the stands"""
        positions = []
        rows = 3
        for row in range(rows):
            y = self.height * 0.3 + row * 20  # Start from upper stands
            count = 20 + row * 5  # More people in lower rows
            for i in range(count):
                x = self.width * (i + 0.5) / count
                positions.append({
                    'x': x,
                    'y': y,
                    'color': self.crowd_colors[random.randint(0, len(self.crowd_colors)-1)],
                    'wave_offset': random.random() * math.pi * 2
                })
        return positions
    
    def draw_pillar(self, surface, x, y, width, height):
        """Draw a coliseum pillar with shading"""
        pygame.draw.rect(surface, self.pillar_color, (x, y, width, height))
        pygame.draw.rect(surface, self.shadow_color, (x, y, width//4, height))  # Left shadow
        pygame.draw.rect(surface, self.arch_color, (x, y, width, height//8))    # Top detail
    
    def draw_arch(self, surface, x, y, width, height):
        """Draw a coliseum arch"""
        # Draw the arch shape
        pygame.draw.rect(surface, self.arch_color, (x, y + height//2, width, height//2))
        pygame.draw.arc(surface, self.arch_color, (x, y, width, height), 0, math.pi, 3)
    
    def update(self):
        """Update any animated elements"""
        # Update crowd animation
        current_time = pygame.time.get_ticks() / 1000
        for person in self.crowd_positions:
            person['y'] = person['y'] + math.sin(current_time + person['wave_offset']) * 0.2
    
    def draw(self, surface):
        """Draw the complete coliseum background"""
        # Calculate offset to center the coliseum
        offset_x = (self.width - self.coliseum_width) // 2
        
        # Draw sky gradient
        surface.blit(self.base_bg, (0, 0))
        
        # Draw distant mountains (full width)
        mountain_color = (160, 140, 120)
        for i in range(3):
            x_offset = self.width * (i - 1) / 2
            points = [
                (x_offset, self.height * 0.5),
                (x_offset + self.width//2, self.height * 0.2),
                (x_offset + self.width, self.height * 0.5)
            ]
            pygame.draw.polygon(surface, mountain_color, points)
        
        # Draw coliseum structure
        num_sections = 8
        section_width = self.coliseum_width // num_sections
        
        # Draw background arches
        for i in range(num_sections):
            self.draw_arch(surface, offset_x + i * section_width, self.height * 0.3,
                         section_width, section_width * 1.5)
        
        # Draw pillars
        for i in range(num_sections + 1):
            self.draw_pillar(surface, offset_x + i * section_width - 10, self.height * 0.3,
                           20, self.height * 0.5)
        
        # Draw crowd
        for person in self.crowd_positions:
            pygame.draw.circle(surface, person['color'],
                             (int(offset_x + person['x']), int(person['y'])), 5)
        
        # Draw ground
        pygame.draw.rect(surface, self.ground_color,
                        (0, self.height * 0.7, self.width, self.height * 0.3))
        
        # Draw arena circle
        pygame.draw.ellipse(surface, (184, 168, 118),  # Lighter sand color
                          (offset_x + self.coliseum_width * 0.1, self.height * 0.65,
                           self.coliseum_width * 0.8, self.height * 0.2))
