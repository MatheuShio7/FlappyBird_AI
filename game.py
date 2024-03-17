import pygame
import os
import random

screen_width = 500
screen_high = 800

pipe_image = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
base_image = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
background_image = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
bird_images = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
game_font = pygame.font.SysFont('arial', 50)

class Bird:
    images = bird_images

    max_rotation = 25
    speed_rotation = 20
    animation_time = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.high = self.y
        self.time = 0
        self.count_image = 0
        self.image = self.images[0]

    def jump(self):
        self.speed = -10.5
        self.tempo = 0
        self.high = self.y

    def move(self):
        #displacement calculation
        self.time += 1
        displacement = 1.5 * (self.time ** 2) + self.speed * self.time

        #restrict displacement 
        if displacement > 16: 
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y += displacement

        #bird angle
        if displacement < 0 or self.y < (self.high + 50):
            if self.angle < self.max_rotation:
                self.angle = self.max_rotation
        else:
            if self.angle > -90:
                 self.angle -= self.speed_rotation

    def draw(self, screen):
        #which image to use
        self.count_image += 1

        if self.count_image < self.animation_time:
            self.image = self.images[0]
        elif self.count_image < self.animation_time * 2:
            self.image = self.images[1]
        elif self.count_image < self.animation_time * 3:
            self.image = self.images[2]
        elif self.count_image < self.animation_time * 4:
            self.image = self.images[1]
        elif self.count_image >= self.animation_time * 4 + 1:
            self.image = self.images[0]
            self.count_image = 0

        #if the bird is falling dont flap its wing
        if self.angle <= 80:
            self.image = self.images[1]
            self.count_image = self.animation_time * 2

        #draw image
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        image_center_posicion = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_image.get_rect(center=image_center_posicion)
        screen.blit(rotated_image, rectangle.topleft)

    def get_mask(self):
        pygame.mask.from_surface(self.image)


class Pipe:
    pass


class Base:
    pass