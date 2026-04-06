# busquedas/avara.py
import heapq
import time
from modelos import Node
from .utilidades import is_goal, expand, reconstruct_path, find_positions, manhattan_dist


def buscar(world_matrix):
    # Find key positions on the map
    start, destination, passengers = find_positions(world_matrix)

    # Initial state: vehicle start position + set of remaining passengers
    initial_state = (start, passengers)

    # Root node of the search tree (depth=0, cost=0)
    root = Node(
        state=initial_state,
        p=None,
        rator=None,
        depth=0,
        cost=0
    )

    # Priority queue: nodes ordered by heuristic value h(n) only
    # (Greedy Best-First Search ignores the actual accumulated cost g(n))
    # Each entry: (h(n), tie_breaker, node)
    frontier = []
    heapq.heappush(frontier, (heuristic(root, destination), id(root), root))

    # Track visited states to avoid re-expanding the same state
    visited = set()

    expanded_nodes = 0
    start_time = time.time()

    # Main search loop
    while frontier:
        # Pop node with the lowest heuristic value (greedy choice)
        h_value, _, current_node = heapq.heappop(frontier)

        # Skip already-visited states (lazy deletion approach)
        if current_node.state in visited:
            continue

        visited.add(current_node.state)
        expanded_nodes += 1

        # Check if the current node satisfies the goal condition:
        # vehicle at destination AND no remaining passengers
        if is_goal(current_node, destination):
            end_time = time.time()
            path = reconstruct_path(current_node)
            return path, expanded_nodes, current_node.depth, current_node.cost, (end_time - start_time)

        # Expand current node: generate all valid child nodes
        children = expand(current_node, world_matrix)

        # Insert children into the priority queue ordered by h(n)
        for child in children:
            if child.state not in visited:
                heapq.heappush(frontier, (heuristic(child, destination), id(child), child))

    # If the frontier is exhausted without finding a solution
    end_time = time.time()
    return None, expanded_nodes, 0, 0, (end_time - start_time)


# Heuristic function 

def heuristic(node, destination):
    """ Greedy heuristic h(n):
    Estimates the remaining cost from the current node to the goal.

    Strategy (mirrors heuristic_min from A*):
    - Find the passenger farthest from the vehicle.
    - h(n) = dist(vehicle -> farthest passenger) + dist(farthest passenger -> destination)
    - If no passengers remain, h(n) = dist(vehicle -> destination)

    This is admissible and guides the search greedily toward the goal."""

    vehicle_pos, passengers = node.state

    if passengers:
        # Compute distance from vehicle to each remaining passenger
        dist_to_passengers = [(manhattan_dist(vehicle_pos, p), p) for p in passengers]
        dist_to_passengers.sort()

        # Select the farthest passenger as the bottleneck
        farthest_dist, farthest_psg = dist_to_passengers[-1]

        # h(n) = distance to farthest passenger + distance from that passenger to destination
        return farthest_dist + manhattan_dist(farthest_psg, destination)
    else:
        # All passengers picked up: only need to reach the destination
        return manhattan_dist(vehicle_pos, destination)
