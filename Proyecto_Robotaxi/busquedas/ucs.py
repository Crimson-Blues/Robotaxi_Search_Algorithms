# busquedas/ucs.py
import heapq
import time
from modelos import Node
from busquedas.utilidades import find_positions, expand, is_goal, reconstruct_path


def buscar(world_matrix):

    # Extract initial key positions
    start, destination, passengers = find_positions(world_matrix)

    # Initial state and node (root)
    initial_state = (start, passengers)

    root = Node(
        state=initial_state,
        p=None,
        rator=None,
        depth=0,
        cost=0
    )

    # Priority queue (cost, nid, node)
    nid = 0 # Node id (incremental simple counter) for tie breaks
    frontier = []
    heapq.heappush(frontier, (0, nid, root))

    expanded_nodes = 0

    start_time = time.time()
    while frontier:
        current_cost, _, current_node = heapq.heappop(frontier)
        expanded_nodes += 1

        # Goal verification
        if is_goal(current_node, destination):
            end_time = time.time()

            path = reconstruct_path(current_node)
            depth = current_node.depth
            total_cost = current_node.cost

            return path, expanded_nodes, depth, total_cost, (end_time - start_time)

        # Else: node expansion
        children = expand(current_node, world_matrix)

        for child in children:
            nid += 1 # Increment node id
            heapq.heappush(frontier, (child.cost, nid, child))

    # In case no solution is found
    time_elapsed = time.time() - start_time
    return None, expanded_nodes, current_node.depth, current_node.cost, time_elapsed