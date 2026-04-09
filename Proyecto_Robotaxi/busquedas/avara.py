# busquedas/avara.py
import heapq
import time
from modelos import Node
from .utilidades import is_goal, expand, reconstruct_path, find_positions, manhattan_dist


def buscar(world_matrix):
    # Find key positions on the map
    start, destinations, passengers = find_positions(world_matrix)

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
    nid = 0
    heapq.heappush(frontier, (heuristic(root, destinations), nid, root))

    expanded_nodes = 0
    start_time = time.time()

    # Main search loop
    while frontier:
        # Pop node with the lowest heuristic value (greedy choice)
        h_value, _, current_node = heapq.heappop(frontier)

        expanded_nodes += 1

        # Check if the current node satisfies the goal condition:
        # vehicle at destination AND no remaining passengers
        if is_goal(current_node, destinations):
            end_time = time.time()
            path = reconstruct_path(current_node)
            return path, expanded_nodes, current_node.depth, current_node.cost, (end_time - start_time)

        # Expand current node: generate all valid child nodes
        children = expand(current_node, world_matrix)

        # Insert children into the priority queue ordered by h(n)
        for child in children:
            nid += 1
            heapq.heappush(frontier, (heuristic(child, destinations), nid, child))

    # If the frontier is exhausted without finding a solution
    time_elapsed = time.time() - start_time
    return None, expanded_nodes, current_node.depth, current_node.cost, time_elapsed


# Heuristic function 
""" Greedy heuristic h(n):
Estimates the remaining cost from the current node to the goal.

Strategy (same as heuristic from A*):
- Find the passenger farthest from the vehicle.
- Find the closest destination to farthers passenger
- h(n) = dist(vehicle -> farthest passenger) + dist(farthest passenger -> closest destination)
- If no passengers remain, h(n) = dist(vehicle -> closest destination)

This is admissible and guides the search greedily toward the goal."""
def heuristic(node, destinations):

    vehicle_pos, passengers = node.state

    if passengers and destinations:
        # Compute distance from vehicle to each remaining passenger
        dist_to_passengers = [(manhattan_dist(vehicle_pos, p), p) for p in passengers]
        dist_to_passengers.sort()

        # Select the farthest passenger as the bottleneck
        farthest_dist_p, farthest_psg = dist_to_passengers[-1]

        # Compute distance from farthest passenger to destinations
        dist_to_dests = [(manhattan_dist(farthest_psg, d), d) for d in destinations]

        # Select the closest destination
        closest_dist_d, closest_dest = dist_to_dests[0]

        # h(n) = distance to farthest passenger + distance from that passenger to destination
        return farthest_dist_p + closest_dist_d
    elif destinations:
        # All passengers picked up: only need to reach the closest destination
        dist_to_dests = [(manhattan_dist(vehicle_pos, d), d) for d in destinations]

        # Select the closest destination
        closest_dist_d, closest_dest = dist_to_dests[0]

        return closest_dist_d
    else:
        return 0
