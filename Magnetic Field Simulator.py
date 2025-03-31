import pygame
import pymunk
import pymunk.pygame_util
import numpy as np
import math
import random

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Magnetic Field Simulation with Iron Filings")
clock = pygame.time.Clock()

# Colors
BACKGROUND = (0, 0, 0)
IRON_COLOR = (180, 180, 180)
N_POLE_COLOR = (255, 0, 0)
S_POLE_COLOR = (0, 0, 255)
WHITE = (255, 255, 255)

# Physics setup
space = pymunk.Space()
space.gravity = (0, 0)  # No gravity
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Constants
IRON_RADIUS = 2
IRON_MASS = 1
MAGNET_STRENGTH = 5000
DAMPING = 0.7  # Air resistance
DIPOLE_STRENGTH = 10  # Strength of dipole-dipole interaction

# Create a background surface
background = pygame.Surface((WIDTH, HEIGHT))
background.fill(BACKGROUND)

class Magnet:
    def __init__(self, pos, strength=MAGNET_STRENGTH, width=100, height=30, is_north_up=True):
        self.pos = pos
        self.strength = strength
        self.width = width
        self.height = height
        self.is_north_up = is_north_up
        self.rect = pygame.Rect(
            self.pos[0] - self.width/2,
            self.pos[1] - self.height/2,
            self.width,
            self.height
        )
        
    def get_field_at(self, pos):
        """Calculate magnetic field vector at given position"""
        dx = pos[0] - self.pos[0]
        dy = pos[1] - self.pos[1]
        distance_squared = dx*dx + dy*dy
        
        # Avoid division by zero
        if distance_squared < 1:
            distance_squared = 1
            
        # Simple inverse square law for field strength
        strength = self.strength / distance_squared
        
        # Field direction depends on pole orientation
        direction = 1 if self.is_north_up else -1
        
        # Calculate field components
        if abs(dx) < self.width/2 and abs(dy) < self.height/2:
            # Inside the magnet, field points straight up or down
            return (0, direction * strength)
        else:
            # Outside the magnet, field curves from north to south
            r = math.sqrt(distance_squared)
            # Simplified dipole field
            fx = 3 * dx * dy * strength / (r**5) * direction
            fy = strength * (3 * dy * dy / (r**5) - 1 / (r**3)) * direction
            
            # Normalize and scale
            mag = math.sqrt(fx*fx + fy*fy)
            if mag > 0:
                fx = fx / mag * strength
                fy = fy / mag * strength
                
            return (fx, fy)
    
    def draw(self, surface):
        # Draw magnet body
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        # Draw N and S poles
        n_rect = pygame.Rect(
            self.pos[0] - self.width/2,
            self.pos[1] - self.height/2 if self.is_north_up else self.pos[1],
            self.width,
            self.height/2
        )
        
        s_rect = pygame.Rect(
            self.pos[0] - self.width/2,
            self.pos[1] if self.is_north_up else self.pos[1] - self.height/2,
            self.width,
            self.height/2
        )
        
        n_color = N_POLE_COLOR if self.is_north_up else S_POLE_COLOR
        s_color = S_POLE_COLOR if self.is_north_up else N_POLE_COLOR
        
        pygame.draw.rect(surface, n_color, n_rect)
        pygame.draw.rect(surface, s_color, s_rect)
        
        # Label poles
        font = pygame.font.SysFont('Arial', 20, bold=True)
        n_text = font.render("N", True, WHITE)
        s_text = font.render("S", True, WHITE)
        
        n_pos = (self.pos[0], self.pos[1] - self.height/4 if self.is_north_up else self.pos[1] + self.height/4)
        s_pos = (self.pos[0], self.pos[1] + self.height/4 if self.is_north_up else self.pos[1] - self.height/4)
        
        surface.blit(n_text, (n_pos[0] - n_text.get_width()/2, n_pos[1] - n_text.get_height()/2))
        surface.blit(s_text, (s_pos[0] - s_text.get_width()/2, s_pos[1] - s_text.get_height()/2))
        return self.rect

class IronFiling(pygame.sprite.DirtySprite):
    def __init__(self, pos):
        pygame.sprite.DirtySprite.__init__(self)
        self.body = pymunk.Body(IRON_MASS, pymunk.moment_for_circle(IRON_MASS, 0, IRON_RADIUS))
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, IRON_RADIUS)
        self.shape.friction = 0.5
        self.shape.elasticity = 0.1
        
        # Add damping to simulate air resistance
        self.body.velocity_func = self.damping_velocity_func
        
        # Dipole moment - initially random
        self.dipole_angle = random.uniform(0, 2*math.pi)
        self.dipole_strength = DIPOLE_STRENGTH
        
        # For dirty sprite
        self.image = pygame.Surface((IRON_RADIUS*4, IRON_RADIUS*4), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.dirty = 2  # Always dirty
        
        # Add to space
        space.add(self.body, self.shape)
    
    def damping_velocity_func(self, body, gravity, damping, dt):
        # Custom damping function
        pymunk.Body.update_velocity(body, gravity, DAMPING, dt)
    
    def apply_magnetic_force(self, field_vector):
        # Calculate torque to align with field
        field_angle = math.atan2(field_vector[1], field_vector[0])
        angle_diff = ((field_angle - self.dipole_angle + math.pi) % (2*math.pi)) - math.pi
        
        # Torque is proportional to sine of angle difference
        torque = self.dipole_strength * math.sin(angle_diff) * 5
        self.body.angular_velocity += torque
        
        # Update dipole angle based on body rotation
        self.dipole_angle = (self.dipole_angle + self.body.angular_velocity * 0.1) % (2*math.pi)
        
        # Apply force in direction of field gradient
        field_strength = math.sqrt(field_vector[0]**2 + field_vector[1]**2)
        force_scale = field_strength * 0.5
        force = (field_vector[0] * force_scale, field_vector[1] * force_scale)
        self.body.apply_force_at_local_point(force, (0, 0))
    
    def apply_dipole_interaction(self, other):
        # Calculate vector between filings
        dx = other.body.position.x - self.body.position.x
        dy = other.body.position.y - self.body.position.y
        r_squared = dx*dx + dy*dy
        
        if r_squared < 1:
            return  # Avoid division by zero
        
        # Calculate dipole-dipole interaction force
        r = math.sqrt(r_squared)
        
        # Get unit vector in direction of other filing
        nx = dx / r
        ny = dy / r
        
        # Calculate dot products of dipole orientations with separation vector
        dot1 = nx * math.cos(self.dipole_angle) + ny * math.sin(self.dipole_angle)
        dot2 = nx * math.cos(other.dipole_angle) + ny * math.sin(other.dipole_angle)
        
        # Calculate dipole-dipole interaction (simplified)
        strength = (3 * dot1 * dot2 - math.cos(self.dipole_angle - other.dipole_angle)) / (r_squared * r)
        strength *= self.dipole_strength * other.dipole_strength * 0.01
        
        force = (nx * strength, ny * strength)
        self.body.apply_force_at_local_point(force, (0, 0))
    
    def update(self):
        # Update sprite position based on physics body
        self.rect.center = (int(self.body.position.x), int(self.body.position.y))
        
        # Clear the image
        self.image.fill((0, 0, 0, 0))
        
        # Draw the filing as a small line oriented along its dipole
        center = (self.image.get_width()//2, self.image.get_height()//2)
        end_x = center[0] + IRON_RADIUS * 2 * math.cos(self.dipole_angle)
        end_y = center[1] + IRON_RADIUS * 2 * math.sin(self.dipole_angle)
        pygame.draw.line(self.image, IRON_COLOR, center, (end_x, end_y), 2)

# Create magnets
magnets = [
    Magnet((WIDTH//2, HEIGHT//2), is_north_up=True)
]

# Create iron filings sprite group
filings_group = pygame.sprite.LayeredDirty()
filings = []

# Create 1000 iron filings
for _ in range(1000):
    x = random.uniform(100, WIDTH-100)
    y = random.uniform(100, HEIGHT-100)
    filing = IronFiling((x, y))
    filings.append(filing)
    filings_group.add(filing)

# Create UI elements
font = pygame.font.SysFont('Arial', 20)
font_surface = font.render("Press F to toggle field lines", True, WHITE).convert_alpha()

# Create buttons
add_magnet_button = pygame.Rect(WIDTH - 200, 20, 180, 40)
flip_magnet_button = pygame.Rect(WIDTH - 200, 70, 180, 40)
clear_button = pygame.Rect(WIDTH - 200, 120, 180, 40)

# Pre-render button text
add_text = font.render("Toggle 2nd Magnet", True, WHITE).convert_alpha()
flip_text = font.render("Flip Magnets", True, WHITE).convert_alpha()
clear_text = font.render("Reset Filings", True, WHITE).convert_alpha()

# Create field line surface
field_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Main loop
running = True
show_field_lines = False
dirty_rects = []

# Draw initial background
screen.blit(background, (0, 0))
pygame.display.flip()

while running:
    dirty_rects = []
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                show_field_lines = not show_field_lines
                dirty_rects.append(pygame.Rect(0, 0, WIDTH, HEIGHT))  # Full screen update needed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if add_magnet_button.collidepoint(mouse_pos):
                if len(magnets) == 1:
                    # Add second magnet
                    magnets.append(Magnet((WIDTH//2 - 150, HEIGHT//2), is_north_up=False))
                else:
                    # Remove second magnet
                    magnets.pop()
                dirty_rects.append(pygame.Rect(0, 0, WIDTH, HEIGHT))  # Full screen update needed
            
            elif flip_magnet_button.collidepoint(mouse_pos):
                # Flip the orientation of all magnets
                for magnet in magnets:
                    magnet.is_north_up = not magnet.is_north_up
                dirty_rects.append(pygame.Rect(0, 0, WIDTH, HEIGHT))  # Full screen update needed
            
            elif clear_button.collidepoint(mouse_pos):
                # Remove all filings and create new ones
                for filing in filings:
                    space.remove(filing.body, filing.shape)
                filings.clear()
                filings_group.empty()
                
                for _ in range(1000):
                    x = random.uniform(100, WIDTH-100)
                    y = random.uniform(100, HEIGHT-100)
                    filing = IronFiling((x, y))
                    filings.append(filing)
                    filings_group.add(filing)
                dirty_rects.append(pygame.Rect(0, 0, WIDTH, HEIGHT))  # Full screen update needed
    
    # Calculate total field at each filing position
    for filing in filings:
        total_field = [0, 0]
        for magnet in magnets:
            field = magnet.get_field_at(filing.body.position)
            total_field[0] += field[0]
            total_field[1] += field[1]
        
        filing.apply_magnetic_force(total_field)
    
    # Apply dipole-dipole interactions between nearby filings (using spatial partitioning)
    for i, filing1 in enumerate(filings):
        pos1 = filing1.body.position
        # Only check filings that haven't been checked yet
        for filing2 in filings[i+1:]:
            pos2 = filing2.body.position
            dist_squared = (pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2
            if dist_squared < 100:  # Only interact with nearby filings
                filing1.apply_dipole_interaction(filing2)
                filing2.apply_dipole_interaction(filing1)
    
    # Update physics
    space.step(1/60.0)
    
    # Update sprites
    filings_group.update()
    
    # Draw background
    screen.blit(background, (0, 0))
    dirty_rects.append(pygame.Rect(0, 0, WIDTH, HEIGHT))
    
    # Draw field lines if enabled
    if show_field_lines:
        field_surface.fill((0, 0, 0, 0))
        for x in range(0, WIDTH, 20):
            for y in range(0, HEIGHT, 20):
                total_field = [0, 0]
                for magnet in magnets:
                    field = magnet.get_field_at((x, y))
                    total_field[0] += field[0]
                    total_field[1] += field[1]
                
                # Normalize and scale for visualization
                magnitude = math.sqrt(total_field[0]**2 + total_field[1]**2)
                if magnitude > 0:
                    scale = min(10, magnitude / 10)
                    dx = total_field[0] / magnitude * scale
                    dy = total_field[1] / magnitude * scale
                    pygame.draw.line(field_surface, (100, 100, 255), (x, y), (x + dx, y + dy), 1)
        screen.blit(field_surface, (0, 0))
    
    # Draw filings using dirty sprite group
    filings_group.draw(screen)
    
    # Draw magnets
    for magnet in magnets:
        rect = magnet.draw(screen)
        dirty_rects.append(rect)
    
    # Draw buttons
    pygame.draw.rect(screen, (100, 100, 100), add_magnet_button)
    pygame.draw.rect(screen, (100, 100, 100), flip_magnet_button)
    pygame.draw.rect(screen, (100, 100, 100), clear_button)
    
    screen.blit(add_text, (add_magnet_button.x + 10, add_magnet_button.y + 10))
    screen.blit(flip_text, (flip_magnet_button.x + 40, flip_magnet_button.y + 10))
    screen.blit(clear_text, (clear_button.x + 40, clear_button.y + 10))
    
    # Display instructions
    screen.blit(font_surface, (20, 20))
    
    # Update only dirty rectangles
    pygame.display.update(dirty_rects)
    clock.tick(60)

pygame.quit()
