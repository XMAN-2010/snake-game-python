import pyfirmata

from sre_parse import WHITESPACE
import pygame
from pygame.locals import*

import os
import sys
import random 
from time import sleep
 

height = 600
width = 800

GRID_SIZE = 20
GRID_WIDTH = width / GRID_SIZE
GRID_HEIGHT = height / GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

WHITE = (255, 255, 255)
ORANGE = (250, 150, 0)
GRAY = (100, 100, 100)
MY_FAVORITE_COLOR = (0, 237, 255)

pygame.mixer.init()

class Snake():
    def __init__(self):
        self.create()

    def create(self): 
        self.length = 2
        self.position = [(int(width / 2), int(height / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def control(self, xy):
        if (xy[0] * -1, xy[1] * -1) == self.direction:
            return
        else:
            self.direction = xy
    
    def move(self):
        cur = self.position[0]
        x,y = self.direction
        new = (cur[0] + (x * GRID_SIZE), (cur[1] + (y * GRID_SIZE)))
        if new in self.position[2:]:
            sleep(1)
            self.create()
        elif new[0] < 0 or new[0] >= width or \
             new[1] < 0 or new[1] >= height:
             sleep(1)
             self.create()
        else:
            self.position.insert(0,new)
            if len(self.position) > self.length:
                self.position.pop()
    def eat(self):
        self.length += 1

    def draw(self, screen):
        red, green, blue = 50 / (self.length -1), 150, 150 / (self.length -1)
        for i,p in enumerate(self.position):
            color = (100+red*i, green, blue*i)
            rect = pygame.Rect((p[0],p[1]),(GRID_SIZE,GRID_SIZE))
            pygame.draw.rect(screen,color,rect)


class feed():
    def __init__(self):
        self.position = (0, 0)
        self.color = MY_FAVORITE_COLOR
        self.create()
    def create(self):
        x = random.randint(0, GRID_WIDTH -1)
        y = random.randint(0, GRID_HEIGHT -1)
        self.position = x * GRID_SIZE, y * GRID_SIZE
    def draw(self, screen):
        rect = pygame.Rect((self.position[0], self.position[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.color, rect)

eat_sound = pygame.mixer.Sound("EATING SOUND.ogg")

class Game():
    def __init__(self):
        self.snake = Snake()
        self.feed = feed()
        self.board = pyfirmata.Arduino('COM3')
        self.board.get_pin('d:13:i')
        self.board.get_pin('d:12:i')
        self.board.get_pin('d:11:i')
        self.board.get_pin('d:10:i')
        pyfirmata.util.Iterator(self.board).start()
        self.speed = 5

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.control(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.control(DOWN)
                elif event.key == pygame.K_RIGHT:
                    self.snake.control(RIGHT)
                elif event.key == pygame.K_LEFT:
                    self.snake.control(LEFT)
        return False
    
    def detect_button(self):
        if self.board.digital[13].read():
            self.snake.control(RIGHT)
        if self.board.digital[12].read():
            self.snake.control(DOWN)
        if self.board.digital[11].read():
            self.snake.control(UP)
        if self.board.digital[10].read():
            self.snake.control(LEFT)


    def run_logic(self):
        self.snake.move()
        self.detect_button()
        self.check_eat(self.snake, self.feed)
        self.speed = (5 + self.snake.length - 1)
    
    
    def check_eat(self, snake, feed):
        if snake.position[0] == feed.position:
            pygame.mixer.Sound.play(eat_sound)
            snake.eat()
            feed.create()
    def display_frame(self, screen):
        screen.fill(GRAY)
        self.snake.draw(screen)
        self.feed.draw(screen)
        screen.blit(screen, (0, 0))

pygame.mixer.music.load('BGM.ogg')
pygame.mixer.music.play()

def main():
    pygame.init()
    pygame.display.set_caption("Snake Game")
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    game = Game()
    done = False
    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        pygame.display.flip()
        clock.tick(game.speed)
    pygame.quit()



main()