# main.py
import pygame
import sys
# IMPORTAMOS NUESTROS MÓDULOS
import algoritmos
from pygame.sprite import Sprite
from modelos import UIElement, Taxi 

# ... (Funciones de dibujo draw_world, etc.)
def draw_world(screen, matrix, taxi_pos, offset_x=0):
    # Definición de tus colores modificados
    COLORS = {
        0: (255, 255, 255),  # Blanco: Calle libre
        1: (112, 128, 144),  # Gris: Obstáculo/Muro
        2: (252, 215, 0),    # Amarillo: Taxi (Inicio)
        3: (193, 4, 15),     # Rojo: Tráfico pesado
        4: (52, 152, 219),   # Azul: Pasajero
        5: (50, 205, 50)     # Verde: Destino final
    }

    CELL_SIZE = 40  
    
    for row_idx, row in enumerate(matrix):
        for col_idx, value in enumerate(row):
            color = COLORS.get(value, (255, 255, 255))
            # Sumamos offset_x a la posición X del rectángulo
            rect = pygame.Rect(offset_x + (col_idx * CELL_SIZE), row_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (18, 18, 18), rect, 1)

    # Dibujar el taxi en movimiento si se proporciona una posición
    if taxi_pos:
        tx_row, tx_col = taxi_pos
        # Calculamos la posición exacta sumando el offset_x del menú
        taxi_x = offset_x + (tx_col * CELL_SIZE) + 5
        taxi_y = (tx_row * CELL_SIZE) + 5
        
        # Creamos el rectángulo del taxi
        taxi_rect = pygame.Rect(taxi_x, taxi_y, CELL_SIZE - 10, CELL_SIZE - 10)
        
        # Pintamos el taxi de AMARILLO (COLORS[2])
        pygame.draw.rect(screen, COLORS[2], taxi_rect, border_radius=5)
        # Opcional: un borde negro para que no se pierda en el blanco
        pygame.draw.rect(screen, (0, 0, 0), taxi_rect, 2, border_radius=5)

def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """ Returns surface with text written on """
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


class UIElement(Sprite):
    """ An user interface element that can be added to a surface """

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            bg_rgb (background colour) - tuple (r, g, b)
            text_rgb (text colour) - tuple (r, g, b)
        """
        self.mouse_over = False  # indicates if the mouse is over the element

        # create the default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # create the image that shows when mouse is over the element
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # add both images and their rects to lists
        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        # calls the init method of the parent sprite class
        super().__init__()

    # properties that vary the image and its rect when the mouse is over the element
    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
        else:
            self.mouse_over = False

    def draw(self, surface):
        """ Draws element onto a surface """
        surface.blit(self.image, self.rect)

def draw_results_window(screen, exp, dep, cost, time):
    # Crear una superficie para el fondo (con transparencia)
    overlay = pygame.Surface((480, 260))
    overlay.set_alpha(230) 
    overlay.fill((40, 44, 52)) # Color oscuro
    
    # Dibujar borde verde (color del destino)
    pygame.draw.rect(overlay, (50, 205, 50), overlay.get_rect(), 3)
    
    font = pygame.font.SysFont("Courier", 20, bold=True)
    title_font = pygame.font.SysFont("Courier", 24, bold=True)

    # Los textos ahora usan las variables exp, dep, cost y time
    texts = [
        ("¡Misión Completada!", (50, 205, 50), title_font),
        (f"Nodos Expandidos: {exp}", (255, 255, 255), font),
        (f"Profundidad: {dep}", (255, 255, 255), font),
        (f"Costo Total: {cost}", (255, 255, 255), font),
        (f"Tiempo: {time:.4f}s", (255, 255, 255), font),
        ("Presiona ESC para volver al Inicio", (200, 200, 200), font)
    ]

    for i, (text, color, f) in enumerate(texts):
        text_surf = f.render(text, True, color)
        overlay.blit(text_surf, (40, 15 + (i * 40))) # Ubicación del texto

    # Centrar la ventana en la pantalla (considerando el offset del menú)
    # Si quieres que aparezca centrada en toda la ventana:
    screen_rect = screen.get_rect()
    screen.blit(overlay, (screen_rect.centerx - 200, screen_rect.centery - 150))

def draw_text(screen, text, center, size=20, color=(255, 255, 255)):
    # Usamos una fuente estándar de Pygame
    font = pygame.font.SysFont("Courier", size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)

def draw_world_preview(screen, matrix, size, offset_x=0):
    # Usamos exactamente tu paleta de colores para la vista previa
    COLORS = {
        0: (255, 255, 255),  # Blanco
        1: (112, 128, 144),  # Gris
        2: (252, 215, 0),    # Amarillo
        3: (193, 4, 15),     # Rojo
        4: (52, 152, 219),   # Azul
        5: (50, 205, 50)     # Verde
    }
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            color = COLORS.get(val, (255, 255, 255))
            # Aplicamos el desplazamiento offset_x a la coordenada X
            rect = pygame.Rect(offset_x + (c * size), r * size, size, size)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (18, 18, 18), rect, 1)

def main():
    # ... (Configuración inicial)
    pygame.init()
    file_path = 'Prueba1.txt'
    map_matrix_original = algoritmos.read_world(file_path)
    if not map_matrix_original: return

    # Usamos una copia para trabajar
    map_matrix = [row[:] for row in map_matrix_original]

    CELL_SIZE = 40 
    map_width = len(map_matrix[0]) * CELL_SIZE
    map_height = len(map_matrix) * CELL_SIZE
    screen = pygame.display.set_mode((300 + map_width, max(400, map_height)))
    
    panel_center_x = 150 

    # Ahora los botones se referencian a través del módulo algoritmos
    buttons = [
        {
            "ui": UIElement((150, 150), "Amplitud", 25, (40, 44, 52), (255, 255, 255)),
            "algo": algoritmos.preferred_search_amplitude # <--- Nota el prefijo
        },
        {
            "ui": UIElement((150, 220), "Profundidad", 25, (40, 44, 52), (255, 255, 255)),
            "algo": algoritmos.preferred_search_depth
        }
    ]

    # ... (Resto del bucle de Pygame)
    estado_actual = "MENU"
    current_taxi_pos = [0, 0]
    path, path_index, move_timer = [], 0, 0
    datos_finales = {}
    clock = pygame.time.Clock()

    while True:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    estado_actual = "MENU"
                    path_index = 0
                    move_timer = 0
                    path = []
                    map_matrix = [row[:] for row in map_matrix_original]
            
            # --- DETECCIÓN DE CLICS DINÁMICA ---
            if estado_actual == "MENU" and event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn["ui"].rect.collidepoint(mouse_pos):
                        # Ejecutamos el algoritmo asociado al botón presionado
                        res = btn["algo"](map_matrix)
                        path, expanded, depth, cost, calc_time = res
                        datos_finales = {'exp': expanded, 'dep': depth, 'cost': cost, 'time': calc_time}
                        
                        start_pos, _, _ = algoritmos.find_positions(map_matrix)
                        current_taxi_pos = list(start_pos)
                        map_matrix[start_pos[0]][start_pos[1]] = 0 
                        estado_actual = "SIMULACION"

        screen.fill((30, 30, 30)) 

        # Dibujar Panel Lateral
        draw_text(screen, "Algoritmos", (panel_center_x, 50), 30)
        for btn in buttons:
            btn["ui"].update(mouse_pos)
            btn["ui"].draw(screen)

        if estado_actual == "MENU":
            draw_world_preview(screen, map_matrix, CELL_SIZE, offset_x=300)
        
        elif estado_actual == "SIMULACION":
            move_timer += dt
            if path and path_index < len(path) and move_timer > 300:
                direction = path[path_index]
                if direction == 'Up': current_taxi_pos[0] -= 1
                elif direction == 'Down': current_taxi_pos[0] += 1
                elif direction == 'Left': current_taxi_pos[1] -= 1
                elif direction == 'Right': current_taxi_pos[1] += 1
                
                if map_matrix[current_taxi_pos[0]][current_taxi_pos[1]] == 4:
                    map_matrix[current_taxi_pos[0]][current_taxi_pos[1]] = 0
                
                path_index += 1
                move_timer = 0

            draw_world(screen, map_matrix, current_taxi_pos, offset_x=300)
            
            if path_index >= len(path):
                draw_results_window(screen, **datos_finales)

        pygame.display.flip()

#Run main function
if __name__ == "__main__":
    main()
    file_path = 'Prueba1.txt'
    map_matrix = read_world(file_path)
    
    if map_matrix:
        path, expanded_nodes, depth, cost, calc_time = preferred_search_amplitude(map_matrix)
        
        if path is not None:
            print("Solución encontrada")
            print("Ruta: ", path)
            print("Nodos expandidos: ", expanded_nodes)
            print("Profundidad del árbol: ", depth)
            print("Costo total de la ruta: ", cost)
            print("Tiempo de cómputo: ", calc_time, "segundos")
        else:
            print("\nNo se encontró una solución")
            print("Nodos expandidos: ", expanded_nodes)