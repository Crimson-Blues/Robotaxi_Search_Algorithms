# busquedas/amplitud.py
from collections import deque
import time
from modelos import Node
from .utilidades import is_goal, expand, reconstruct_path, find_positions

def buscar(world_matrix): 
    
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
    return path, expanded_nodes, depth, cost, time_elapsed