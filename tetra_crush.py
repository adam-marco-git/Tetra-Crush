
import subprocess
from components import *

# --- Initialize Pygame ---
pygame.init()
pygame.display.set_caption("Tetra Crush")

# --- Custom Fonts ---
custom_font = pygame.font.Font("ARCADECLASSIC.ttf", 24)
TIMER_FONT  = pygame.font.Font("ARCADECLASSIC.ttf", 30)
TITLE_FONT  = pygame.font.Font("ARCADECLASSIC.ttf", 40)
SCORE_FONT  = pygame.font.Font("ARCADECLASSIC.ttf", 40)
lb_font = pygame.font.Font("ARCADECLASSIC.ttf", 18)

# --- Prompt for player name via Pygame ---
prompt     = PlayerNamePrompt(screen, custom_font)
PLAYER_NAME = prompt.get_name()

# --- Leaderboard instance ---
lb = Leaderboard(custom_font)
# --- Grid Constants ---
TOP_MARGIN = 60
SHRINK_INTERVAL = 5
rect_width, rect_height = 150, 60
rect_x, rect_y = (UI_WIDTH + rect_width) , rect_height

# --- Generates a random block ---
class RandomBlock(Block):
      """Inherits from the Block class"""
      def __init__(self):
        blocklist = ['O', 'I', 'T', 'L', 'J', 'S', 'Z']
        block_type = random.choice(blocklist)
        rotation_state = random.choice(range(len(BLOCKS[block_type])))
        super().__init__(block_type, rotation_state)


# --- Buttons ---
exit_button = Button(
    rect=(10, 10, 50, 25),
    text="EXIT",
    font=custom_font,
    bg_color=WHITE,
    text_color=BLACK)


# --- Grid Variables ---
MOVES = 0
START_TIME = pygame.time.get_ticks()
TOTAL_LINES_CLEARED = 0
TOTAL_BLOCKS_PLACED = 0
TOTAL_SQUARES_FILLED = 0
# --- Labels UI ---
def labels(self):
    """Timer counter"""
    elapsed_time = (pygame.time.get_ticks() - START_TIME) // 1000
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60

    """Labels on the screen"""
    title = TITLE_FONT.render('Tetra  Crush',True, WHITE)
    score_label = custom_font.render('Points', True, WHITE)
    np_label = custom_font.render('Next Pieces', True, WHITE)
    lb_label = custom_font.render('Leaderboard', True, WHITE)
    gametime_label = custom_font.render('Game  Time', True, WHITE)
    time_label = TIMER_FONT.render(f'{minutes}{seconds:02d}', True, WHITE)
    score = SCORE_FONT.render(str(SCORE), True, WHITE)
    name_lb = lb_font.render('Name', True, WHITE)
    place_lb = lb_font.render('Place', True, WHITE)
    sc_lb = lb_font.render('Score', True, WHITE)

    """Gets rect for labels"""
    title_rect = title.get_rect(center=(WINDOW_WIDTH / 2, 25))
    score_label_rect = score_label.get_rect(center=(465, 90))
    np_rect = np_label.get_rect(center=(465, 225))
    game_rect = gametime_label.get_rect(center=(420, 195)) 
    timer_rect = time_label.get_rect(center=(525, 195))
    score_rect = score.get_rect(center=(465, 120))
    lb_rect = np_label.get_rect(center=(460, 380))
    name_lb_rect = name_lb.get_rect(center=(465, 415))
    place_lb_rect = place_lb.get_rect(center=(395, 415))
    sc_lb_rect = sc_lb.get_rect(center=(535, 415))

    """Blit on screen"""
    screen.blit(title, title_rect)
    screen.blit(score_label, score_label_rect)
    screen.blit(np_label, np_rect)
    screen.blit(gametime_label, game_rect)
    screen.blit(time_label, timer_rect)
    screen.blit(score, score_rect)
    screen.blit(lb_label, lb_rect)
    screen.blit(name_lb, name_lb_rect)
    screen.blit(place_lb, place_lb_rect)
    screen.blit(sc_lb, sc_lb_rect)


# --- Next Piece Preview UI ---
def next_piece_ui():
    np_border = pygame.Rect(360, 210, 210, 140)
    piece1_rect = pygame.Rect(360, 240, 71, 110)
    piece2_rect = pygame.Rect(430, 240, 71, 110)
    piece3_rect = pygame.Rect(500, 240, 70, 110)


    """Blit Next Piece Preview"""
    pygame.draw.rect(screen, WHITE, np_border, 2)
    pygame.draw.rect(screen, WHITE, piece1_rect, 2)
    pygame.draw.rect(screen, WHITE, piece2_rect, 2)
    pygame.draw.rect(screen, WHITE, piece3_rect, 2)


# --- Clock ---
clock = pygame.time.Clock()
running = True

# --- Background ---
def game_background(image):
      background = pygame.image.load(image)
      background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
      screen.blit(background, (0, 0))


# --- Preview Queue ---
preview_queue = [RandomBlock() for _ in range(3)]
dragged_block = None



# --- Game Loop ---
while running:
      game_background("galaxy_background.jpg")
      '''Event handling code '''
      get_events = pygame.event.get()
      for event in get_events:
            if event.type == pygame.QUIT:
                  running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                  # iterate exactly over what's in preview_queue
                  for i, blk in enumerate(preview_queue):
                        preview_rect = pygame.Rect(GRID_WIDTH + 65 + i * 70, 250, 60, 80)
                        if preview_rect.collidepoint(event.pos):
                             # safely pop the i-th block
                             dragged_block = preview_queue.pop(i)
                             dragged_block.dragging = True
                             # compute offsets based on the rect you clicked
                             dragged_block.offset_x = event.pos[0] - preview_rect.x
                             dragged_block.offset_y = event.pos[1] - preview_rect.y
                             break
            if exit_button.is_clicked(event):
                  subprocess.Popen([sys.executable,'launcher.py'])
                  running = False
      if dragged_block:
           dropped = dragged_block.drag_drop(get_events, GRID)
           if dropped:
               # 1) clear lines & get count + points
               SCORE += 4
               cleared_count, earned = Score.clear_and_score(GRID)
               SCORE += earned
               temp = TOTAL_LINES_CLEARED
               TOTAL_LINES_CLEARED += cleared_count
               if TOTAL_LINES_CLEARED > temp:
                   throw_confetti()
               TOTAL_BLOCKS_PLACED += 1
               TOTAL_SQUARES_FILLED += len(dragged_block.coordinates)
               # 1a) regrow one row per cleared line (up to 20)
               for _ in range(cleared_count):
                   if ROWS < 20:
                       GRID.insert(0, [0] * COLS)
                       ROWS += 1
               # 2) count this as a move (for shrinking)
               MOVES += 1
               # 3) advance preview queue
               preview_queue.append(RandomBlock())
               # 4) reset dragging
               dragged_block = None
               if not any_valid_moves(preview_queue, GRID):
                   game_over()
                   pygame.time.delay(1000)
                   subprocess.Popen([sys.executable, 'launcher.py'])
                   running = False
           else:
                dragged_block.place_block(screen)



      # --- Block Preview UI ---
      for i, blk in enumerate(preview_queue):
           preview_rect = pygame.Rect(GRID_WIDTH + 65 + i * 70, 250, 60, 80)
           blk.place_block(screen, preview=True, rect=preview_rect)



      #Load Leaderboard
      scores = lb.load_leaderboard()
      scores = lb.sort_game_scores(scores)
      # 2 draw labels and next piece ui5
      labels(GRID)
      next_piece_ui()

      # 3) draw the top five from `scores`
      lb.leaderboard_ui(scores, x=360, y=360)
      for i, (name, sc) in enumerate(scores[:5], start = 1):
          text = custom_font.render(f"{i:^10}{name:^24.3}{sc:^5}", True, WHITE)
          screen.blit(text, (375, 400 + i * 40))

      # --- Grid Shrinking Mechanics ---
      if MOVES >= SHRINK_INTERVAL and ROWS > 5:
          ROWS -= 2
          MOVES = 0



      # --- Game Grid ---
      for row in range(ROWS):
            for col in range(COLS):
                  rect = pygame.Rect(col * CELL_SIZE + 30, row * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE)
                  pygame.draw.rect(screen, WHITE, rect, 1)
                  if GRID[row][col] != 0:
                       pygame.draw.rect(screen, GRID[row][col], rect)
                       pygame.draw.rect(screen, WHITE, rect, 1) #Outline
                  else:
                       pygame.draw.rect(screen, WHITE, rect, 1)
      if not any_valid_moves(preview_queue, GRID):
              game_over()
              pygame.time.delay(1000)
              subprocess.Popen([sys.executable, 'launcher.py'])
              running = False
      exit_button.draw(screen)

      for piece in confetti[:]:
          piece.update()
          piece.draw()
          if piece.y > WINDOW_HEIGHT:
              confetti.remove(piece)
      pygame.display.flip()
      clock.tick(60)
pygame.quit()
lb.log_session(
    PLAYER_NAME,
    SCORE,
    TOTAL_BLOCKS_PLACED,
    TOTAL_SQUARES_FILLED,
    TOTAL_LINES_CLEARED
)
print("Session logged.")