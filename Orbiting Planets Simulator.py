import pygame
import math

# Constants
WIDTH, HEIGHT = 1920, 1080
G = 6.67430e-11  # Gravitational constant
SCALE = 2.5e9  # Increased scale to make outer planets visible (1 pixel = SCALE meters)
TIME_STEP = 3600  # Time step in seconds (1 hour)

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)
BLUE = (100, 149, 237)
RED = (255, 69, 0)
GRAY = (169, 169, 169)
ORANGE = (255, 140, 0)
LIGHT_BLUE = (173, 216, 230)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
TURQUOISE = (64, 224, 208)  # New color for Uranus
DARK_BLUE = (0, 0, 139)  # Darker blue for Neptune to distinguish from Earth

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, 0, 5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, 5)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class Planet:
    def __init__(self, x, y, mass, radius, color, name, vx=0, vy=0):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = max(radius, 3)  # Ensure minimum visibility
        self.color = color
        self.name = name
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = 0
    
    def update_position(self):
        # Update velocity based on acceleration
        self.vx += self.ax * TIME_STEP
        self.vy += self.ay * TIME_STEP
        # Update position based on velocity
        self.x += self.vx * TIME_STEP
        self.y += self.vy * TIME_STEP
    
    def apply_gravity(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        r = math.sqrt(dx**2 + dy**2)
        
        if r < self.radius + other.radius:
            return  # Prevent extreme forces in case of collision
        
        force = G * self.mass * other.mass / r**2
        ax = force / self.mass * (dx / r)
        ay = force / self.mass * (dy / r)
        
        self.ax += ax
        self.ay += ay
    
    def draw(self, screen, font):
        x = WIDTH // 2 + int(self.x / SCALE)
        y = HEIGHT // 2 + int(self.y / SCALE)
        
        # Draw the planet
        pygame.draw.circle(screen, self.color, (x, y), self.radius)
        
        # Draw rings for Uranus (simplified representation)
        if self.name == "Uranus":
            ring_color = (200, 200, 255)  # Light blue-white for rings
            pygame.draw.ellipse(screen, ring_color, (x - self.radius*1.8, y - self.radius/3, 
                                                   self.radius*3.6, self.radius/1.5), 1)
        
        # Draw planet name
        text = font.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=(x, y - self.radius - 15))
        screen.blit(text, text_rect)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Orbiting Planets Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 16)
button_font = pygame.font.SysFont('Arial', 20, bold=True)

# Create exit button
exit_button = Button(WIDTH - 120, 20, 100, 40, "EXIT", RED, (200, 0, 0))

# Create Sun and Planets
sun = Planet(0, 0, 1.989e30, 15, YELLOW, "Sun")
mercury = Planet(5.79e10, 0, 3.285e23, 5, GRAY, "Mercury", 0, 47.87e3)
venus = Planet(1.082e11, 0, 4.867e24, 7, ORANGE, "Venus", 0, 35.02e3)
earth = Planet(1.496e11, 0, 5.972e24, 8, BLUE, "Earth", 0, 29.78e3)
mars = Planet(2.279e11, 0, 6.39e23, 6, RED, "Mars", 0, 24.07e3)
jupiter = Planet(7.785e11, 0, 1.898e27, 12, BROWN, "Jupiter", 0, 13.07e3)
saturn = Planet(1.429e12, 0, 5.683e26, 10, LIGHT_BLUE, "Saturn", 0, 9.69e3)

# Adjusted distances for Uranus and Neptune to fit on screen
uranus = Planet(1.8e12, 0, 8.681e25, 11, TURQUOISE, "Uranus", 0, 6.81e3)
neptune = Planet(2.2e12, 0, 1.024e26, 9, DARK_BLUE, "Neptune", 0, 5.43e3)

planets = [mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]

running = True
while running:
    screen.fill(BLACK)
    
    # Handle events
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_click = True
    
    # Check button hover and click
    exit_button.check_hover(mouse_pos)
    if exit_button.is_clicked(mouse_pos, mouse_click):
        running = False
    
    # Update and draw planets
    for planet in planets:
        planet.ax, planet.ay = 0, 0  # Reset acceleration
        planet.apply_gravity(sun)  # Apply Sun's gravity
        planet.update_position()
        planet.draw(screen, font)
    
    # Draw sun
    sun.draw(screen, font)
    
    # Draw exit button
    exit_button.draw(screen, button_font)
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
