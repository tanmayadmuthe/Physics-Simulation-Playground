import pygame
import math

# Pygame setup
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

g = 9.81  # Gravity
pixel_to_meter = 15  # 1 meter = 15 pixels
length1_m = 10  # Length of first pendulum in meters
length2_m = 10  # Length of second pendulum in meters
length1 = length1_m * pixel_to_meter  # Convert to pixels
length2 = length2_m * pixel_to_meter  # Convert to pixels
mass1 = 5  # Mass of first bob
mass2 = 10  # Mass of second bob

theta1 = math.pi / 2  # Initial angle of first pendulum
theta2 = math.pi / 2  # Initial angle of second pendulum
omega1 = 0  # Angular velocity of first pendulum
omega2 = 0  # Angular velocity of second pendulum
dt = 0.05  # Time step

def calculate_acceleration(theta1, theta2, omega1, omega2):
    num1 = -g * (2 * mass1 + mass2) * math.sin(theta1)
    num2 = -mass2 * g * math.sin(theta1 - 2 * theta2)
    num3 = -2 * math.sin(theta1 - theta2) * mass2
    num4 = omega2**2 * length2 + omega1**2 * length1 * math.cos(theta1 - theta2)
    den = length1 * (2 * mass1 + mass2 - mass2 * math.cos(2 * theta1 - 2 * theta2))
    alpha1 = (num1 + num2 + num3 * num4) / den
    
    num5 = 2 * math.sin(theta1 - theta2)
    num6 = (omega1**2 * length1 * (mass1 + mass2) + g * (mass1 + mass2) * math.cos(theta1))
    num7 = omega2**2 * length2 * mass2 * math.cos(theta1 - theta2)
    den2 = length2 * (2 * mass1 + mass2 - mass2 * math.cos(2 * theta1 - 2 * theta2))
    alpha2 = (num5 * (num6 + num7)) / den2
    
    return alpha1, alpha2

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

origin = (WIDTH // 2, HEIGHT // 3)

running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Compute accelerations
    alpha1, alpha2 = calculate_acceleration(theta1, theta2, omega1, omega2)
    
    # Update velocities and angles
    omega1 += alpha1 * dt
    omega2 += alpha2 * dt
    theta1 += omega1 * dt
    theta2 += omega2 * dt
    
    # Calculate bob positions
    x1 = origin[0] + length1 * math.sin(theta1)
    y1 = origin[1] + length1 * math.cos(theta1)
    x2 = x1 + length2 * math.sin(theta2)
    y2 = y1 + length2 * math.cos(theta2)
    
    # Draw pendulums
    pygame.draw.line(screen, BLACK, origin, (x1, y1), 2)
    pygame.draw.circle(screen, RED, (int(x1), int(y1)), 10)
    pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 2)
    pygame.draw.circle(screen, BLUE, (int(x2), int(y2)), 10)
    
    # Display text info
    info_text = [
        "Double Pendulum Chaos",
        f"Mass1: {mass1} kg, Mass2: {mass2} kg",
        f"Length1: {length1_m} m, Length2: {length2_m} m",
        f"Gravity: {g} m/s²"
    ]
    for i, text in enumerate(info_text):
        label = font.render(text, True, BLACK)
        screen.blit(label, (10, 10 + i * 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
