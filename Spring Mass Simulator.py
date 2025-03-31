import pygame
import math

# Pygame setup
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

g = 9.8  # Gravity
k = 0.05  # Spring constant
mass = 2  # Mass of the object
damping = 0.02  # Damping factor

y_equilibrium = HEIGHT // 3  # Equilibrium position
velocity = 0
acceleration = 0
stretch = 20  # Initial displacement

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

def reset_system():
    global stretch, velocity
    stretch = 50  # Reset displacement
    velocity = 0

running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Press 'R' to reset the system
                reset_system()
    
    # Physics calculations
    force_spring = -k * stretch  # Hooke's Law: F = -k * x
    force_gravity = mass * g
    net_force = force_spring + force_gravity
    acceleration = net_force / mass
    velocity += acceleration
    velocity *= (1 - damping)  # Apply damping
    stretch += velocity
    
    # Ball position
    ball_y = y_equilibrium + stretch
    ball_x = WIDTH // 2
    
    # Draw spring
    pygame.draw.line(screen, BLACK, (ball_x, y_equilibrium - 20), (ball_x, int(ball_y)), 4)
    pygame.draw.circle(screen, RED, (ball_x, int(ball_y)), 20)
    
    # Display text info
    info_text = [
        f"Spring Constant: {k}",
        f"Mass: {mass} kg",
        f"Damping: {damping}",
        f"Press 'R' to Reset"
    ]
    for i, text in enumerate(info_text):
        label = font.render(text, True, BLACK)
        screen.blit(label, (10, 10 + i * 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()