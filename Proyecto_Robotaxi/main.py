# main.py
import pygame
import sys
import os
from busquedas import amplitud, utilidades, profundidad, ucs, a_estrella, avara
from modelos import UIElement
from pygame.sprite import Sprite
import tkinter as tk
from tkinter import filedialog

# Variable Global de Assets (Guarda imágenes cargadas a memoria)
ASSETS = {}

# ... (Funciones de dibujo draw_world, etc.)
def draw_world(screen, matrix, taxi_pos, size, offset_x=0, offset_y=0):
    # Definición de colores modificados
    COLORS = {
        0: (255, 255, 255),  # Blanco: Calle libre
        1: (112, 128, 144),  # Gris: Obstáculo/Muro
        2: (252, 215, 0),    # Amarillo: Taxi (Inicio)
        3: (193, 4, 15),     # Rojo: Tráfico pesado
        4: (52, 152, 219),   # Azul: Pasajero
        5: (50, 205, 50)     # Verde: Destino final
    }

    CELL_SIZE = size  
    
    for row_idx, row in enumerate(matrix):
        for col_idx, value in enumerate(row):
            rect = pygame.Rect(offset_x + (col_idx * CELL_SIZE), offset_y + (row_idx * CELL_SIZE), CELL_SIZE, CELL_SIZE)
            
            # Pintar el suelo base (blanco para calles)
            base_color = COLORS.get(value, (255, 255, 255))
            if value in [2, 4, 5]:
                base_color = (255, 255, 255)
            pygame.draw.rect(screen, base_color, rect)
            pygame.draw.rect(screen, (18, 18, 18), rect, 1)
            
            asset = None
            if value == 2 and not taxi_pos and 'taxi' in ASSETS:
                asset = ASSETS['taxi']
            elif value == 4 and 'passenger' in ASSETS:
                asset = ASSETS['passenger']
            elif value == 5 and 'destination' in ASSETS:
                asset = ASSETS['destination']
            
            # Renderizar el Icono encima de la calle blanca
            if asset:
                scaled_asset = pygame.transform.smoothscale(asset, (int(CELL_SIZE - 4), int(CELL_SIZE - 4)))
                screen.blit(scaled_asset, (rect.x + 2, rect.y + 2))
            elif value in [2, 4, 5] and not taxi_pos:
                # Fallback en caso de que ocurra un error con la imagen
                pygame.draw.rect(screen, COLORS[value], rect)
                pygame.draw.rect(screen, (18, 18, 18), rect, 1)

    # Dibujar el taxi animado superpuesto en movimiento si existe
    if taxi_pos:
        tx_row, tx_col = taxi_pos
        rect = pygame.Rect(offset_x + (tx_col * CELL_SIZE), offset_y + (tx_row * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        
        if 'taxi' in ASSETS:
            scaled_taxi = pygame.transform.smoothscale(ASSETS['taxi'], (int(CELL_SIZE - 2), int(CELL_SIZE - 2)))
            screen.blit(scaled_taxi, (rect.x + 1, rect.y + 1))
        else:
            taxi_x = offset_x + (tx_col * CELL_SIZE) + 5
            taxi_y = offset_y + (tx_row * CELL_SIZE) + 5
            taxi_rect = pygame.Rect(taxi_x, taxi_y, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(screen, COLORS[2], taxi_rect, border_radius=5)
            pygame.draw.rect(screen, (0, 0, 0), taxi_rect, 2, border_radius=5)

def create_surface_with_text(text, font_size, text_rgb, bg_rgb, border_color=None):
    font = pygame.font.SysFont("Arial", int(font_size), bold=True)
    
    if "Seleccionar Mundo" in text:
        text_rgb = (255, 170, 0)
        
    lines = text.split('\n')
    text_surfs = [font.render(line, True, text_rgb) for line in lines]
    
    max_w = max([s.get_width() for s in text_surfs])
    total_h = sum([s.get_height() for s in text_surfs]) + (len(lines) - 1) * 5
    
    glow_size = 6
    padding_x = 25 + glow_size
    padding_y = 12 + glow_size
    w = max_w + padding_x * 2
    h = total_h + padding_y * 2
    
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # Extraemos el color rgb
    r, g, b = text_rgb
    br, bg, bb = border_color if border_color else text_rgb
    
    plain_text_mode = False
    upper_text = text.upper()
    keywords = ["CORRER", "ALGORITMOS DE", "INFORMADA", "ESTRELLA", "AVARA", "AMPLITUD", "PROFUNDIDAD", "COSTO"]
    if any(k in upper_text for k in keywords) or text.strip() == "X" or text.endswith(" "):
        plain_text_mode = True

    if plain_text_mode:
        current_y = padding_y
        for i, s in enumerate(text_surfs):
            x_pos = padding_x + (max_w - s.get_width()) // 2
            surface.blit(s, (x_pos, current_y))
            current_y += s.get_height() + 5
    else:
        rect_outer = (glow_size, glow_size, w - glow_size * 2, h - glow_size * 2)
        
        pygame.draw.rect(surface, (br, bg, bb, 40), rect_outer, width=8, border_radius=12)
        pygame.draw.rect(surface, (br, bg, bb, 90), rect_outer, width=5, border_radius=10)
        pygame.draw.rect(surface, (br, bg, bb, 255), rect_outer, width=2, border_radius=8)

        current_y = padding_y
        for s in text_surfs:
            x_pos = padding_x + (max_w - s.get_width()) // 2
            surface.blit(s, (x_pos, current_y))
            current_y += s.get_height() + 5
        
    return surface.convert_alpha()


class UIElement(Sprite):
    # An user interface element that can be added to a surface 

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, border_color=None):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            bg_rgb (background colour) - tuple (r, g, b)
            text_rgb (text colour) - tuple (r, g, b)
        """
        self.mouse_over = False  # indicates if the mouse is over the element
        self.text = text # Store text value

        # create the default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb, border_color=border_color
        )

        # create the image that shows when mouse is over the element
        scale_factor = 1.0 if ("ALGORITMOS DE" in text or text.endswith(" ")) else 1.1
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * scale_factor, text_rgb=text_rgb, bg_rgb=bg_rgb, border_color=border_color
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
        # Draws element onto a surface
        surface.blit(self.image, self.rect)

def draw_results_window(screen, success, exp, dep, cost, time):
    # Crear una superficie para el fondo (con transparencia)
    overlay = pygame.Surface((480, 260))
    overlay.set_alpha(230) 
    overlay.fill((40, 44, 52)) # Color oscuro
    
    # Dibujar borde verde (color del destino)
    if success:
        pygame.draw.rect(overlay, (50, 205, 50), overlay.get_rect(), 3)
        message = "¡Misión Completada!"
        txt_color = (50, 205, 50)
    else:
        pygame.draw.rect(overlay, (140, 8, 35), overlay.get_rect(), 3)
        message = "Solución No Encontrada"
        txt_color = (240, 10, 56)
    
    font = pygame.font.SysFont("Courier", 20, bold=True)
    title_font = pygame.font.SysFont("Courier", 24, bold=True)

    # Los textos ahora usan las variables exp, dep, cost y time

    texts = [
        (message, txt_color, title_font),
        (f"Nodos Expandidos: {exp}", (255, 255, 255), font),
        (f"Profundidad: {dep}", (255, 255, 255), font),
        (f"Costo Total: {cost}", (255, 255, 255), font),
        (f"Tiempo: {time:.4f}s", (255, 255, 255), font),
        ("Presiona ESC para volver al Inicio", (200, 200, 200), font)
    ]

    for i, (text, color, f) in enumerate(texts):
        text_surf = f.render(text, True, color)
        overlay.blit(text_surf, (40, 15 + (i * 40))) # Ubicación del texto

    screen_rect = screen.get_rect()
    screen.blit(overlay, (screen_rect.centerx - 200, screen_rect.centery - 150))

def draw_text(screen, text, center, size=20, color=(255, 255, 255)):
    # Usamos una fuente estándar de Pygame
    font = pygame.font.SysFont("Courier", size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)
    return rect

def draw_world_preview(screen, matrix, size, offset_x=0, offset_y=0):
    # Use color palette for preview of map
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
            rect = pygame.Rect(offset_x + (c * size), offset_y + (r * size), size, size)
            
            # Pintar el suelo base (blanco para calles)
            base_color = COLORS.get(val, (255, 255, 255))
            if val in [2, 4, 5]:
                base_color = (255, 255, 255)
            pygame.draw.rect(screen, base_color, rect)
            pygame.draw.rect(screen, (18, 18, 18), rect, 1)
            
            asset = None
            if val == 2 and 'taxi' in ASSETS:
                asset = ASSETS['taxi']
            elif val == 4 and 'passenger' in ASSETS:
                asset = ASSETS['passenger']
            elif val == 5 and 'destination' in ASSETS:
                asset = ASSETS['destination']
                
            # Renderizar el Icono si existe
            if asset:
                scaled_asset = pygame.transform.smoothscale(asset, (int(size - 4), int(size - 4)))
                screen.blit(scaled_asset, (rect.x + 2, rect.y + 2))
            elif val in [2, 4, 5]:
                # Fallback sin iconos
                pygame.draw.rect(screen, COLORS[val], rect)
                pygame.draw.rect(screen, (18, 18, 18), rect, 1)


# Pop up file selection window 
def select_file():
    # Root window for carry on context
    root = tk.Tk()
    root.withdraw()
    try:
        icon = tk.PhotoImage(file='folder.png')
        root.iconphoto(True, icon)
    except Exception:
        pass # Prevents crash if the image file is missing
    filepath = filedialog.askopenfilename(
        title="Selecciona Archivo",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        multiple=False,
        parent=root
    )

    root.destroy()

    return filepath

def main():
    # Initial config
    pygame.init()

    file_path = ""
    current_algo_name = ""

    # Initialize empty map
    map_matrix = []
    map_matrix_original = []

    CELL_SIZE = 0
    map_width = 400
    map_height = 400

    screen_width = 900
    screen_height = 600  
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    base_dir = os.path.dirname(__file__)
    bg_path = os.path.join(base_dir, "assets", "background.png")
    bg2_path = os.path.join(base_dir, "assets", "background2.png")
    bg3_path = os.path.join(base_dir, "assets", "background3.png")
    icon_path = os.path.join(base_dir, "assets", "icon.png")
    
    try:
        bg_img = pygame.image.load(bg_path).convert()
    except Exception as e:
        print("Aviso: No se pudo cargar el fondo:", e)
        bg_img = None
        
    try:
        bg2_img = pygame.image.load(bg2_path).convert()
    except Exception as e:
        print("Aviso: No se pudo cargar el fondo 2:", e)
        bg2_img = None

    try:
        bg3_img = pygame.image.load(bg3_path).convert()
    except Exception as e:
        print("Aviso: No se pudo cargar el fondo 3:", e)
        bg3_img = None
        
    try:
        ui_icon = pygame.image.load(icon_path).convert_alpha()
        ui_icon = pygame.transform.smoothscale(ui_icon, (110, 110))
    except Exception as e:
        print("Aviso: No se pudo cargar el icono:", e)
        ui_icon = None

    global ASSETS
    try:
        ASSETS['taxi'] = pygame.image.load(os.path.join(base_dir, "assets", "taxi.png")).convert_alpha()
        ASSETS['passenger'] = pygame.image.load(os.path.join(base_dir, "assets", "passenger.png")).convert_alpha()
        ASSETS['destination'] = pygame.image.load(os.path.join(base_dir, "assets", "destination_icon.png")).convert_alpha()
    except Exception as e:
        print("Aviso: Fallo al cargar sprites de minimapa:", e)


    
    panel_center_x = 250 
    true_center_x = 450

    # Buttons for choosing search algorithm
    back_button = {
            "ui": UIElement((44, 24), "<-", 15, (40, 44, 52), (158, 155, 155)),
            "funct": lambda: update_state("MENU INICIAL CON MUNDO")
        }
    buttons_algs = {
        "selection": [
            {
                "ui": UIElement((panel_center_x, 277), "BÚSQUEDA NO\nINFORMADA", 20, (40, 44, 52), (255, 170, 0)),
                "funct": lambda: update_state("MENU NO INFORMADO")
            },
            {
                "ui": UIElement((panel_center_x, 399), "BÚSQUEDA\nINFORMADA", 20, (40, 44, 52), (255, 170, 0)),
                "funct": lambda: update_state("MENU INFORMADO")
            }
        ],
        "not_informed": [
        {
            "ui": UIElement((panel_center_x, 256), "Amplitud", 25, (40, 44, 52), (255, 170, 0)),
            "algo": amplitud.buscar # Calls on the amplitude search algorithm
        },
        {
            "ui": UIElement((panel_center_x, 341), "Profundidad", 25, (40, 44, 52), (255, 170, 0)),
            "algo": profundidad.buscar # Calls on the depth search algorithm
        },
        {
            "ui": UIElement((panel_center_x, 423), "Costo Uniforme", 25, (40, 44, 52), (255, 170, 0)),
            "algo": ucs.buscar # Calls on the cost search algorithm
        }
        ],
        "informed": [
        {
            "ui": UIElement((panel_center_x, 278), "A Estrella", 25, (40, 44, 52), (255, 170, 0)),
            "algo": a_estrella.buscar # Calls on the A* search algorithm
        },
        {
            "ui": UIElement((panel_center_x, 397), "Avara", 25, (40, 44, 52), (255, 170, 0)),
            "algo": avara.buscar # Calls on the Greedy Best-First Search algorithm
        }
        ]

    }

    titles_algs = [
        {
            "ui": UIElement((panel_center_x, 173), "BÚSQUEDA NO\nINFORMADA ", 22, (40, 44, 52), (255, 255, 255)),
            "funct": lambda: None
        },
        {
            "ui": UIElement((panel_center_x, 169), "BÚSQUEDA\nINFORMADA ", 22, (40, 44, 52), (255, 255, 255)),
            "funct": lambda: None
        }
    ]

    tipo_algs_title = {
        "ui": UIElement((panel_center_x, 169), "ALGORITMOS DE\nBÚSQUEDA", 22, (40, 44, 52), (255, 255, 255)),
        "funct": lambda: None
    }

    buttons_initial_center = [
        {
            "ui": UIElement((true_center_x, 250), "Seleccionar Mundo", 25, (40, 44, 52), (255, 255, 255)),
            "funct": lambda: update_file(select_file()) # Select custom File
        },
        {
            "ui": UIElement((true_center_x, 320), "Usar ejemplo", 18, (40, 44, 52), (230, 245, 255)),
            "funct": lambda: update_file("Prueba1.txt") # Use example file
        }
    ]

    buttons_initial_left = [
        {
            "ui": UIElement((300, 250), "Seleccionar Mundo", 25, (40, 44, 52), (255, 255, 255)),
            "funct": lambda: update_file(select_file())
        },
        {
            "ui": UIElement((300, 320), "Usar ejemplo", 18, (40, 44, 52), (230, 245, 255)),
            "funct": lambda: update_file("Prueba1.txt")
        },
        {
            "ui": UIElement((685, 200), "X", 15, (40, 44, 52), (255, 60, 60)),
            "funct": lambda: update_state("MENU INICIAL SIN MUNDO")
        },
        {
            "ui": UIElement((600, 390), "Correr Simulación", 23, (40, 44, 52), (255, 170, 0)),
            "funct": lambda: update_state("MENU SELECCION ALGORITMO")
        }
    ]

    estado_actual = "MENU INICIAL SIN MUNDO" # Initial menu state
    current_taxi_pos = [0, 0]
    path, path_index, move_timer = [], 0, 0
    datos_finales = {}
    clock = pygame.time.Clock()
    current_title = None
    button_list = buttons_initial_center

    #Inner functions to change menus

    def alg_selection_menu():
        nonlocal estado_actual, current_title, button_list
        estado_actual = "MENU SELECCION ALGORITMO"
        current_title = tipo_algs_title
        button_list = buttons_algs["selection"]

    def non_informed_menu():
        nonlocal estado_actual, current_title, button_list
        estado_actual = "MENU NO INFORMADO"
        current_title = titles_algs[0]
        button_list = buttons_algs["not_informed"]

    def informed_menu():
        nonlocal estado_actual, current_title, button_list
        current_title = titles_algs[1]
        estado_actual = "MENU INFORMADO"
        button_list = buttons_algs["informed"]

    def initial_menu_with_wrld():
        nonlocal button_list, estado_actual
        estado_actual = "MENU INICIAL CON MUNDO"
        button_list = buttons_initial_left

    def initial_menu_no_wrld():
        nonlocal button_list, estado_actual
        estado_actual = "MENU INICIAL SIN MUNDO"
        button_list = buttons_initial_center

    #Auxilary functions to set button actions

    def update_file(new_file_path):
        nonlocal map_matrix
        nonlocal map_matrix_original
        nonlocal estado_actual
        nonlocal CELL_SIZE
        nonlocal file_path
        estado_actual = "MENU INICIAL CON MUNDO"
        file_path = new_file_path
        map_matrix_original = utilidades.read_world(file_path) # Read world map
        if not map_matrix_original: return

        # Mutable copy for searches
        map_matrix = [row[:] for row in map_matrix_original]

        CELL_SIZE = 360/len(map_matrix[0])

    def update_state(new_state):
        nonlocal estado_actual
        estado_actual = new_state

    while True:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    estado_actual = "MENU SELECCION ALGORITMO"
                    path_index = 0
                    move_timer = 0
                    path = []
                    map_matrix = [row[:] for row in map_matrix_original] # Restart map_matrix 
            
            # --- DYNAMIC CLICK DETECTION ---
            if ("INFORMADO" in estado_actual or estado_actual == "MENU SELECCION ALGORITMO") and event.type == pygame.MOUSEBUTTONDOWN:
                if estado_actual == "MENU SELECCION ALGORITMO":
                    button_list = buttons_algs["selection"]
                elif estado_actual == "MENU NO INFORMADO":
                    button_list = buttons_algs["not_informed"]
                elif estado_actual == "MENU INFORMADO":
                    button_list = buttons_algs["informed"]

                for btn in button_list:
                    if btn["ui"].rect.collidepoint(mouse_pos):
                        if "algo" in btn:
                            # Execute algorithm of chosen button
                            current_algo_name = btn["ui"].text.replace("\n", " ") # Store name
                            res = btn["algo"](map_matrix)
                            path, expanded, depth, cost, calc_time = res
                            datos_finales = {'exp': expanded, 'dep': depth, 'cost': cost, 'time': calc_time}
                            
                            start_pos, _, _ = utilidades.find_positions(map_matrix)
                            current_taxi_pos = list(start_pos)
                            map_matrix[start_pos[0]][start_pos[1]] = 0 
                            estado_actual = "SIMULACION"
                        elif "funct" in btn:
                            btn["funct"]()

                if current_title:
                    if current_title["ui"].rect.collidepoint(mouse_pos):
                        current_title["funct"]()

                if back_button["ui"].rect.collidepoint(mouse_pos):
                    if estado_actual == "MENU SELECCION ALGORITMO":
                        update_state("MENU INICIAL CON MUNDO")
                    else:
                        update_state("MENU SELECCION ALGORITMO")

            if "MENU INICIAL" in estado_actual and event.type == pygame.MOUSEBUTTONDOWN:
                for btn in button_list:
                    if btn["ui"].rect.collidepoint(mouse_pos):
                        btn["funct"]()



        # Render del Fondo principal
        if "MENU INICIAL" in estado_actual and bg_img:
            bg_scaled = pygame.transform.scale(bg_img, (screen_width, screen_height))
            screen.blit(bg_scaled, (0, 0))
        elif estado_actual in ["MENU SELECCION ALGORITMO", "MENU INFORMADO", "SIMULACION"]:
            # Durante la simulación, decidimos el fondo según la categoría (current_title)
            if estado_actual == "SIMULACION" and current_title and "NO" in current_title["ui"].text:
                if bg3_img:
                    bg3_scaled = pygame.transform.scale(bg3_img, (screen_width, screen_height))
                    screen.blit(bg3_scaled, (0, 0))
            else:
                if bg2_img:
                    bg2_scaled = pygame.transform.scale(bg2_img, (screen_width, screen_height))
                    screen.blit(bg2_scaled, (0, 0))
        elif estado_actual == "MENU NO INFORMADO":
            if bg3_img:
                bg3_scaled = pygame.transform.scale(bg3_img, (screen_width, screen_height))
                screen.blit(bg3_scaled, (0, 0))
        else:
            screen.fill((30, 30, 30)) 

        # Update state visuals
        if estado_actual == "MENU INICIAL SIN MUNDO":
            initial_menu_no_wrld()
        elif estado_actual == "MENU INICIAL CON MUNDO":
            initial_menu_with_wrld()
        elif estado_actual == "MENU SELECCION ALGORITMO":
            alg_selection_menu()
        elif estado_actual == "MENU NO INFORMADO":
            non_informed_menu()
        elif estado_actual == "MENU INFORMADO":
            informed_menu()

        # Drew updated visuals
        if "INFORMADO" in estado_actual or estado_actual in ["MENU SELECCION ALGORITMO", "SIMULACION"]:
            if current_title:
                current_title["ui"].update(mouse_pos)
                current_title["ui"].draw(screen)
            
            # Solo botón de retroceso fuera de simulación
            if estado_actual != "SIMULACION":
                back_button["ui"].update(mouse_pos)
                back_button["ui"].draw(screen)
            
            # Dibujamos el nombre del algoritmo seleccionado durante la simulación
            if estado_actual == "SIMULACION":
                y_pos = 256 if "NO" in current_title["ui"].text else 278
                draw_text(screen, current_algo_name, (panel_center_x, y_pos), size=30, color=(255, 170, 0))
            
            # Solo dibujamos el preview si NO estamos simulando (ya que la simulación tiene su propio dibujo dinámico)
            if estado_actual != "SIMULACION":
                draw_world_preview(screen, map_matrix, CELL_SIZE, offset_x=448, offset_y=127)

        if "MENU" in estado_actual:
            for btn in button_list:
                btn["ui"].update(mouse_pos)
                btn["ui"].draw(screen)

        if "MENU " in estado_actual or estado_actual == "SIMULACION":
            draw_text(screen, "ROBOTAXI ZOOX", (true_center_x + 3, 46), size=55, color=(40, 30, 0))
            draw_text(screen, "ROBOTAXI ZOOX", (true_center_x, 43), size=55, color=(255, 170, 0))
            
        # Sólo lo mostramos cuando el mundo está vacío para que no estrelle con el minimapa!
        if estado_actual == "MENU INICIAL SIN MUNDO":
            if ui_icon:
                icon_rect = ui_icon.get_rect(center=(true_center_x, 400))
                screen.blit(ui_icon, icon_rect)

        if estado_actual == "MENU INICIAL CON MUNDO":
            draw_world_preview(screen, map_matrix, 150/len(map_matrix[0]), offset_x=600-75, offset_y=210)

        
        elif estado_actual == "SIMULACION":
            move_timer += dt
            if path and path_index < len(path) and move_timer > 100: # Playback animation speed
                direction = path[path_index]
                if direction == 'Up': current_taxi_pos[0] -= 1
                elif direction == 'Down': current_taxi_pos[0] += 1
                elif direction == 'Left': current_taxi_pos[1] -= 1
                elif direction == 'Right': current_taxi_pos[1] += 1
                
                if map_matrix[current_taxi_pos[0]][current_taxi_pos[1]] == 4:
                    map_matrix[current_taxi_pos[0]][current_taxi_pos[1]] = 0
                
                path_index += 1
                move_timer = 0

            draw_world(screen, map_matrix, current_taxi_pos, CELL_SIZE, offset_x=448, offset_y=127)
            
            if path and path_index >= len(path):
                draw_results_window(screen, success=True, **datos_finales)

            if path is None:
                draw_results_window(screen, success=False, **datos_finales)

        pygame.display.flip()

#Run main function
if __name__ == "__main__":
    main()

    # file_path = 'Prueba1.txt'
    # map_matrix = read_world(file_path)
    
    # if map_matrix:
    #     print("Test")
    #     path, expanded_nodes, depth, cost, calc_time = amplitud.buscar(map_matrix)
        
    #     if path is not None:
    #         print("Solución encontrada")
    #         print("Ruta: ", path)
    #         print("Nodos expandidos: ", expanded_nodes)
    #         print("Profundidad del árbol: ", depth)
    #         print("Costo total de la ruta: ", cost)
    #         print("Tiempo de cómputo: ", calc_time, "segundos")
    #     else:
    #         print("\nNo se encontró una solución")
    #         print("Nodos expandidos: ", expanded_nodes)
    #         print("Tiempo de cómputo: ", calc_time, "segundos")