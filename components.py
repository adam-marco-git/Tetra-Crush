import random
import sys
import pygame
import csv
import matplotlib.pyplot as plt
import numpy as np
import time

# --- Initialize Pygame --- 
pygame.init()
clock = pygame.time.Clock()


# --- Constants ---
GRID_WIDTH, GRID_HEIGHT = 300, 650
UI_WIDTH = 220
WINDOW_WIDTH, WINDOW_HEIGHT = (UI_WIDTH + GRID_WIDTH + 80), (GRID_HEIGHT + 40)
COLS, ROWS = 10, 20
CELL_SIZE = GRID_WIDTH // COLS
TITLE_FONT  = pygame.font.Font("ARCADECLASSIC.ttf", 40)
confetti = []

GRID = [[0 for _ in range(COLS)] for _ in range(ROWS)]
global SCORE

# --- Screen ---
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# --- Game Over Image ---
GAME_OVER_IMG = pygame.image.load('GameOver.png').convert_alpha()

# --- SCORE ---
SCORE=0
# --- Grid Origin Offsets ---
# These must match the drawing offsets in tetra_crush.py
GRID_OFFSET_X = 30  # horizontal offset where grid starts on screen
GRID_OFFSET_Y = 60  # vertical offset where grid starts on screen


# --- Confetti Class and Method ---
class Confetti:
    def __init__(self,x,y,color,speed):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.direction = random.choice([-1, 1]) 
        self.size = random.randint(10, 15)
        self.gravity = 0.5  
    def update(self):
          self.y += self.speed
          self.x += self.direction * random.randint(1, 3)
          self.speed += self.gravity
    def draw(self):
          pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

def throw_confetti():
        for _ in range(100):  # Create 100 confetti pieces
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT // 2)
            color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)])
            speed = random.randint(3, 6)
            confetti.append(Confetti(x, y, color, speed))

# --- Block Variables ---
BLUE = (51, 51, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 0, 255)
PURPLE = (153,51, 255)
YELLOW = (255, 255, 51)
ORANGE = (255, 128, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (169, 169, 169)
BLOCK_COLORS = [
      BLUE,
      RED,
      PURPLE,
      GREEN,
      PINK,
      BLUE,
      ORANGE
]

BLOCKS = {
      'O': [[(1, 1), (1, 2), (2, 1), (2, 2)]],
      'I': [[(0, 1), (1, 1), (2, 1), (3, 1)],
            [(1, 0), (1, 1), (1, 2), (1, 3)],
            [(0, 2), (1, 2), (2, 2), (3, 2)],
            [(2, 0), (2, 1), (2, 2), (2, 3)]],
      'T': [[(0, 1), (1, 0), (1, 1), (1, 2)],
            [(0, 1), (1, 1), (1, 2), (2, 1)],
            [(1, 0), (1, 1), (1, 2), (2, 1)],
            [(0, 1), (1, 0), (1, 1), (2, 1)]],
      'L': [[(2, 2), (1, 0), (1, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (2, 0)],
            [(1, 0), (1, 1), (1, 2), (0, 0)],
            [(0, 1), (1, 1), (2, 1), (0, 2)]],
      'J': [[(0, 2), (1, 0), (1, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (2, 2)],
            [(1, 0), (1, 1), (1, 2), (2, 0)],
            [(0, 1), (1, 1), (2, 1), (0, 0)]],
      'S': [[(1, 0), (1, 1), (0, 1), (0, 2)],
            [(0, 1), (1, 1), (1, 2), (2, 2)],
            [(1, 2), (1, 1), (2, 1), (2, 0)],
            [(0, 0), (1, 0), (1, 1), (2, 1)]],
      'Z': [[(0, 0), (0, 1), (1, 1), (1, 2)],
            [(0, 2), (1, 2), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (2, 1), (2, 2)],
            [(0, 1), (1, 1), (1, 0), (2, 0)]]
}

# --- Scoring System ---
class Score:
    def clear_and_score(grid):
        lines = []
        # detect full rows
        for r in range(len(grid)):
            if all(grid[r][c] != 0 for c in range(len(grid[0]))):
                lines.append(('row', r))
        # detect full columns
        for c in range(len(grid[0])):
            if all(grid[r][c] != 0 for r in range(len(grid))):
                lines.append(('col', c))
        # clear detected lines
        for typ, val in lines:
            if typ == 'row':
                for c in range(len(grid[0])):
                    grid[val][c] = 0
            elif typ == 'col':
                for r in range(len(grid)):
                    grid[r][val] = 0
        # calculate score
        count = len(lines)
        base = 10 * count
        bonus_table = [0, 0, 30, 40, 50, 60, 70, 80, 90, 100]
        bonus = bonus_table[count] if count < len(bonus_table) else 100
        total = base + bonus

        return count, total

# --- Button System ---
class Button:
    def __init__(self, rect, text, font, bg_color, text_color):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.preview = False

        # Prepare the rendered text surface once
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        if self.bg_color is not None:
            pygame.draw.rect(surface, self.bg_color, self.rect)
        surface.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))

# --- Block System ---
class Block:
    def __init__(self, block_type, rotation_state):
        self.block_type = block_type
        self.color = random.choice(BLOCK_COLORS)
        self.rotation_state = rotation_state
        self.coordinates = BLOCKS[self.block_type][self.rotation_state]
        self.xPixel_movement = 0
        self.yPixel_movement = 0
        self.dragging = False
        self.preview = False
        self.dropped_x = 0
        self.dropped_y = 0
        self.preview_rect = None

    def place_block(self, screen, preview=False, rect=None):
        if not preview:
            for x, y in self.coordinates:
                x_pixel = self.xPixel_movement + x * CELL_SIZE
                y_pixel = self.yPixel_movement + y * CELL_SIZE
                pygame.draw.rect(screen, self.color, (x_pixel, y_pixel, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, BLACK, (x_pixel, y_pixel, CELL_SIZE, CELL_SIZE), 1)
        else:
            self.preview = True
            size = CELL_SIZE // 2.5
            min_x = min(px for px, _ in self.coordinates)
            min_y = min(py for _, py in self.coordinates)
            max_x = max(px for px, _ in self.coordinates)
            max_y = max(py for _, py in self.coordinates)
            block_width = (max_x - min_x + 1) * size
            block_height = (max_y - min_y + 1) * size
            self.offset_x = rect.x + (rect.width - block_width) // 2 - min_x * size
            self.offset_y = rect.y + (rect.height - block_height) // 2 - min_y * size
            for x, y in self.coordinates:
                x_px = self.offset_x + x * size
                y_px = self.offset_y + y * size
                pygame.draw.rect(screen, self.color, (x_px, y_px, size, size))
                pygame.draw.rect(screen, BLACK, (x_px, y_px, size, size), 1)

    def drag_drop(self, get_events, GRID):
        for event in get_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                xMouse, yMouse = event.pos
                if self.preview:
                    size = CELL_SIZE // 2.5
                    for x, y in self.coordinates:
                        x_pixel = self.offset_x + x * size
                        y_pixel = self.offset_y + y * size
                        rect = pygame.Rect(x_pixel, y_pixel, size, size)
                        if rect.collidepoint(xMouse, yMouse):
                            self.dragging = True
                            self.offset_x = xMouse - x_pixel
                            self.offset_y = yMouse - y_pixel
                    self.xPixel_movement = xMouse - self.offset_x
                    self.yPixel_movement = yMouse - self.offset_y
                else:
                    for x, y in self.coordinates:
                        x_pixel = self.xPixel_movement + x * CELL_SIZE
                        y_pixel = self.yPixel_movement + y * CELL_SIZE
                        rect = pygame.Rect(x_pixel, y_pixel, CELL_SIZE, CELL_SIZE)
                        if rect.collidepoint(xMouse, yMouse):
                            self.dragging = True
                            self.offset_x = xMouse - self.xPixel_movement
                            self.offset_y = yMouse - self.yPixel_movement
                            break



            elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
                self.dragging = False
                # Compute grid position
                xSnap = round((self.xPixel_movement - GRID_OFFSET_X) / CELL_SIZE)
                ySnap = round((self.yPixel_movement - GRID_OFFSET_Y) / CELL_SIZE)
                # Determine block bounds for edge placement
                min_x = min(px for px, _ in self.coordinates)
                max_x = max(px for px, _ in self.coordinates)
                min_y = min(py for _, py in self.coordinates)
                max_y = max(py for _, py in self.coordinates)
                # Clamp to valid range
                xSnap = max(-min_x, min(COLS - 1 - max_x, xSnap))
                ySnap = max(-min_y, min(ROWS - 1 - max_y, ySnap))
                # Check explicitly for collision with existing blocks
                collision = False
                try:
                    for px, py in self.coordinates:
                        gridx = xSnap + px
                        gridy = ySnap + py
                        if gridx < 0 or gridx >= COLS or gridy < 0 or gridy >= ROWS or GRID[gridy][gridx] != 0:
                            collision = True
                            break
                except IndexError:
                    self.preview = True
                    self.dragging = True
                    if self.preview_rect:
                        self.xPixel_movement = self.preview_rect.x
                        self.yPixel_movement = self.preview_rect.y
                    return False
                if collision:
                    self.preview = True
                    self.dragging = True
                    if self.preview_rect:
                        self.xPixel_movement = self.preview_rect.x
                        self.yPixel_movement = self.preview_rect.y
                    return False

                else:
                    self.xPixel_movement = xSnap * CELL_SIZE + GRID_OFFSET_X
                    self.yPixel_movement = ySnap * CELL_SIZE + GRID_OFFSET_Y
                    self.dropped_x = xSnap
                    self.dropped_y = ySnap
                    # Place block into grid
                    for px, py in self.coordinates:
                        GRID[ySnap + py][xSnap + px] = self.color
                    self.placed = True
                    return True
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                xMouse, yMouse = event.pos
                self.xPixel_movement = xMouse - self.offset_x
                self.yPixel_movement = yMouse - self.offset_y


# --- Leaderboard System ---
class Leaderboard:
    def __init__(self,font):
        self.font = font

    def leaderboard_ui(self, scores, x, y):
        lb_border = pygame.Rect(x, y, 210, 300)
        pygame.draw.rect(screen, WHITE, lb_border, 2)

    def load_leaderboard(self, filename='leaderboard.csv'):
        scores = []
        try:
            with open(filename, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    # skip blank rows or rows too short
                    if len(row) <= 2:
                        continue

                    name, score_str = row[0], row[1]
                    try:
                        score = int(score_str)
                    except ValueError:
                        # this skips the header ("Score") or any bad data
                        continue

                    scores.append((name, score))
        except FileNotFoundError:
            print(f"⚠️ {filename} not found, starting fresh.")
        return scores

    def log_session(self,
                    player_name,
                    player_score,
                    blocks_placed,
                    squares_filled,
                    lines_cleared,
                    filename='leaderboard.csv'):
        """
        Append one row, then reload + sort descending by score
        """
        try:
            # 1) append the new row
            with open(filename, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    player_name,
                    player_score,
                    blocks_placed,
                    squares_filled,
                    lines_cleared
                ])
        except Exception as e:
            print(f"Could not write session data: {e}")
            return

        try:
            # 2) read back all valid rows
            rows = []
            with open(filename, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2 and row[1].isdigit():
                        rows.append(row)

            # 3) build (score_int, row) pairs
            pairs = []
            for row in rows:
                score_int = int(row[1])
                pairs.append((score_int, row))

            # 4) sort pairs by score_int descending
            pairs.sort(reverse=True)

            # 5) extract sorted rows
            sorted_rows = [pair[1] for pair in pairs]

            # 6) overwrite CSV with sorted_rows
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(sorted_rows)

        except Exception as e:
            print(f"Could not sort leaderboard: {e}")

    def sort_game_scores(self, scores):
        """
        Recursively sort the list of (name, score) tuples
        in descending order by score (quicksort style).
        """
        if len(scores) <= 1:
            return scores
        pivot = scores[0]
        greater = [e for e in scores[1:] if e[1] > pivot[1]]
        lesser = [e for e in scores[1:] if e[1] <= pivot[1]]
        return self.sort_game_scores(greater) + [pivot] + self.sort_game_scores(lesser)


    def plot_scores(self, filename='leaderboard.csv'):
            try:
                with open(filename,'r+', newline='') as file:
                    reader = csv.reader(file)
                    data = []
                    for row in reader:
                        if len(row) >= 3 and row[0].strip() != 'Name':
                            data.append(row)
                    sorted_data = sorted(data, key=lambda row: int(row[1]), reverse=True)
                    plot_scores = sorted_data[0:]
                    placed, scores, names = [], [], []
                    for row in plot_scores:
                        names.append(row[0])
                        placed.append(int(row[2]))
                        scores.append(int(row[1]))

                    fig_width = WINDOW_WIDTH / 100
                    fig_height = WINDOW_HEIGHT / 100
                    plt.figure(figsize=(fig_width, fig_height), dpi=100)
                    plt.scatter(placed,scores,color='black')
    
                    for i, text in enumerate(names):
                        plt.text(placed[i] + .1, scores[i] + .1, text, fontsize=9,ha='left',color='blue')

                    plt.title('Top Scores vs. Blocks Placed')
                    plt.xlabel('Blocks Placed')
                    plt.ylabel('Scores')

                    plt.savefig('Highscore_plot.png')
                    plt.close()
            except FileNotFoundError:
                print(f" {filename} not found, starting fresh.")

class PlayerNamePrompt:
    def __init__(self, screen, font, fg=WHITE, bg=BLACK):
        self.screen = screen
        self.font   = font
        self.fg     = fg
        self.bg     = bg

    def get_name(self):
        name = ""
        clock = pygame.time.Clock()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        return name.strip() or "Player"
                    elif e.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += e.unicode

            # draw prompt
            self.screen.fill(self.bg)
            prompt_surf = self.font.render("Enter your name", True, self.fg)
            name_surf   = self.font.render(name, True, self.fg)
            pw, ph      = prompt_surf.get_size()
            nw, nh      = name_surf.get_size()
            midx        = WINDOW_WIDTH // 2
            self.screen.blit(prompt_surf, (midx - pw//2, WINDOW_HEIGHT//3))
            self.screen.blit(name_surf,   (midx - nw//2, WINDOW_HEIGHT//3 + ph + 10))

            pygame.display.flip()
            clock.tick(30)
def any_valid_moves(preview_queue, grid):
    """
    Return True if at least one block in preview_queue can be placed
    in any orientation somewhere on the grid.
    """
    rows, cols = len(grid), len(grid[0])
    for block in preview_queue:
        # Try every rotation for this block
        for shape in BLOCKS[block.block_type]:
            # Determine shape bounds
            max_x = max(px for px, _ in shape)
            max_y = max(py for _, py in shape)
            # Slide shape over grid
            for y in range(rows - max_y):
                for x in range(cols - max_x):
                    if all(
                        grid[y + py][x + px] == 0
                        for px, py in shape
                    ):
                        return True
    return False

def game_over():
    img = pygame.transform.scale(GAME_OVER_IMG, screen.get_size())
    screen.blit(img, (0, 0))
    pygame.display.flip()




