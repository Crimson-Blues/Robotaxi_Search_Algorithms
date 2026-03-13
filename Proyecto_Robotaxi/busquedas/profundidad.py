# busquedas/profundidad.py
from collections import deque
import time
from modelos import Node
from .utilidades import is_goal, expand, reconstruct_path, find_positions

def buscar(world_matrix): 
    # 1. Configuración inicial igual que en amplitud
    start, destination, initial_passengers = find_positions(world_matrix)
    initial_state = (start, initial_passengers)

    root_node = Node(state=initial_state)

    # 2. Usamos una lista o deque como PILA (LIFO)
    stack = deque([root_node])
    
    # El conjunto de visitados es crucial en DFS para evitar bucles infinitos
    visited = set()
    visited.add(initial_state)

    expanded_nodes = 0
    start_time = time.time()

    while stack:
        # 3. DIFERENCIA CLAVE: Usamos pop() para sacar el ÚLTIMO elemento insertado
        current_node = stack.pop()

        expanded_nodes += 1

        # 4. Verificación de meta
        if is_goal(current_node.state, destination):
            time_elapsed = time.time() - start_time
            path = reconstruct_path(current_node)
            return path, expanded_nodes, current_node.depth, current_node.cost, time_elapsed

        # 5. Expansión de hijos
        children = expand(current_node, world_matrix)

        for child in children:
            if child.state not in visited:
                visited.add(child.state)
                # Al añadir al final y sacar del final, exploramos hacia lo profundo
                stack.append(child)

    # En caso de no encontrar solución
    return None, expanded_nodes, 0, 0, 0