import pygame
import sys
from math import sqrt, sin, cos


class Player:
    def __init__(self, display: pygame.surface.Surface, colour="white", radius=10):
        self.display = display
        self.colour = colour
        self.radius = radius
        self.landed = False
        self.cursor_distance = 0
        self.magnitude = 0
        self.y_ready = True
        self.x_ready = True
        self.x = 200
        self.y = 300
        self.y_vel = 0
        self.x_vel = 0
        self.direction = "RIGHT"
        self.FRICTION = 1.01
        self.GRAVITY = 0.25
        self.CLICK_FORCE = 10

    def __y_component(self):
        self.y -= self.y_vel
        self.y_vel -= self.GRAVITY

        if self.y_ready and pygame.mouse.get_pressed()[0]:
            self.y_ready = False
            self.landed = False
            unit_vector = self.cursor_distance[1]/self.magnitude
            self.y_vel = unit_vector * self.CLICK_FORCE

        if not pygame.mouse.get_pressed()[0]:
            self.y_ready = True

        if self.landed:
            self.y_vel = 0

    def __x_component(self):

        if self.x_ready and pygame.mouse.get_pressed()[0]:
            self.x_ready = False
            unit_vector = self.cursor_distance[0]/self.magnitude
            self.x_vel = unit_vector * self.CLICK_FORCE
        if not pygame.mouse.get_pressed()[0]:
            self.x_ready = True

        self.x += self.x_vel
        self.x_vel /= self.FRICTION

        if self.landed and self.x_vel < 0.005:
            self.x_vel = 0

    def __calculate_cursor(self):
        cursor_x, cursor_y = pygame.mouse.get_pos()
        self.cursor_distance = (cursor_x - self.x, self.y - cursor_y)

        if self.cursor_distance[0] > 0:
            self.direction = "RIGHT"
        else:
            self.direction = "LEFT"

        self.magnitude = sqrt((cursor_x - self.x)**2 + (cursor_y - self.y)**2)

    def __display(self):
        position = (self.x, self.y)
        pygame.draw.circle(self.display, self.colour, position, self.radius)

    def __force_indicator(self):
        unit_vector_x = self.cursor_distance[0] / self.magnitude
        unit_vector_y = self.cursor_distance[1] / self.magnitude
        endpoint_x = self.x + (unit_vector_x * self.CLICK_FORCE * 10)
        endpoint_y = self.y - (unit_vector_y * self.CLICK_FORCE * 10)
        print(endpoint_y)
        pygame.draw.line(self.display, "red", (self.x, self.y), (endpoint_x, endpoint_y))

    def run(self):
        self.__calculate_cursor()
        self.__y_component()
        self.__x_component()
        self.__display()


class Arena:
    def __init__(self):
        self.grid = None

    def __generate(self):
        pass


size = width, height = 900, 900
pygame.init()
win = pygame.display.set_mode(size)
clock = pygame.time.Clock()

player = Player(win, radius=10)

# mainloop
running = True


while running:

    win.fill("black")
    player.run()
    pygame.display.update()

    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()