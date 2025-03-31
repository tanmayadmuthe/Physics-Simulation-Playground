import pymunk
import pymunk.pygame_util
import pygame
import random
import math
import numpy as np

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Collapse Simulation")
clock = pygame.time.Clock()

# Physics constants
GRAVITY = 981  # Gravity strength (9.81 m/s²)
TIME_STEP = 1.0 / 60.0  # Physics timestep
BLOCK_DENSITY = 5.0  # Density of blocks
GROUND_FRICTION = 0.8  # Ground friction coefficient
BLOCK_FRICTION = 0.6  # Block-to-block friction
BLOCK_ELASTICITY = 0.2  # Block elasticity/restitution
AIR_DAMPING = 0.9  # Air resistance factor

# Colors
BACKGROUND = (50, 50, 50)
GROUND_COLOR = (80, 80, 80)
BLOCK_COLORS = [
    (220, 170, 100),  # Light wood
    (200, 150, 80),   # Medium wood
    (180, 130, 60)    # Dark wood
]
TEXT_COLOR = (255, 255, 255)

# Create a pymunk space
space = pymunk.Space()
space.gravity = (0, GRAVITY)
space.damping = AIR_DAMPING  # Add air resistance

# Drawing options
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Font for UI
font = pygame.font.SysFont('Arial', 24)

class Block:
    def __init__(self, pos, size, mass=None, color=None):
        self.pos = pos
        self.size = size
        
        # Calculate mass based on density and size if not provided
        if mass is None:
            mass = size[0] * size[1] * BLOCK_DENSITY / 100
        
        # Create body and shape
        moment = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos
        
        # Add slight random rotation to make tower less stable
        self.body.angle = random.uniform(-0.03, 0.03)
        
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.friction = BLOCK_FRICTION
        self.shape.elasticity = BLOCK_ELASTICITY
        
        # Add material imperfections (slight variations in friction and elasticity)
        self.shape.friction *= random.uniform(0.95, 1.05)
        self.shape.elasticity *= random.uniform(0.95, 1.05)
        
        # Set color
        self.color = color if color else random.choice(BLOCK_COLORS)
        
        # Add to space
        space.add(self.body, self.shape)

def create_ground():
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 5)
    shape.friction = GROUND_FRICTION
    shape.elasticity = 0.2
    space.add(body, shape)
    return shape

def create_tower(x_center, base_y, width, height, block_width, block_height, layers):
    blocks = []
    
    # Calculate vertical spacing based on total height and layers
    y_spacing = height / layers
    
    # Calculate number of blocks per layer based on width
    blocks_per_layer = max(1, int(width / block_width))
    
    for layer in range(layers):
        # Alternate orientation for stability
        if layer % 2 == 0:
            # Horizontal layer
            for i in range(blocks_per_layer):
                x = x_center - (width / 2) + (i * block_width) + (block_width / 2)
                y = base_y - (layer * y_spacing)
                
                # Add slight position imperfections
                x += random.uniform(-1, 1)
                y += random.uniform(-0.5, 0.5)
                
                # Create block with slight variations in size
                size_variation = random.uniform(0.95, 1.05)
                block = Block(
                    (x, y), 
                    (block_width * size_variation, block_height),
                    color=BLOCK_COLORS[layer % len(BLOCK_COLORS)]
                )
                blocks.append(block)
        else:
            # Vertical layer
            # Calculate how many blocks can fit in the width
            rotated_blocks_per_layer = max(1, int(width / block_height))
            
            for i in range(rotated_blocks_per_layer):
                x = x_center - (width / 2) + (i * block_height) + (block_height / 2)
                y = base_y - (layer * y_spacing)
                
                # Add slight position imperfections
                x += random.uniform(-1, 1)
                y += random.uniform(-0.5, 0.5)
                
                # Create block with slight variations in size
                size_variation = random.uniform(0.95, 1.05)
                block = Block(
                    (x, y), 
                    (block_height, block_width * size_variation),
                    color=BLOCK_COLORS[layer % len(BLOCK_COLORS)]
                )
                blocks.append(block)
    
    return blocks

def apply_wind_force(blocks, strength):
    for block in blocks:
        # Apply force proportional to block's surface area facing the wind
        force = strength * block.size[0] * block.size[1] / 1000
        
        # Apply at a slight angle for more realistic effect
        angle = random.uniform(-0.2, 0.2)
        force_vector = (force * math.cos(angle), force * math.sin(angle))
        
        # Apply at center of mass with slight offset
        offset = (random.uniform(-block.size[0]/4, block.size[0]/4), 
                 random.uniform(-block.size[1]/4, block.size[1]/4))
        block.body.apply_force_at_local_point(force_vector, offset)

def calculate_center_of_mass(blocks):
    if not blocks:
        return (0, 0)
    
    total_mass = 0
    weighted_x = 0
    weighted_y = 0
    
    for block in blocks:
        mass = block.body.mass
        total_mass += mass
        weighted_x += block.body.position.x * mass
        weighted_y += block.body.position.y * mass
    
    if total_mass > 0:
        return (weighted_x / total_mass, weighted_y / total_mass)
    return (0, 0)

def calculate_stability_index(blocks, com):
    if not blocks:
        return 1.0
    
    # Find the base blocks (lowest y positions)
    base_blocks = sorted(blocks, key=lambda b: b.body.position.y, reverse=True)[:3]
    
    if not base_blocks:
        return 0.0
    
    # Calculate the base width
    leftmost = min(b.body.position.x - b.size[0]/2 for b in base_blocks)
    rightmost = max(b.body.position.x + b.size[0]/2 for b in base_blocks)
    base_width = rightmost - leftmost
    
    # Calculate how centered the COM is over the base
    com_x = com[0]
    base_center = (leftmost + rightmost) / 2
    offset = abs(com_x - base_center)
    
    # Normalize to get a stability index between 0 and 1
    # 1 = perfectly stable, 0 = about to topple
    stability = max(0, 1 - (2 * offset / base_width))
    return stability

def main():
    ground = create_ground()
    
    # Tower parameters
    tower_x = WIDTH // 2
    tower_base_y = HEIGHT - 55
    tower_width = 300
    tower_height = 500
    block_width = 80
    block_height = 30
    layers = 15
    
    blocks = create_tower(tower_x, tower_base_y, tower_width, tower_height, 
                         block_width, block_height, layers)
    
    # Simulation state
    running = True
    paused = False
    wind_active = False
    wind_strength = 0
    
    # For measuring time
    simulation_time = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reset simulation
                    for block in blocks:
                        space.remove(block.body, block.shape)
                    blocks = create_tower(tower_x, tower_base_y, tower_width, tower_height, 
                                         block_width, block_height, layers)
                    simulation_time = 0
                elif event.key == pygame.K_w:
                    # Toggle wind
                    wind_active = not wind_active
                    wind_strength = 500 if wind_active else 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Apply impulse at mouse position
                mouse_pos = pygame.mouse.get_pos()
                
                # Find closest block to mouse
                closest_block = None
                min_dist = float('inf')
                
                for block in blocks:
                    dist = ((block.body.position.x - mouse_pos[0])**2 + 
                            (block.body.position.y - mouse_pos[1])**2)**0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_block = block
                
                if closest_block and min_dist < 100:
                    # Apply impulse in direction from mouse to block
                    dx = closest_block.body.position.x - mouse_pos[0]
                    dy = closest_block.body.position.y - mouse_pos[1]
                    
                    # Normalize and scale
                    length = (dx**2 + dy**2)**0.5
                    if length > 0:
                        dx /= length
                        dy /= length
                        
                    impulse = (dx * 5000, dy * 5000)
                    closest_block.body.apply_impulse_at_local_point(impulse, (0, 0))
        
        screen.fill(BACKGROUND)
        
        # Update physics if not paused
        if not paused:
            # Apply wind if active
            if wind_active:
                apply_wind_force(blocks, wind_strength)
            
            # Step the simulation
            space.step(TIME_STEP)
            simulation_time += TIME_STEP
        
        # Draw ground
        pygame.draw.line(screen, GROUND_COLOR, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 10)
        
        # Draw all objects
        space.debug_draw(draw_options)
        
        # Calculate center of mass and stability
        com = calculate_center_of_mass(blocks)
        stability = calculate_stability_index(blocks, com)
        
        # Draw center of mass
        pygame.draw.circle(screen, (255, 0, 0), (int(com[0]), int(com[1])), 5)
        
        # Draw UI
        time_text = font.render(f"Time: {simulation_time:.2f}s", True, TEXT_COLOR)
        stability_text = font.render(f"Stability: {stability:.2f}", True, TEXT_COLOR)
        help_text = font.render("Space: Pause | R: Reset | W: Wind | Click: Apply Force", True, TEXT_COLOR)
        
        screen.blit(time_text, (20, 20))
        screen.blit(stability_text, (20, 50))
        screen.blit(help_text, (20, HEIGHT - 40))
        
        if wind_active:
            wind_text = font.render("Wind Active", True, (255, 200, 200))
            screen.blit(wind_text, (WIDTH - 150, 20))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()
