import pygame
import sys
import time
from collections import deque

# Configurações
TILE_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WIDTH = TILE_SIZE * GRID_WIDTH
HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (160, 160, 160)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Mapa do labirinto (0 = caminho livre, 1 = parede)
maze = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Exemplo de paredes
for i in range(5, 25):
    maze[10][i] = 1
maze[10][15] = 0  # abertura no meio

# Ponto inicial e final
start = (5, 5)
end = (15, 15)

def draw_grid(screen, distances):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, rect)
            elif distances[y][x] > 0:
                pygame.draw.rect(screen, (255 - distances[y][x]*10, 255 - distances[y][x]*5, 200), rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)
    pygame.draw.rect(screen, GREEN, (*[i * TILE_SIZE for i in start], TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (*[i * TILE_SIZE for i in end], TILE_SIZE, TILE_SIZE))

def wavefront(screen):
    distances = [[-1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    queue = deque()
    queue.append(end)
    distances[end[1]][end[0]] = 1

    while queue:
        x, y = queue.popleft()
        draw_grid(screen, distances)
        pygame.display.flip()
        time.sleep(0.02)

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if maze[ny][nx] == 0 and distances[ny][nx] == -1:
                    distances[ny][nx] = distances[y][x] + 1
                    queue.append((nx, ny))

    return distances

def trace_path(screen, distances):
    path = []
    x, y = start
    if distances[y][x] == -1:
        print("Caminho não encontrado")
        return

    while (x, y) != end:
        path.append((x, y))
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if distances[ny][nx] == distances[y][x] - 1:
                    x, y = nx, ny
                    break

    for (x, y) in path:
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, YELLOW, rect)
        pygame.display.flip()
        time.sleep(0.05)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Wavefront Maze Solver (de trás para frente)")
    clock = pygame.time.Clock()

    distances = wavefront(screen)
    trace_path(screen, distances)

    # Espera até fechar
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
