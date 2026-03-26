import heapq
import time
from modelos import Node
from busquedas.utilidades import find_positions, expand, is_goal, reconstruct_path


def buscar(world_matrix):
    start_time = time.time()

    # Obtener posiciones
    start, destination, passengers = find_positions(world_matrix)

    # Estado inicial
    initial_state = (start, passengers)

    root = Node(
        state=initial_state,
        p=None,
        rator=None,
        depth=0,
        cost=0
    )

    # Cola de prioridad (costo, id, nodo)
    frontier = []
    heapq.heappush(frontier, (0, id(root), root))

    visited = set()
    best_cost = {initial_state: 0}

    expanded_nodes = 0

    while frontier:
        current_cost, _, current_node = heapq.heappop(frontier)

        if current_node.state in visited:
            continue

        visited.add(current_node.state)
        expanded_nodes += 1

        # Verificar objetivo
        if is_goal(current_node, destination):
            end_time = time.time()

            path = reconstruct_path(current_node)
            depth = current_node.depth
            total_cost = current_node.cost

            return path, expanded_nodes, depth, total_cost, (end_time - start_time)

        # Expandir
        children = expand(current_node, world_matrix)

        for child in children:
            state = child.state

            if state not in best_cost or child.cost < best_cost[state]:
                best_cost[state] = child.cost
                heapq.heappush(frontier, (child.cost, id(child), child))

    # No hay solución
    end_time = time.time()
    return None, expanded_nodes, 0, 0, (end_time - start_time)