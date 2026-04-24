# modelos.py
from turtle import update
from utilities import create_surface_with_text
from pygame.sprite import Sprite
import pygame


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
    def __init__(self, state = [], p = None, rator = None, depth = 0, cost = 0):
        self.state = state
        self.p = p
        self.rator = rator
        self.depth = depth
        self.children = []
        self.cost = cost



class Search_Tree:
    def __init__(self, root = Node()):
        self.root = root

class UIElement(Sprite):
    """ An user interface element that can be added to a surface """

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, text_style=None, alt_text = None, alt_flag = None):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            bg_rgb (background colour) - tuple (r, g, b)
            text_rgb (text colour) - tuple (r, g, b)
        """
        self.mouse_over = False  # indicates if the mouse is over the element
        self._visibility = True # Makes element visible or not
        self.alt_flag = alt_flag # Allows alternate text for buttons
        self.text = text # Store text value

        # create the default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb, text_style=text_style
        )

        # create the image that shows when mouse is over the element
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb, text_style=text_style
        )

        if alt_text:
            default_image_alt = create_surface_with_text(
            text=alt_text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb, text_style=text_style
            )
            highlighted_image_alt = create_surface_with_text(
                text=alt_text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb, text_style=text_style
            )

            self.alt_images = [default_image_alt, highlighted_image_alt]
            self.alt_rects = [
                default_image_alt.get_rect(center=center_position),
                highlighted_image_alt.get_rect(center=center_position),
            ]

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
        if self.alt_flag and self.alt_flag() and self.alt_images:
            return self.alt_images[1] if self.mouse_over else self.alt_images[0]
        else:
            return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        if self.alt_flag and self.alt_flag() and self.alt_rects:
            return self.alt_rects[1] if self.mouse_over else self.alt_rects[0]
        else:
            return self.rects[1] if self.mouse_over else self.rects[0]

    @property
    def visibility(self):
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        self._visibility = value

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
        else:
            self.mouse_over = False
        

    def set_visibility(self, value):
        self.visibility = value

    def draw(self, surface):
        # Draws element onto a surface if visibility is set to true
        if self._visibility:
            surface.blit(self.image, self.rect)





            