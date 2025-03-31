import pygame
import random
import sys
import math

# Constants
WIDTH, HEIGHT = 800, 600
GRAVITY = 9.8  # Acceleration due to gravity (m/s^2)
ENERGY_LOSS = 0.8  # Coefficient of restitution (bounciness factor)
BALL_COUNT = 10
PIXELS_PER_METER = 50  # Scale: 1 meter = 50 pixels
DT = 0.016  # Time step (seconds per frame, ~60 FPS)
BALL_COLOR = (0, 0, 139)  # Dark blue
BALL_RADIUS = 10  # Normal ball size

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# Ball class
class Ball:
    def __init__(self, x, height_meters):
        self.x = x
        self.y = HEIGHT - (height_meters * PIXELS_PER_METER) - 20
        self.radius = BALL_RADIUS
        self.color = BALL_COLOR
        self.vx = random.uniform(-3, 3)  # Random initial horizontal velocity in m/s
        self.vy = random.uniform(1, 5)  # Random initial vertical velocity in m/s

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

# Collision handling with momentum exchange
def handle_collisions():
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            dx = balls[j].x - balls[i].x
            dy = balls[j].y - balls[i].y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < balls[i].radius + balls[j].radius:  # Collision detected
                angle = math.atan2(dy, dx)
                
                # Velocity components along the collision axis
                v1_parallel = balls[i].vx * math.cos(angle) + balls[i].vy * math.sin(angle)
                v2_parallel = balls[j].vx * math.cos(angle) + balls[j].vy * math.sin(angle)
                
                # Exchange velocities (elastic collision)
                balls[i].vx += (v2_parallel - v1_parallel) * math.cos(angle)
                balls[i].vy += (v2_parallel - v1_parallel) * math.sin(angle)
                balls[j].vx += (v1_parallel - v2_parallel) * math.cos(angle)
                balls[j].vy += (v1_parallel - v2_parallel) * math.sin(angle)
                
                # Push balls apart to prevent sticking
                overlap = (balls[i].radius + balls[j].radius - distance) / 2
                balls[i].x -= overlap * math.cos(angle)
                balls[i].y -= overlap * math.sin(angle)
                balls[j].x += overlap * math.cos(angle)
                balls[j].y += overlap * math.sin(angle)

# Get user input for height in meters
initial_height_meters = float(input("Enter initial height (meters): "))

# Create balls
balls = [Ball(random.randint(50, WIDTH - 50), initial_height_meters) for _ in range(BALL_COUNT)]

# Simulation loop
running = True
while running:
    screen.fill((255, 255, 255))
    
    # Draw ground
    pygame.draw.line(screen, (0, 0, 0), (0, HEIGHT - 20), (WIDTH, HEIGHT - 20), 3)
    
    # Display initial height in the corner
    text = font.render(f"Initial Height: {initial_height_meters:.2f} m", True, (0, 0, 0))
    screen.blit(text, (10, 10))
    
    # Handle ball collisions
    handle_collisions()
    
    # Update and draw balls
    for ball in balls:
        ball.update()
        ball.draw()
    
    pygame.display.flip()
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()
