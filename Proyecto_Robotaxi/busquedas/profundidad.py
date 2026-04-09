# busquedas/profundidad.py
from collections import deque
import time
from modelos import Node
from .utilidades import is_goal, expand, reconstruct_path, find_positions

def buscar(world_matrix): 
    # Initial values identical to Breadth First Search (Búsqueda preferente por amplitud)
    start, destinations, initial_passengers = find_positions(world_matrix)
    initial_state = (start, initial_passengers)

    root_node = Node(state=initial_state)

    # Use of list/dequeue as Stack (LIFO)
    stack = deque([root_node])

    expanded_nodes = 0
    start_time = time.time()

    while stack:
        # KEY DIFFERENCE: Using pop() to extract LAST inserted element
        current_node = stack.pop()

        expanded_nodes += 1

        # Goal verification
        if is_goal(current_node, destinations):
            time_elapsed = time.time() - start_time
            path = reconstruct_path(current_node)
            return path, expanded_nodes, current_node.depth, current_node.cost, time_elapsed

        # Children expansion
        children = expand(current_node, world_matrix)

        for child in children:
            # By adding and extracting from the right side deepest nodes are explored first
            stack.append(child)

    # In case there's no solution
    time_elapsed = time.time() - start_time
    return None, expanded_nodes, current_node.depth, current_node.cost, time_elapsed