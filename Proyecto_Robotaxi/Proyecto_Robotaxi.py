#Importations
from collections import namedtuple, deque
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

# Algorithm Logic 
def read_world(file_path):
    world_matrix = []
    try:
        with open(file_path, 'r') as file: 
            for line in file: 
                text_row = line.strip().split() 
                if text_row: 
                    int_row = [int(number) for number in text_row] 
                    world_matrix.append(int_row) 
        return world_matrix
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta {file_path}")
        return None


def find_positions(map_matrix):
    start = None
    destination = None
    passengers = set()
    for row in range(len(map_matrix)):
        for col in range(len(map_matrix[row])):
            if map_matrix[row][col] == 2:
                start = (row, col)
            elif map_matrix[row][col] == 5:
                destination = (row, col)
            elif map_matrix[row][col] == 4:
                passengers.add((row, col))
    return start, destination, frozenset(passengers)


def is_goal(state, destination):
    current_position = state[0]
    remaining_passengers = state[1]
    return current_position == destination and len(remaining_passengers) == 0


def expand(current_node, world_matrix):
    children = []
    # Unpack the state
    (current_row, current_col), remaining_passengers = current_node.state
    
    # dr (delta row), dc (delta col), rator (operator)
    movements = [(-1, 0, 'Up'), (1, 0, 'Down'), (0, -1, 'Left'), (0, 1, 'Right')]
    
    for dr, dc, rator in movements:
        new_row = current_row + dr
        new_col = current_col + dc
        
        if 0 <= new_row < len(world_matrix) and 0 <= new_col < len(world_matrix[0]):            
            if world_matrix[new_row][new_col] != 1:
                movement_cost = 7 if world_matrix[new_row][new_col] == 3 else 1
                new_cost = current_node.cost + movement_cost
                
                new_passengers = set(remaining_passengers)
                if (new_row, new_col) in new_passengers:
                    new_passengers.remove((new_row, new_col))
                
                new_state = ((new_row, new_col), frozenset(new_passengers))
                
                new_node = Node(
                    state=new_state,
                    p=current_node,
                    rator=rator,
                    depth=current_node.depth + 1,
                    cost=new_cost
                )
                children.append(new_node)
                
    return children


def reconstruct_path(goal_node):
    path = []
    current_node = goal_node
    while current_node.p is not None:
        path.append(current_node.rator)
        current_node = current_node.p
    path.reverse()
    return path


def preferred_search_amplitude(world_matrix):
    start, destination, initial_passengers = find_positions(world_matrix)
    initial_state = (start, initial_passengers)

    root_node = Node(state=initial_state)

    queue = deque([root_node])
    visited = set()
    visited.add(initial_state)

    expanded_nodes = 0
    start_time = time.time()

    while queue:
        current_node = queue.popleft()

        # Count as expanded when checking if it is the goal
        expanded_nodes += 1

        if is_goal(current_node.state, destination):
            time_elapsed = time.time() - start_time
            path = reconstruct_path(current_node)
            return path, expanded_nodes, current_node.depth, current_node.cost, time_elapsed

        # If it's not the goal, create its children
        children = expand(current_node, world_matrix)

        for child in children:
            # Validate visited nodes to avoid cycles
            if child.state not in visited:
                visited.add(child.state)
                queue.append(child)

    # If the queue empties without finding the goal
    return None, expanded_nodes, 0, 0, 0

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
    file_path = 'Prueba1.txt'
    map_matrix = read_world(file_path)
    
    if map_matrix:
        path, expanded_nodes, depth, cost, calc_time = preferred_search_amplitude(map_matrix)
        
        if path is not None:
            print("Solución encontrada")
            print("Ruta: ", path)
            print("Nodos expandidos: ", expanded_nodes)
            print("Profundidad del árbol: ", depth)
            print("Costo total de la ruta: ", cost)
            print("Tiempo de cómputo: ", calc_time, "segundos")
        else:
            print("\nNo se encontró una solución")
            print("Nodos expandidos: ", expanded_nodes)