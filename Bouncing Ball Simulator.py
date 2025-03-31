import pygame
import random
import sys
import math

# Constants
WIDTH, HEIGHT = 800, 600
GRAVITY = 9.8  # Acceleration due to gravity (m/s^2)
ENERGY_LOSS = 0.8  # Coefficient of restitution (bounciness factor)
BALL_COUNT = 15 # Number of balls
PIXELS_PER_METER = 17  # Scale: 1 meter = 17 pixels
DT = 0.020
BALL_COLOR = (0, 0, 139)  # Dark blue

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# Ball class
class Ball:
    def __init__(self, x, height_meters, radius):
        self.x = x
        self.y = HEIGHT - (height_meters * PIXELS_PER_METER) - 20
        self.radius = radius
        self.color = BALL_COLOR
        self.vx = random.uniform(-15, 15)  # Increased horizontal velocity range
        self.vy = random.uniform(10, 40)  # Increased vertical velocity range

    def update(self):
        # Apply gravity
        self.vy += GRAVITY * DT
        self.y += self.vy * PIXELS_PER_METER * DT
        self.x += self.vx * PIXELS_PER_METER * DT
        
        # Collision with ground
        if self.y + self.radius >= HEIGHT - 20:
            self.y = HEIGHT - 20 - self.radius
            self.vy = -self.vy * ENERGY_LOSS  # Bounce with energy loss
        
        # Collision with walls (left & right boundaries)
        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.vx = -self.vx * ENERGY_LOSS
            self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        
        # Stop the ball if velocity is very low
        if abs(self.vy) < 0.5 and self.y >= HEIGHT - 20 - self.radius:
            self.vy = 0
            self.vx *= 0.95  # Gradually stop horizontal motion

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def check_collision(self, other):
        # Calculate the distance between the centers of the two balls
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)

        # Check if the distance is less than the sum of their radii
        if distance < self.radius + other.radius:
            # Resolve collision by exchanging velocities (simplified elastic collision)
            nx, ny = dx / distance, dy / distance  # Normal vector
            p = 2 * (self.vx * nx + self.vy * ny - other.vx * nx - other.vy * ny) / 2

            self.vx -= p * nx
            self.vy -= p * ny
            other.vx += p * nx
            other.vy += p * ny

# Get user input for height in meters
initial_height_meters = 10.0

# Create balls
balls = [Ball(random.randint(50, WIDTH - 50), initial_height_meters, 10) for _ in range(BALL_COUNT)]

# Simulation loop
running = True
while running:
    screen.fill((255, 255, 255))
    
    # Draw ground
    pygame.draw.line(screen, (0, 0, 0), (0, HEIGHT - 20), (WIDTH, HEIGHT - 20), 3)
    
    # Display initial height in the corner
    text = font.render(f"Initial Height: {initial_height_meters:.2f} m", True, (0, 0, 0))
    screen.blit(text, (10, 10))
    
    # Update and draw balls
    for i, ball in enumerate(balls):
        ball.update()
        for j in range(i + 1, len(balls)):
            ball.check_collision(balls[j])  # Check collision with other balls
        ball.draw()
    
    pygame.display.flip()
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()