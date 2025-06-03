import pygame
import asyncio
import random
import platform
import time
from collections import deque

# Configurações
TILE_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
WIDTH = TILE_SIZE * GRID_WIDTH
HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (160, 160, 160)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
VERDE = (0, 200, 155)  # Cor do menor caminho

# Ponto inicial e final
start = (0, 0)
end = (29, 29)

# Função para verificar se o labirinto é solucionável
def is_maze_solvable(walls):
    distances = [[-1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    queue = deque([end])
    distances[end[1]][end[0]] = 1

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                edge = tuple(sorted([(x, y), (nx, ny)]))
                if edge not in walls and distances[ny][nx] == -1:
                    distances[ny][nx] = distances[y][x] + 1
                    queue.append((nx, ny))
    
    return distances[start[1]][start[0]] != -1

# Gera mapa do labirinto com paredes como linhas
def generate_maze():
    random.seed(time.time())  # Garante labirintos diferentes
    walls = set()  # Conjunto de arestas (paredes) entre células
    # Adiciona paredes aleatórias (30% das arestas possíveis)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            for dx, dy in [(1,0), (0,1)]:  # Apenas direitas e abaixo para evitar duplicatas
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    if random.random() < 0.50:  # Aumentado para 50%
                        edge = tuple(sorted([(x, y), (nx, ny)]))
                        if (x, y) not in [start, end] and (nx, ny) not in [start, end]:
                            walls.add(edge)
    # Verifica se o labirinto é solucionável
    if not is_maze_solvable(walls):
        return generate_maze()
    return walls

# Inicializa o labirinto
walls = generate_maze()

def draw_grid(screen, distances, font):
    screen.fill(WHITE)
    # Desenha as células e números
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if distances[y][x] > 0:
                # Corrige os valores RGB para ficarem no intervalo [0, 255]
                r = max(0, min(255, 255 - distances[y][x] * 2))
                g = max(0, min(255, 255 - distances[y][x] * 2))
                b = 255
                pygame.draw.rect(screen, (r, g, b), rect)
                # Desenha o número da distância
                if font:
                    text = font.render(str(distances[y][x]), True, BLACK)
                    text_rect = text.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
                    screen.blit(text, text_rect)
            pygame.draw.rect(screen, GRAY, rect, 1)
    
    # Desenha as paredes como linhas negras
    for (x1, y1), (x2, y2) in walls:
        start_pos = (x1 * TILE_SIZE + (TILE_SIZE if x2 > x1 or y2 > y1 else 0), y1 * TILE_SIZE + (TILE_SIZE if y2 > y1 else 0))
        end_pos = (x2 * TILE_SIZE + (0 if x2 > x1 or y2 > y1 else TILE_SIZE), y2 * TILE_SIZE + (0 if y2 > y1 else TILE_SIZE))
        pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
    
    # Desenha os pontos inicial e final
    pygame.draw.rect(screen, GREEN, (*[i * TILE_SIZE for i in start], TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (*[i * TILE_SIZE for i in end], TILE_SIZE, TILE_SIZE))

async def wavefront(screen, font):
    distances = [[-1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    queue = deque([end])
    distances[end[1]][end[0]] = 1

    while queue:
        x, y = queue.popleft()
        # Para quando alcançar o ponto inicial
        if (x, y) == start:
            break
        draw_grid(screen, distances, font)
        pygame.display.flip()
        await asyncio.sleep(0.01)

        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                edge = tuple(sorted([(x, y), (nx, ny)]))
                if edge not in walls and distances[ny][nx] == -1:
                    distances[ny][nx] = distances[y][x] + 1
                    queue.append((nx, ny))
    
    return distances

async def trace_path(screen, distances, font):
    path = []
    x, y = start
    if distances[y][x] == -1:
        print("Caminho não encontrado")
        return

    # Construir o caminho do início ao fim
    while (x, y) != end:
        path.append((x, y))
        min_distance = float('inf')
        next_pos = None
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                edge = tuple(sorted([(x, y), (nx, ny)]))
                if edge not in walls and distances[ny][nx] != -1 and distances[ny][nx] < min_distance:
                    min_distance = distances[ny][nx]
                    next_pos = (nx, ny)
        if next_pos is None:
            print("Erro ao traçar o caminho")
            return
        x, y = next_pos
    path.append(end)  # Inclui o ponto final

    # Redesenha o labirinto
    draw_grid(screen, distances, font)
    pygame.display.flip()
    await asyncio.sleep(0.1)

    # Desenha o caminho em azul como pequenos círculos para preservar números
    for (x, y) in path:
        center = (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)
        pygame.draw.circle(screen, VERDE, center, TILE_SIZE // 3)  # Círculo menor
        # Redesenha as paredes
        for (x1, y1), (x2, y2) in walls:
            start_pos = (x1 * TILE_SIZE + (TILE_SIZE if x2 > x1 or y2 > y1 else 0), y1 * TILE_SIZE + (TILE_SIZE if y2 > y1 else 0))
            end_pos = (x2 * TILE_SIZE + (0 if x2 > x1 or y2 > y1 else TILE_SIZE), y2 * TILE_SIZE + (0 if y2 > y1 else TILE_SIZE))
            pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
        # Redesenha início e fim
        pygame.draw.rect(screen, GREEN, (*[i * TILE_SIZE for i in start], TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, RED, (*[i * TILE_SIZE for i in end], TILE_SIZE, TILE_SIZE))
        # Redesenha o número na célula atual para garantir visibilidade
        if font and distances[y][x] > 0:
            text = font.render(str(distances[y][x]), True, BLACK)
            text_rect = text.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
            screen.blit(text, text_rect)
        pygame.display.flip()
        await asyncio.sleep(0.05)

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BFS Maze Solver (de trás para frente)")
    font = pygame.font.SysFont('arial', 12)  # Fonte para os números
    
    # Executa o algoritmo BFS e traça o caminho
    distances = await wavefront(screen, font)
    await trace_path(screen, distances, font)

    # Mantém a janela aberta até o usuário fechar
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())