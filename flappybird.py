import pygame
import time
import os
import random

pygame.font.init()

# Dimensions of the screen
WIN_WIDTH = 500 
WIN_HEIGHT = 800 

# this gets the bird images to animate later on its stored in a list (here scale increases the size and load loads)
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

# gets the bg, base and pipe image respectively
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("Consolas", 27)

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25   # tilt of the bird
    ROT_VEL = 20        # how much rotation in each frame
    ANIMATION_TIME = 5  # how long it takes for each animation

    def __init__(self, x, y): # starting position
        self.x = x
        self.y = y
        self.tilt = 0                 # how much is the image tilting
        self.tick_count = 0           # for the physics of bird ie jump and stuff
        self.vel = 0                  # cause bird is stationary
        self.height = self.y 
        self.img_count = 0            # to know which image are we using
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -9                   # to jump upwards
        self.tick_count = 0             # count of last jump
        self.height = self.y            # counts where the bird started to jump from or moving from

    def move(self):             #every frame to move the bird
        self.tick_count += 1            # a frame went by

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2             # formula to calculate the displacement ie how many pixels to move up or down
                                                                                # so this formula basically makes u get that arc like goes down down 
                                                                                # down down and then up up up 

        if d >= 16:                                                             # if you are moving down 16 pixels 
            d = 16

        if d < 0:                                                               # if you going up go thodu more up (jump higher)
            d -= 2                                                              # change this number to adjust jump 

        self.y = self.y + d                                                     #changes Y position based on your displacement 

        if d < 0 or self.y < self.height + 50:                                  # if you are moving up or your position is above ur current position you wouldnt tilt downwards 
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:                                                                   # if the birdy is moving down it would seem its going down faster and faster like nose diving
            if self.tilt > -90: 
                self.tilt -= self.ROT_VEL
    
    def draw(self,win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:                                # checking which image should be shown based on the current image; 
                                                                                # so if the image count is less then "5" we show the 1st image
                                                                                # if the image count is less than "10" we show the second if the img count is less 
                                                                                # than "15" we show the third image and so on
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:                            # here if the bird is tilted 90 degree downwards we dont want it to be flapping ie changing the image
            self.img = self.IMGS[1]                     # it shows nose dive
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):                         # to gt collisions (shits very complicated but basically uses pygame featurs)
        return pygame.mask.from_surface(self.img)
    
class Pipe:
    GAP = 200                                   # space bewteen the pipes
    VEL = 5                                     # since all the objects move; this is the speed at which the pipes move behind towards the bird

    def __init__(self, x) -> None:              # using only "x" cause the height of the tubes are gonna be random everytime
        self.x = x
        self.height = 0 

        self.top = 0
        self.bottom = 0 
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)  # the pipe image is only of the bottom one so this flips it and stores it 
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False                     # checks if the bird has passed the pipe
        self.set_height()                       # define the top, bottom of the pipe, the height and where does the gap occur

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height() # complicated stuff to basically calculate the top pipe's left hand conrner I.E the positioin of the pipe
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):                                        # in simple words HITBOXs
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))            # offset is basically how far the hitboxs are
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)             # if they dont collide we get "none"
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:                                              # if any of these collids we get to know they collided 
            return True
        
        return False
    
class Base:
    VEL = 5                             # same as pipe
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y) -> None:
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0,0))                         # blit basically means draw

    for pipe in pipes:
        pipe.draw(win)


    text = STAT_FONT.render("Score: " + str(score), 1,(0, 0, 0))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw(win)
    pygame.display.update()

def main():
    bird = Bird(230,350)
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()                                 # so basically this give the while loop a tick rate so the bird doesnt fall very fast 
    
    score = 0
    run = True
    
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()                                 # Allows the bird to jump using space


        bird.move()
        base.move()

        # Check if bird hits the ground (base)
        if bird.y + bird.img.get_height() >= 730:
            run = False


        # Generate new pipes and check collisions
        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(bird):
                run = False

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
        
        for r in rem:
            pipes.remove(r)

        draw_window(win, bird, pipes, base, score)

    pygame.quit()
    quit()

main()

if __name__ == "__main__":
    main()
