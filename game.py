import pygame
import os 
import random
import neat

ai_playing = True
generation = 0

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
        self.time = 0
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
        if self.angle <= -80:
            self.image = self.images[1]
            self.count_image = self.animation_time * 2

        #draw image
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        image_center_posicion = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_image.get_rect(center=image_center_posicion)
        screen.blit(rotated_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    distance = 200
    speed = 5

    def __init__(self, x):
        self.x = x
        self.high = 0
        self.position_top_pipe = 0
        self.position_base_pipe = 0
        self.top_pipe = pygame.transform.flip(pipe_image, False, True)
        self.base_pipe = pipe_image
        self.passed = False
        self.set_high()

    def set_high(self):
        self.high = random.randrange(50, 450)
        self.position_top_pipe = self.high - self.top_pipe.get_height()
        self.position_base_pipe = self.high + self.distance 
    
    def move(self):
        self.x -= self.speed

    def draw(self, screen):
        screen.blit(self.top_pipe, (self.x, self.position_top_pipe))
        screen.blit(self.base_pipe, (self.x, self.position_base_pipe))     

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.top_pipe)
        base_mask = pygame.mask.from_surface(self.base_pipe)

        top_distance = (self.x - bird.x, self.position_top_pipe - round(bird.y))
        base_distance = (self.x - bird.x, self.position_base_pipe - round(bird.y))

        top_point = bird_mask.overlap(top_mask, top_distance)
        base_point = bird_mask.overlap(base_mask, base_distance)

        if top_point or base_point:
            return True
        else:
            return False


class Base:
    speed = 5
    base_width = base_image.get_width()
    image = base_image

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.base_width

    def move(self):
        self.x1 -= self.speed
        self.x2 -= self.speed

        if self.x1 + self.base_width < 0:
            self.x1 = self.x2 + self.base_width

        if self.x2 + self.base_width < 0:
            self.x2 = self.x1 + self.base_width

    def draw(self,screen):
        screen.blit(self.image, (self.x1, self.y))
        screen.blit(self.image, (self.x2, self.y))


def draw_screen(screen, birds, pipes, base, score):
    screen.blit(background_image, (0, 0))

    for bird in birds:
        bird.draw(screen)
    
    for pipe in pipes:
        pipe.draw(screen)

    text = game_font.render(f'Score: {score}', 1, (255, 255, 255))
    screen.blit(text, (screen_width - 10 - text.get_width(), 10))

    if ai_playing:
        text = game_font.render(f'Gen: {generation}', 1, (255, 255, 255))
        screen.blit(text, (10, 10))
    
    base.draw(screen)

    pygame.display.update()


#fitness function 
def main(genomes, config):
    global generation
    generation += 1

    if ai_playing:
        redes = []
        genome_list = []
        birds = []
        for _, genome in genomes:
            #criando a rede neural
            rede = neat.nn.FeedForwardNetwork.create(genome, config) 
            redes.append(rede)

            genome.fitness = 0 #pontuação da rede neural
            genome_list.append(genome)

            #criando cada pássaro
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]

    base = Base(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((screen_width, screen_high))
    score = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if not ai_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.jump()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].top_pipe.get_width()):
                pipe_index = 1
        else:
            running = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            genome_list[i]

        base.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            
            pipe.move()
            if pipe.x + pipe.top_pipe.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > base.y or bird.y < 0:
                birds.pop(i)

    
        draw_screen(screen, birds, pipes, base, score)
    
#se este for o arquivo que você está rodando rode isso:
#caso este arquivo está sendo inportado não rode isso:
if __name__ == '__main__':
    main()