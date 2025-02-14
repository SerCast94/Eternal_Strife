# Eternal Strife (En Desarrollo)

**Eternal Strife** es un videojuego 2D de supervivencia y oleadas de enemigos desarrollado en Python utilizando la librería **PyGame**. Enfréntate a hordas de enemigos mientras mejoras tus habilidades y sobrevives el mayor tiempo posible.

## Estado Actual

### Características Implementadas:

-   **Menú Principal**: Menú con botones y fondo animado, que incluye la capacidad de controlar la velocidad del planeta.
-   **Generación de Mapas**: Implementación de un sistema de **tiles** para generar el entorno del juego, optimizando la creación de niveles.
-   **Lógica de Juego**:
    -   Movimiento del jugador y sistema básico de colisiones.
    -   **Puntuación**: Sistema de puntuaciones con opción de volver al menú principal.
    -   **Pantalla de Carga**: Con estrellas para mejorar la experiencia visual al iniciar el juego.
    -   **Dificultad Dinámica**: Los enemigos aumentan en cantidad y/o velocidad conforme avanza el tiempo.
-   **Enemigos**:
    -   Sistema de generación de enemigos con distintos comportamientos.
    -   Uso de **multihilo** para la lógica de los enemigos, lo que mejora la fluidez del movimiento y las interacciones.
    -   **Particionamiento espacial** para calcular las colisiones de los enemigos (aún en proceso de optimización).


## Características

-   **Movimiento del jugador**: Controla al jugador en cuatro direcciones con el teclado.
-   **Ataque automático**: El jugador puede atacar de forma automática con proyectiles o área de efecto.
-   **Sistema de salud**: La salud del jugador disminuye al recibir daño de los enemigos.
-   **Generación de enemigos**: Los enemigos aparecen de forma continua, moviéndose hacia el jugador.
-   **Puntuación**: El puntaje se basa en el tiempo sobrevivido o los enemigos derrotados.

## Tecnologías

-   **Lenguaje de Programación**: Python.
-   **Biblioteca Gráfica**: PyGame.
-   **Manejo de Sonido**: PyGame.mixer.
-   **Control de Versiones**: Git
-   **Manejo de datos y gráficas**: Matplotlib
-   **Manejo de imágenes**: Manejo de imágenes

## Librerías

Mientras implementamos un sistema de instalación automatico de librerías, ahora mismo necesitan ser instaladas manualmente.:
```bash
pip install pygame matplotlib pillow
```
