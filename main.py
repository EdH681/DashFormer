import pygame
from math import sqrt, fabs
import time


def timer(func):
    start = time.time()
    func()
    end = time.time()
    print(end-start)


class Obstacle:
    def __init__(self, display, pos, repetitions):
        self._display = display
        self.reps = repetitions
        self._safe = True
        self.x, self.y = pos
        self.sprite = pygame.image.load("assets/block.png")

    def hitbox(self):
        return {"top": self.y, "bottom": self.y + self.sprite.get_height(),
                "left": self.x, "right": self.x + (self.sprite.get_width() * self.reps)}

    def display(self):
        sprite_width = self.sprite.get_width()
        for i in range(self.reps):
            self._display.blit(self.sprite, (self.x + (i * sprite_width), self.y))

    def safe(self):
        return self._safe


class SpikedPlatform(Obstacle):
    def __init__(self, display, pos, repetitions):
        super().__init__(display, pos, repetitions)
        self._safe = False

    def display(self):
        sprite_width = self.sprite.get_width()
        for i in range(self.reps):
            self._display.blit(self.sprite, (self.x + (i * sprite_width), self.y))

        spike_number = (self.reps * self.sprite.get_width()) // 10
        spike_start = self.x + ((self.reps * self.sprite.get_width()) - (spike_number * 10)) / 2

        for i in range(spike_number):
            points = ((spike_start + (i * 10), self.y), (spike_start + (i * 10) + 10, self.y),
                      (spike_start + (i * 10) + 5, self.y - 5))
            pygame.draw.polygon(self._display, "black", points)


class Wall(Obstacle):
    def __init__(self, display, pos, repetitions):
        super().__init__(display, pos, repetitions)
        img = pygame.image.load("assets/block.png")
        self.sprite = pygame.transform.rotate(img, 90)

    def display(self):
        sprite_height = self.sprite.get_height()
        for i in range(self.reps):
            self._display.blit(self.sprite, (self.x, self.y + (sprite_height * i)))

    def hitbox(self):
        return {"top": self.y, "bottom": self.y + (self.sprite.get_height() * self.reps),
                "left": self.x, "right": self.x + self.sprite.get_width()}


class SpikedWall(Wall):
    def __init__(self, display, pos, repetitions):
        super().__init__(display, pos, repetitions)
        self._safe = False

    def display(self):
        sprite_height = self.sprite.get_height()
        for i in range(self.reps):
            self._display.blit(self.sprite, (self.x, self.y + (sprite_height * i)))

        spike_number = (self.reps * self.sprite.get_height()) // 10
        spike_start = self.y - ((self.reps * self.sprite.get_height()) - (spike_number * 10)) / 2
        for i in range(spike_number):
            points = ((self.x, spike_start + (i * 10)), (self.x, spike_start + (i * 10) + 10),
                      (self.x - 5, spike_start + (i * 10) + 5))
            pygame.draw.polygon(self._display, "black", points)


class Player:
    def __init__(self, display: pygame.surface.Surface, grounds: list):
        self.display = display
        self.platforms = grounds
        img = pygame.image.load("assets/ball.png")
        self.sprite = pygame.transform.scale(img, (20, 20))
        self.rect = self.sprite.get_rect()
        self.rect.x = 50
        self.rect.y = 500
        self.landed = False
        self.cursor_distance = (0, 0)
        self.magnitude = 0
        self.y_ready = True
        self.x_ready = True
        self.y_vel = 0
        self.x_vel = 0
        self.direction = "RIGHT"
        self.FRICTION = 1.01
        self.PLATFORM_FRICTION = 1.5
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

    def __collision_check(self):
        max_height = self.display.get_height()
        sprite_height = self.rect.height

        if self.rect.bottom > max_height:
            self.rect.y = max_height - sprite_height
            self.landed = True
        else:
            self.landed = False

        if self.rect.top < 0:
            self.rect.y = 0
            self.y_vel = 0

        if self.rect.left < 0:
            self.rect.x = 0
            self.x_vel = 0

        if self.rect.right > self.display.get_width():
            self.rect.x = self.display.get_width() - self.rect.width
            self.x_vel = 0

        for plt in self.platforms:
            if plt.hitbox()["left"] < self.rect.centerx < plt.hitbox()["right"]:

                if plt.hitbox()["top"] < self.rect.bottom < plt.hitbox()["bottom"]:
                    self.rect.y = plt.hitbox()["top"] - sprite_height
                    self.landed = True
                    if not plt.safe():
                        self.__die()
                else:
                    self.landed = False

                if plt.hitbox()["top"] < self.rect.top < plt.hitbox()["bottom"]:
                    self.rect.y = plt.hitbox()["bottom"]
                    self.y_vel = 0

            if plt.hitbox()["top"] < self.rect.centery < plt.hitbox()["bottom"]:
                if plt.hitbox()["left"] < self.rect.left < plt.hitbox()["right"]:
                    self.rect.x = plt.hitbox()["right"]
                    self.x_vel = 0
                    if not plt.safe():
                        self.__die()
                if plt.hitbox()["left"] < self.rect.right < plt.hitbox()["right"]:
                    self.rect.x = plt.hitbox()["left"] - self.rect.width
                    self.x_vel = 0
                    if not plt.safe():
                        self.__die()

    def __x_component(self):
        friction = self.FRICTION
        if self.landed:
            friction = self.PLATFORM_FRICTION

        if fabs(self.x_vel) <= 0.1:
            self.x_vel = 0

        if self.x_ready and pygame.mouse.get_pressed()[0]:
            self.x_ready = False
            unit_vector = self.cursor_distance[0] / self.magnitude
            self.x_vel = unit_vector * self.CLICK_FORCE
        if not pygame.mouse.get_pressed()[0]:
            self.x_ready = True

        self.rect.x += self.x_vel
        self.x_vel /= friction

    def __die(self):
        pygame.time.delay(100)
        self.x_vel, self.y_vel = 0, 0
        self.rect.x = 50
        self.rect.y = 500

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
        # pygame.draw.rect(self.display, "red", self.rect, 2)

    def __force_indicator(self):
        unit_vector_x = self.cursor_distance[0] / self.magnitude
        unit_vector_y = self.cursor_distance[1] / self.magnitude
        endpoint_x = self.rect.x + (unit_vector_x * self.CLICK_FORCE * 10)
        endpoint_y = self.rect.y - (unit_vector_y * self.CLICK_FORCE * 10)
        pygame.draw.line(self.display, "red", (self.rect.x, self.rect.y), (endpoint_x, endpoint_y))

    def run(self):
        self.__calculate_cursor()
        self.__y_component()
        self.__x_component()
        self.__collision_check()
        self.__display()


if __name__ == "__main__":
    size = window_width, window_height = 1500, 750
    pygame.init()
    win = pygame.display.set_mode(size)
    player_display = pygame.Surface(size)
    clock = pygame.time.Clock()

    objects = [
        Obstacle(win, (0, 600), 10),
        SpikedPlatform(win, (100, 300), 4),
        Wall(win, (900, 100), 10),
        SpikedWall(win, (1200, 200), 5)
    ]

    player = Player(win, objects)

    # mainloop
    running = True
    bg_image = pygame.image.load("assets/backdrop.png").convert()
    bg_image = pygame.transform.scale(bg_image, (window_width, window_height))
    while running:
        start = time.time()
        win.blit(bg_image, (0, 0))
        player.run()
        for obj in objects:
            obj.display()
        pygame.display.update()

        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

        end = time.time()
        print(end-start)
