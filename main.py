import pygame
import sys
from math import sqrt, sin, cos


class Player:
    def __init__(self, display: pygame.surface.Surface):
        self.display = display
        self.sprite = pygame.image.load("assets/ball.png")
        self.rect = self.sprite.get_rect()
        self.rect.x = 200
        self.rect.y = 300
        self.landed = False
        self.cursor_distance = 0
        self.magnitude = 0
        self.y_ready = True
        self.x_ready = True
        self.y_vel = 0
        self.x_vel = 0
        self.direction = "RIGHT"
        self.FRICTION = 1.01
        self.GRAVITY = 0.25
        self.TERMINAL = -7
        self.CLICK_FORCE = 10

    def __y_component(self):
        self.rect.y -= self.y_vel
        if self.y_vel > self.TERMINAL:
            self.y_vel -= self.GRAVITY
        else:
            self.y_vel = self.TERMINAL

        if self.y_ready and pygame.mouse.get_pressed()[0]:
            self.y_ready = False
            self.landed = False
            unit_vector = self.cursor_distance[1] / self.magnitude
            self.y_vel = unit_vector * self.CLICK_FORCE

        if not pygame.mouse.get_pressed()[0]:
            self.y_ready = True

        max_height = self.display.get_height()
        sprite_height = self.rect.height

        if self.rect.bottom > max_height:
            self.rect.y = max_height - self.rect.height

    def __x_component(self):

        if self.x_ready and pygame.mouse.get_pressed()[0]:
            self.x_ready = False
            unit_vector = self.cursor_distance[0] / self.magnitude
            self.x_vel = unit_vector * self.CLICK_FORCE
        if not pygame.mouse.get_pressed()[0]:
            self.x_ready = True

        self.rect.x += self.x_vel
        self.x_vel /= self.FRICTION

    def __calculate_cursor(self):
        cursor_x, cursor_y = pygame.mouse.get_pos()
        self.cursor_distance = (cursor_x - self.rect.x, self.rect.y - cursor_y)

        if self.cursor_distance[0] > 0:
            self.direction = "RIGHT"
        else:
            self.direction = "LEFT"

        self.magnitude = sqrt((cursor_x - self.rect.x) ** 2 + (cursor_y - self.rect.y) ** 2)

    def __display(self):
        self.display.blit(self.sprite, self.rect.topleft)

    def __force_indicator(self):
        unit_vector_x = self.cursor_distance[0] / self.magnitude
        unit_vector_y = self.cursor_distance[1] / self.magnitude
        endpoint_x = self.rect.x + (unit_vector_x * self.CLICK_FORCE * 10)
        endpoint_y = self.rect.y - (unit_vector_y * self.CLICK_FORCE * 10)
        print(endpoint_y)
        pygame.draw.line(self.display, "red", (self.rect.x, self.rect.y), (endpoint_x, endpoint_y))

    def run(self):
        self.__calculate_cursor()
        self.__y_component()
        self.__x_component()
        self.__display()


size = window_width, window_height = 900, 900
pygame.init()
win = pygame.display.set_mode(size)
clock = pygame.time.Clock()

player = Player(win)

# mainloop
running = True

while running:

    win.fill("white")
    player.run()
    pygame.display.update()

    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
