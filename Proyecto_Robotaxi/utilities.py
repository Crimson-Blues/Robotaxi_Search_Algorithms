import pygame
from pygame.sprite import Sprite
import tkinter as tk
from tkinter import filedialog
import os


def create_surface_with_text(text, font_size, text_rgb, bg_rgb, border_color=None, text_style=None):
    font = pygame.font.SysFont("Arial", int(font_size), bold=True)
        
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
    

    if text_style == "PLAIN":
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

def draw_world(screen, matrix, taxi_pos, size, offset_x=0, offset_y=0, ASSETS = {}):
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

def draw_text(screen, text, center, size=20, color=(255, 255, 255)):
    # Usamos una fuente estándar de Pygame
    font = pygame.font.SysFont("Courier", size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)
    return rect

def draw_world_preview(screen, matrix, size, offset_x=0, offset_y=0, ASSETS={}):
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

def load_assets():
    ASSETS = {}
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
        ui_icon = pygame.transform.scale_by(ui_icon, 0.25)
    except Exception as e:
        print("Aviso: No se pudo cargar el icono:", e)
        ui_icon = None

    try:
        ASSETS['taxi'] = pygame.image.load(os.path.join(base_dir, "assets", "taxi.png")).convert_alpha()
        ASSETS['passenger'] = pygame.image.load(os.path.join(base_dir, "assets", "passenger.png")).convert_alpha()
        ASSETS['destination'] = pygame.image.load(os.path.join(base_dir, "assets", "destination_icon.png")).convert_alpha()
    except Exception as e:
        print("Aviso: Fallo al cargar sprites de minimapa:", e)

    ASSETS["bg_img"] = bg_img
    ASSETS["bg2_img"] = bg2_img
    ASSETS["bg3_img"] = bg3_img
    ASSETS["ui_icon"] = ui_icon

    return ASSETS