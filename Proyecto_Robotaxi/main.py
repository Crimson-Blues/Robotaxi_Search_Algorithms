# main.py
from hmac import new
import pygame
import sys
import os
from utilities import *
from busquedas import amplitud, utilidades, profundidad, ucs, a_estrella, avara
from modelos import UIElement
from pygame.sprite import Sprite
import tkinter as tk
from tkinter import filedialog

# Variable Global de Assets (Guarda imágenes cargadas a memoria)
ASSETS = {}


def main():
    global ASSETS
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

    ASSETS = load_assets()
    bg_img = ASSETS["bg_img"]
    bg2_img = ASSETS["bg2_img"]
    bg3_img = ASSETS["bg3_img"]
    ui_icon = ASSETS["ui_icon"]

    panel_center_x = 250 
    true_center_x = 450

    # Buttons for choosing search algorithm
    back_button = {
            "ui": UIElement((44, 24), "<-", 15, (40, 44, 52), (158, 155, 155)),
            "funct": lambda: initial_menu_with_wrld()
        }
    buttons_algs = {
        "selection": [
            {
                "ui": UIElement((panel_center_x, 277), "BÚSQUEDA NO\nINFORMADA", 20, (40, 44, 52), (255, 170, 0), text_style="PLAIN"),
                "funct": lambda: non_informed_menu()
            },
            {
                "ui": UIElement((panel_center_x, 399), "BÚSQUEDA\nINFORMADA", 20, (40, 44, 52), (255, 170, 0), text_style="PLAIN"),
                "funct": lambda: informed_menu()
            }
        ],
        "not_informed": [
        {
            "ui": UIElement((panel_center_x, 256), "Amplitud", 25, (40, 44, 52), (255, 170, 0), text_style="PLAIN"),
            "algo": amplitud.buscar # Calls on the amplitude search algorithm
        },
        {
            "ui": UIElement((panel_center_x, 341), "Profundidad", 25, (40, 44, 52), (255, 170, 0), text_style="PLAIN"),
            "algo": profundidad.buscar # Calls on the depth search algorithm
        },
        {
            "ui": UIElement((panel_center_x, 423), "Costo Uniforme", 25, (40, 44, 52), (255, 170, 0), text_style="PLAIN"),
            "algo": ucs.buscar # Calls on the cost search algorithm
        }
        ],
        "informed": [
        {
            "ui": UIElement((panel_center_x, 278), "A Estrella", 25, (40, 44, 52), (255, 170, 0), text_style="PLAIN"),
            "algo": a_estrella.buscar # Calls on the A* search algorithm
        },
        {
            "ui": UIElement((panel_center_x, 397), "Avara", 25, (40, 44, 52), (255, 170, 0), text_style="PLAIN"),
            "algo": avara.buscar # Calls on the Greedy Best-First Search algorithm
        }
        ]

    }

    titles_algs = [
        {
            "ui": UIElement((panel_center_x, 173), "BÚSQUEDA NO\nINFORMADA ", 22, (40, 44, 52), (255, 255, 255), text_style="PLAIN"),
            "funct": lambda: None
        },
        {
            "ui": UIElement((panel_center_x, 169), "BÚSQUEDA\nINFORMADA ", 22, (40, 44, 52), (255, 255, 255), text_style="PLAIN"),
            "funct": lambda: None
        }
    ]

    tipo_algs_title = {
        "ui": UIElement((panel_center_x, 169), "ALGORITMOS DE\nBÚSQUEDA", 22, (40, 44, 52), (255, 255, 255), text_style="PLAIN"),
        "funct": lambda: None
    }

    buttons_initial_center = [
        {
            "ui": UIElement((true_center_x, 250), "Seleccionar Mundo", 25, (40, 44, 52), (255, 170, 0)),
            "funct": lambda: update_file(select_file()) # Select custom File
        },
        {
            "ui": UIElement((true_center_x, 320), "Usar ejemplo", 18, (40, 44, 52), (230, 245, 255)),
            "funct": lambda: update_file("Prueba1.txt") # Use example file
        }
    ]

    buttons_initial_left = [
        {
            "ui": UIElement((300, 250), "Seleccionar Mundo", 25, (40, 44, 52), (255, 170, 0)),
            "funct": lambda: update_file(select_file())
        },
        {
            "ui": UIElement((300, 320), "Usar ejemplo", 18, (40, 44, 52), (230, 245, 255)),
            "funct": lambda: update_file("Prueba1.txt")
        },
        {
            "ui": UIElement((685, 200), "X", 15, (40, 44, 52), (255, 60, 60), text_style="PLAIN"),
            "funct": lambda: initial_menu_no_wrld()
        },
        {
            "ui": UIElement((600, 390), "Correr Simulación", 23, (40, 44, 52), (255, 170, 0), text_style="PLAIN"),
            "funct": lambda: alg_selection_menu()
        }
    ]

    simulation_btns_dx = 75
    simulation_btns_y = 550

    buttons_simulation = [
        {
            "ui": UIElement((true_center_x, simulation_btns_y), "▶", 25, (40, 44, 52), (255, 170, 0), alt_text = "⏸",
                            alt_flag = (lambda: (estado_simulacion == "PLAY"))),
            "funct": lambda: play_btn_func()
        },
        {
            "ui": UIElement((true_center_x - simulation_btns_dx, simulation_btns_y), "<-", 18, (40, 44, 52), (230, 245, 255)),
            "funct": lambda: rewind_btn_func()
        },
        {
            "ui": UIElement((true_center_x + simulation_btns_dx, simulation_btns_y), "->", 15, (40, 44, 52), (255, 60, 60)),
            "funct": lambda: forward_btn_func()
        },
    ]


    estado_actual = "MENU INICIAL SIN MUNDO" # Initial menu state
    estado_simulacion = "PLAY" # Initial simulation playback settings
    playback_speed = 100
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

    def simulation():
        nonlocal button_list, estado_actual
        estado_actual = "SIMULACION"
        button_list = buttons_simulation


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
        initial_menu_with_wrld()

    def play_btn_func():
        nonlocal estado_simulacion
        nonlocal playback_speed
        if estado_simulacion == "PAUSE":
            estado_simulacion = "PLAY"
            playback_speed = 100
        else:
            estado_simulacion = "PAUSE"

    def rewind_btn_func():
        nonlocal estado_simulacion
        nonlocal playback_speed
        if estado_simulacion == "PLAY":
            estado_simulacion = "REWIND"
            playback_speed = 100
        elif estado_simulacion == "PAUSE":
            simulation_step_bck()

    def forward_btn_func():
        nonlocal estado_simulacion
        nonlocal playback_speed
        if estado_simulacion == "PLAY":
            playback_speed = 50
        elif estado_simulacion == "PAUSE":
            simulation_step_fwd()
        elif estado_simulacion == "REWIND":
            estado_simulacion = "PLAY"
            playback_speed = 50

    # Helper function for simulation steps::

    def simulation_step_fwd():
        nonlocal map_matrix
        nonlocal path_index
        nonlocal move_timer
        if path and path_index < len(path):
            direction = path[path_index]
            if direction == 'Up': current_taxi_pos[0] -= 1
            elif direction == 'Down': current_taxi_pos[0] += 1
            elif direction == 'Left': current_taxi_pos[1] -= 1
            elif direction == 'Right': current_taxi_pos[1] += 1
                
            if map_matrix[current_taxi_pos[0]][current_taxi_pos[1]] == 4:
                map_matrix[current_taxi_pos[0]][current_taxi_pos[1]] = 0
                
            path_index += 1


    def simulation_step_bck():
        nonlocal map_matrix
        nonlocal path_index
        nonlocal move_timer
        if path and path_index > 0:
            direction = path[path_index -1]
            if direction == 'Up': current_taxi_pos[0] += 1
            elif direction == 'Down': current_taxi_pos[0] -= 1
            elif direction == 'Left': current_taxi_pos[1] += 1
            elif direction == 'Right': current_taxi_pos[1] -= 1
                
            if map_matrix_original[current_taxi_pos[0]][current_taxi_pos[1]] == 4:
                map_matrix[current_taxi_pos[0]][current_taxi_pos[1]] = 4
                
            path_index -= 1


    while True:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    alg_selection_menu()
                    path_index = 0
                    move_timer = 0
                    path = []
                    map_matrix = [row[:] for row in map_matrix_original] # Restart map_matrix 

            
            # --- DYNAMIC CLICK DETECTION ---
            if event.type == pygame.MOUSEBUTTONDOWN:

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
                            simulation()
                        elif "funct" in btn:
                            btn["funct"]()

                if current_title:
                    if current_title["ui"].rect.collidepoint(mouse_pos):
                        current_title["funct"]()

                if back_button["ui"].rect.collidepoint(mouse_pos):
                    if estado_actual == "MENU SELECCION ALGORITMO":
                        initial_menu_with_wrld()
                    else:
                        alg_selection_menu()
                        


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
                draw_world_preview(screen, map_matrix, CELL_SIZE, offset_x=448, offset_y=127, ASSETS=ASSETS)

        # if "MENU" in estado_actual:
        for btn in button_list:
            btn["ui"].update(mouse_pos)
            btn["ui"].draw(screen)

        # if "MENU " in estado_actual or estado_actual == "SIMULACION":
        draw_text(screen, "ROBOTAXI ZOOX", (true_center_x + 3, 46), size=55, color=(40, 30, 0))
        draw_text(screen, "ROBOTAXI ZOOX", (true_center_x, 43), size=55, color=(255, 170, 0))
            
        # Sólo lo mostramos cuando el mundo está vacío para que no estrelle con el minimapa!
        if estado_actual == "MENU INICIAL SIN MUNDO":
            if ui_icon:
                icon_rect = ui_icon.get_rect(center=(true_center_x, 400))
                screen.blit(ui_icon, icon_rect)

        if estado_actual == "MENU INICIAL CON MUNDO":
            draw_world_preview(screen, map_matrix, 150/len(map_matrix[0]), offset_x=600-75, offset_y=210, ASSETS=ASSETS)


        elif estado_actual == "SIMULACION":
            move_timer += dt
            if move_timer > playback_speed and estado_simulacion == "PLAY": # Playback animation speed
                simulation_step_fwd()
                move_timer = 0

            if move_timer > playback_speed and estado_simulacion == "REWIND": # Playback animation speed
                simulation_step_bck()
                move_timer = 0

            draw_world(screen, map_matrix, current_taxi_pos, CELL_SIZE, offset_x=448, offset_y=127, ASSETS=ASSETS)
            
            if path and path_index >= len(path):
                draw_results_window(screen, success=True, **datos_finales)

            if path is None:
                draw_results_window(screen, success=False, **datos_finales)

        pygame.display.flip()

#Run main function
if __name__ == "__main__":
    main()