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
    start, destination, passengers = find_positions(world_matrix)

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

    # Priority queue for nodes not yet expanded
    pending_nodes = []
    # Pop root node
    heapq.heappush(pending_nodes, (estim_cost(root, destination), id(root) , root))


    expanded_nodes = 0

    start_time = time.time()

    #Begin search
    while pending_nodes:
        #Pop node of highest priority (least estimated cost)
        current_cost, tie_breaker, current_node = heapq.heappop(pending_nodes)

        #Increment expanded nodes counter
        expanded_nodes += 1
        #print(f"f(n): {estim_cost(current_node, destination)}")

        #Check if the popped node is a goal
        if is_goal(current_node, destination):
            end_time = time.time()

            path = reconstruct_path(current_node)
            depth = current_node.depth
            total_cost = current_node.cost

            return reconstruct_path(current_node), expanded_nodes, depth, total_cost, (end_time - start_time)


        #If node is not goal, expand into childrens
        children = expand(current_node, world_matrix)

        #Insert children into priority queue
        for i, child in enumerate(children):
            heapq.heappush(pending_nodes, (estim_cost(child, destination), id(child), child))


    #If priority queue is empty and no solution is found:

    end_time = time.time()
    return None, expanded_nodes, 0, 0, (end_time - start_time)



#Sum of Manhattan distance from vehicle to n passengers and destination divided by n+1
def heuristic_average(node, destination):
    vehicle_pos, passengers = node.state

    distance = 0
    #Sum of Manhattan distances from vehicles to passengers
    for passenger in passengers:
        distance += manhattan_dist(vehicle_pos, passenger)

    #Add distance from vehicle to destination
    distance += manhattan_dist(vehicle_pos, destination)

    distance = distance/(len(passengers) + 1)

    return distance


def heuristic_min(node, destination):
    vehicle_pos, passengers = node.state

    estim = 0

    #Determine furthest passenger from vehicle
    dist_to_psgs = [(manhattan_dist(vehicle_pos, p), p) for p in passengers]
    dist_to_psgs.sort()
    
    if dist_to_psgs:
        furthest_psg =  dist_to_psgs[-1]
        #Distance to furthest passenger
        estim += furthest_psg[0]
        #Distance from furthest passenger to destinatio
        estim += manhattan_dist(furthest_psg[1], destination)
    else: #In case there's no passengers left
        estim += manhattan_dist(vehicle_pos, destination)

    return estim

#Sum of Manhattan distances from passenger to passenger from closest to furthest
def heuristic_total(node, destination):
    vehicle_pos, passengers = node.state

    estim = 0

    #Determine distance of passengers from vehicles
    dist_to_psgs = [(manhattan_dist(vehicle_pos, p), p) for p in passengers]
    dist_to_psgs.sort()

    #If there are remaining passengers
    if dist_to_psgs:
        #Adds distance from vehicle to closest passenger
        estim += dist_to_psgs[0][0]

        #Adds distances from passenger to passenger
        for i in range(len(dist_to_psgs) - 1):
            estim += manhattan_dist(dist_to_psgs[i][1], dist_to_psgs[i+1][1])

        #Adds distance from furthest passenger to destination
        estim += manhattan_dist(destination, dist_to_psgs[-1][1])

    else:
        estim += manhattan_dist(vehicle_pos, destination)
    
    return estim

def estim_cost(node, destination):
    return node.cost + heuristic_min(node, destination)


#file_path = '../Prueba1.txt'
#map_matrix_original = read_world(file_path) 

#path, expanded_nodes, depth, total_cost, time = buscar(map_matrix_original)
#print(f"Path: {path}")
#print(f"Expanded Nodes: {expanded_nodes}")
#print(f"Depth: {depth}")
#print(f"Total Cost: {total_cost}")
#print(f"Time: {time}")


