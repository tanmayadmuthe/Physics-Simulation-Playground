import pygame
import math

# Pygame setup
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)  # Font for displaying text

# Pendulum properties
origin = (WIDTH // 2, 100)  # Fixed pivot point
length = 200  # Length of the pendulum

gravity = 9.80  # Gravity
damping = 0.02  # Air resistance factor

# User input fields
input_active = True
angle_deg = 45  # Default angle
mass = 10  # Default mass
start_simulation = False

# Initialize physics variables
def update_angle(value):
    global angle, angle_deg
    angle_deg = value
    angle = math.radians(angle_deg)

update_angle(angle_deg)
angular_velocity = 0  # Initial angular velocity
angular_acceleration = 0  # Initial angular acceleration

# Input box setup
input_box_angle = pygame.Rect(200, 250, 140, 32)
input_box_mass = pygame.Rect(200, 300, 140, 32)
start_button = pygame.Rect(WIDTH - 200, HEIGHT - 60, 140, 40)  # Bottom-right corner
exit_button = pygame.Rect(60, HEIGHT - 60, 140, 40)  # Bottom-left corner
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active_angle = False
active_mass = False
text_angle = str(angle_deg)
text_mass = str(mass)

while True:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if input_box_angle.collidepoint(event.pos):
                active_angle = True
                active_mass = False
            elif input_box_mass.collidepoint(event.pos):
                active_mass = True
                active_angle = False
            elif start_button.collidepoint(event.pos):
                start_simulation = True
                update_angle(float(text_angle))
                mass = float(text_mass)
            elif exit_button.collidepoint(event.pos):
                start_simulation = False
                angular_velocity = 0
                update_angle(45)
                mass = 10
                text_angle = str(angle_deg)
                text_mass = str(mass)
            else:
                active_angle = False
                active_mass = False
        elif event.type == pygame.KEYDOWN:
            if active_angle:
                if event.key == pygame.K_RETURN:
                    update_angle(float(text_angle))
                    active_angle = False
                elif event.key == pygame.K_BACKSPACE:
                    text_angle = text_angle[:-1]
                else:
                    text_angle += event.unicode
            elif active_mass:
                if event.key == pygame.K_RETURN:
                    mass = float(text_mass)
                    active_mass = False
                elif event.key == pygame.K_BACKSPACE:
                    text_mass = text_mass[:-1]
                else:
                    text_mass += event.unicode
    
    if not start_simulation:
        pygame.draw.rect(screen, color_active if active_angle else color_inactive, input_box_angle, 2)
        pygame.draw.rect(screen, color_active if active_mass else color_inactive, input_box_mass, 2)
        pygame.draw.rect(screen, BLACK, start_button)
        
        angle_surface = font.render(text_angle, True, BLACK)
        mass_surface = font.render(text_mass, True, BLACK)
        button_text = font.render("Start", True, WHITE)
        
        screen.blit(angle_surface, (input_box_angle.x + 5, input_box_angle.y + 5))
        screen.blit(mass_surface, (input_box_mass.x + 5, input_box_mass.y + 5))
        screen.blit(button_text, (start_button.x + 50, start_button.y + 10))
        
        screen.blit(font.render("Enter Initial Angle:", True, BLACK), (50, 255))
        screen.blit(font.render("Enter Mass:", True, BLACK), (50, 305))
    
    if start_simulation:
        # Physics calculations
        force_gravity = -gravity * math.sin(angle) / length  # Torque equation
        angular_acceleration = force_gravity - damping * angular_velocity  # Adding air resistance
        angular_velocity += angular_acceleration  # Update velocity
        angle += angular_velocity  # Update angle
        
        # Calculate bob position
        bob_x = origin[0] + length * math.sin(angle)
        bob_y = origin[1] + length * math.cos(angle)
        bob_pos = (int(bob_x), int(bob_y))
        
        # Draw pendulum
        pygame.draw.line(screen, BLACK, origin, bob_pos, 2)
        pygame.draw.circle(screen, BLACK, bob_pos, 15)
        
        # Display text info
        info_text = [
            f"Mass: {mass} kg",
            f"Damping: {damping}",
            f"Initial Angle: {angle_deg}°"
        ]
        for i, text in enumerate(info_text):
            label = font.render(text, True, BLACK)
            screen.blit(label, (10, 10 + i * 20))
    
    # Draw the exit button (always visible)
    pygame.draw.rect(screen, BLACK, exit_button)
    exit_text = font.render("Exit", True, WHITE)
    screen.blit(exit_text, (exit_button.x + 50, exit_button.y + 10))
    
    pygame.display.flip()
    clock.tick(60)
