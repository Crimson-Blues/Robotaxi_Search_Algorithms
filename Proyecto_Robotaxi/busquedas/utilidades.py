# busquedas/utilidades.py
from modelos import Node

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
pass
    
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
pass

def is_goal(state, destination):
    current_position = state[0]
    remaining_passengers = state[1]
    return current_position == destination and len(remaining_passengers) == 0
pass

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
pass

def reconstruct_path(goal_node):
    path = []
    current_node = goal_node
    while current_node.p is not None:
        path.append(current_node.rator)
        current_node = current_node.p
    path.reverse()
    return path
pass
