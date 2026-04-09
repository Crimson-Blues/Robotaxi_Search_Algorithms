# busquedas/a_estrella.py
import dis
import heapq
from math import exp
import time
from modelos import Node
from .utilidades import is_goal, expand, reconstruct_path, find_positions, manhattan_dist, read_world

def buscar(world_matrix):

    # Setting up of initial conditions
    # Initial key positions
    start, destinations, passengers = find_positions(world_matrix)

    # Initial state: start position of vehicle and position of passengers
    initial_state = (start, passengers)

    #Root node of search tree
    root = Node(
        state=initial_state,
        p=None,
        rator=None,
        depth=0,
        cost=0
    )
    nid = 0

    # Priority queue for nodes not yet expanded
    pending_nodes = []
    # Pop root node
    heapq.heappush(pending_nodes, (estim_cost(root, destinations), nid , root))


    expanded_nodes = 0

    start_time = time.time()

    #Begin search
    while pending_nodes:
        #Pop node of highest priority (least estimated cost)
        current_cost, tie_breaker, current_node = heapq.heappop(pending_nodes)

        #Increment expanded nodes counter
        expanded_nodes += 1
        #print(f"f(n)   : {estim_cost(current_node, destination)}")

        #Check if the popped node is a goal
        if is_goal(current_node, destinations):
            end_time = time.time()

            path = reconstruct_path(current_node)
            depth = current_node.depth
            total_cost = current_node.cost

            return reconstruct_path(current_node), expanded_nodes, depth, total_cost, (end_time - start_time)


        #If node is not goal, expand into childrens
        children = expand(current_node, world_matrix)

        #Insert children into priority queue
        for i, child in enumerate(children):
            nid += 1
            heapq.heappush(pending_nodes, (estim_cost(child, destinations), nid, child))


    #If priority queue is empty and no solution is found:

    time_elapsed = time.time() - start_time
    return None, expanded_nodes, current_node.depth, current_node.cost, time_elapsed



#Sum of Manhattan distance from vehicle to n passengers and destination divided by n+1
def heuristic_alt(node, destination):
    vehicle_pos, passengers = node.state

    distance = 0
    #Sum of Manhattan distances from vehicles to passengers
    for passenger in passengers:
        distance += manhattan_dist(vehicle_pos, passenger)

    #Add distance from vehicle to destination
    distance += manhattan_dist(vehicle_pos, destination)

    distance = distance/(len(passengers) + 1)

    return distance

#Heuristic function:
""" heuristic h(n):
Estimates the remaining cost from the current node to the goal.

Strategy:
- Find the passenger farthest from the vehicle.
- h(n) = dist(vehicle -> farthest passenger) + dist(farthest passenger -> destination)
- If no passengers remain, h(n) = dist(vehicle -> destination)

Is admissible as it calculates minimal required route"""
def heuristic(node, destinations):
    vehicle_pos, passengers = node.state

    estim = 0

    #Determine furthest passenger from vehicle
    dist_to_psgs = [(manhattan_dist(vehicle_pos, p), p) for p in passengers]
    dist_to_psgs.sort()
    
    if dist_to_psgs and destinations:
        furthest_psg =  dist_to_psgs[-1]
        #Distance to furthest passenger
        estim += furthest_psg[0]

        # Compute distance from farthest passenger to destinations
        dist_to_dests = [(manhattan_dist(furthest_psg[1], d), d) for d in destinations]

        # Select the closest destination
        closest_dist_d, closest_dest = dist_to_dests[0]

        estim += closest_dist_d

    elif destinations: #In case there's no passengers left: Distance to closest destination
        dist_to_dests = [(manhattan_dist(vehicle_pos, d), d) for d in destinations]
        closest_dist_d, closest_dest = dist_to_dests[0]

        estim += closest_dist_d

    return estim

# Estimating cost function
""" Total cost estimation f(n):
Estimates the total cost of solution of the branch.
From root passing through current node to the goal.

Strategy:
- Add known cost from root to current node g(n)
- Add heuristic estimation of cost from node to goal h(n)
- f(n) = g(n) + h(n)"""
def estim_cost(node, destinations):
    return node.cost + heuristic(node, destinations)


#file_path = '../Prueba1.txt'
#map_matrix_original = read_world(file_path) 

#path, expanded_nodes, depth, total_cost, time = buscar(map_matrix_original)
#print(f"Path: {path}")
#print(f"Expanded Nodes: {expanded_nodes}")
#print(f"Depth: {depth}")
#print(f"Total Cost: {total_cost}")
#print(f"Time: {time}")


