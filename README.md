# Robotaxi Zoox
Un simulador interactivo construido con **Pygame** que visualiza en tiempo real el comportamiento de diversos algoritmos de búsqueda (Informada y No Informada). 

## Características
* **Búsqueda No Informada:** Amplitud, Profundidad y Costo Uniforme.
* **Búsqueda Informada:** A* y Avara.
* **Interfaz Gráfica:** Animaciones del recorrido y métricas finales (nodos expandidos, profundidad, costo total y tiempo de cómputo).
* **Mapas Personalizados:** Carga de mundos personalizados a través de archivos `.txt`.

## Requisitos Previos
Asegúrate de tener instalado [Python](https://www.python.org/downloads/) en tu sistema. (Se recomienda una versión estable como **Python 3.12**).

## Instalación y Ejecución
Sigue estos pasos para clonar y ejecutar el proyecto en tu máquina local de forma segura utilizando un entorno virtual.

### 1. Clonar el repositorio
Abre tu terminal y ejecuta: 
```bash
git clone https://github.com/Crimson-Blues/Robotaxi_Search_Algorithms.git
cd .\Robotaxi_Search_Algorithms\
```
### 2. Crear un entorno virtual
Para evitar conflictos con otras librerías de tu sistema, crea un entorno virtual (venv):
```bash
python -m venv venv
```
O en algunos equipos:
```bash
py -m venv venv
```

### 3. Activar el entorno virtual
* **En Windows:**
  ```bash
  .\venv\Scripts\activate
  ```
* **En macOS y Linux:**
  ```bash
  source venv/bin/activate
  ```
### 4. Instalar las dependencias
Con el entorno activado, instala la versión de Pygame requerida:
```bash
pip install -r requirements.txt
```

### 5. Iniciar la simulación
Finalmente, navega hasta la carpeta de código y ejecuta el archivo principal 
```bash
cd .\Proyecto_Robotaxi\
python main.py
```
O:
```bash
cd .\Proyecto_Robotaxi\
py main.py
```

## Cómo usar
1. Al iniciar, selecciona **"Seleccionar Mundo"** para cargar un archivo `.txt` de configuración, o usa el archivo de prueba por defecto.
2. Haz clic en **"Correr Simulación"**.
3. Elige el tipo de algoritmo que deseas visualizar (Informado o No Informado).
4. Selecciona el algoritmo específico.
5. Observa cómo el Robotaxi encuentra el camino óptimo. Al terminar, presiona `ESC` para volver al menú de selección.
