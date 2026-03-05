#Importations
from collections import namedtuple
import time
import sys, os
import numpy as np
import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum

class Taxi:
    def __init__(self, x_pos=0, y_pos=0):
        self.passengers = 0
        self.x_pos = x_pos
        self.y_pos = y_pos

    def move(self, movement):
        if movement and movement is Movement:
            self.x_pos += movement.x
            self.y_pos += movement.y

    def pick_up_passenger(self):
        self.passengers += 1


class Movement:
    def __init__(self, x_mov=0, y_mov=0):
        self.x_mov = x_mov
        self.y_mov = y_mov

class Board:
    def __init__(self, width = 3, height = 3, state = []):
        self.width = width
        self.height = height
        self.state = state
        if not state:
            for i in range(width):
                self.state.append([0]*height)
        print(self.state)



class Node:
    def __init__(self, state = [], p = None, rator = None, depth = 0):
        self.state = state
        self.p = p
        self.rator = rator
        self.depth = depth
        self.children = []



class Search_Tree:
    def __init__(self, root = Node()):
        self.root = root


#Helper graphing functions

def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """ Returns surface with text written on """
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


class UIElement(Sprite):
    """ An user interface element that can be added to a surface """

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            bg_rgb (background colour) - tuple (r, g, b)
            text_rgb (text colour) - tuple (r, g, b)
        """
        self.mouse_over = False  # indicates if the mouse is over the element

        # create the default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # create the image that shows when mouse is over the element
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # add both images and their rects to lists
        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        # calls the init method of the parent sprite class
        super().__init__()

    # properties that vary the image and its rect when the mouse is over the element
    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
        else:
            self.mouse_over = False

    def draw(self, surface):
        """ Draws element onto a surface """
        surface.blit(self.image, self.rect)

#Frontend loop:
def main():
    #Color definitions:
    BLUE = (106, 159, 181)
    WHITE = (255, 255, 255)

    pygame.init()

    screen = pygame.display.set_mode((800, 600))

    # create a ui element
    uielement = UIElement(
        center_position=(400, 400),
        font_size=30,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text="Hello World",
    )

    # main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                return 
        screen.fill(BLUE)

        uielement.update(pygame.mouse.get_pos())
        uielement.draw(screen)
        pygame.display.flip()


#Run main function
if __name__ == "__main__":
    main()