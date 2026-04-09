# busquedas/amplitud.py
from collections import deque
import time
from modelos import Node
from .utilidades import is_goal, expand, reconstruct_path, find_positions

def buscar(world_matrix): 
    # Initilization of key positions (Vehicle start position, destination, passenger positions)
    start, destination, initial_passengers = find_positions(world_matrix)

    # Creation of root node with initial state
    initial_state = (start, initial_passengers)
    root_node = Node(state=initial_state)

    # Double sided queue for nodes yet to be expanded
    queue = deque([root_node])

    expanded_nodes = 0
    start_time = time.time()

    while queue:
        # Select left most node at queue to expand
        current_node = queue.popleft()

        # Count as expanded when checking if it is the goal
        expanded_nodes += 1

        if is_goal(current_node, destination):
            time_elapsed = time.time() - start_time
            path = reconstruct_path(current_node)
            return path, expanded_nodes, current_node.depth, current_node.cost, time_elapsed

        # If it's not the goal, create its children
        children = expand(current_node, world_matrix)

        #Append all children to the end of expanding queue
        for child in children:
            queue.append(child)

    # If the queue empties without finding the goal
    time_elapsed = time.time() - start_time
    return None, expanded_nodes, current_node.depth, current_node.cost, time_elapsed