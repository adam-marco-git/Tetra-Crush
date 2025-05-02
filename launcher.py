import pygame
pygame.init()
import sys
import subprocess
import time
from components import Button, Leaderboard, WINDOW_WIDTH, WINDOW_HEIGHT


# --- Constants --- 
custom_font = pygame.font.Font("ARCADECLASSIC.ttf", 24)
lb = Leaderboard(custom_font)
BACKGROUND = "BGandTitle.jpg"
BLACK = (0,0,0)
WHITE = (255,255,255)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Launch Tetra Crush")
clock = pygame.time.Clock()
plot_image, show_plot = None, False

# --- Background Generation ---
def game_background(screen, BGimage):
      background = pygame.image.load(BGimage)
      background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
      screen.blit(background, (0, 0))
                

# --- Buttons ---
start_button = Button(
rect=((WINDOW_WIDTH-200)//2, 385, 200, 60),
text="START",
font=custom_font,
bg_color=BLACK,
text_color=WHITE)

quit_button = Button(
rect=((WINDOW_WIDTH-125)//2, 455, 125, 40),
text="EXIT",
font=custom_font,
bg_color=None,
text_color=WHITE)

scoregraph_button = Button(
    rect=((WINDOW_WIDTH - 135)//2, 530, 135, 25),
    text="Plot Highscores",
    font=custom_font,
    bg_color=None,
    text_color=WHITE)

return_button = Button(
    rect=(5, 5, 135, 25),
    text="Return",
    font=custom_font,
    bg_color=BLACK,
    text_color=WHITE)


# --- Screen Loop ---
if __name__ == '__main__':
    running = True
    while running: 
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if start_button.is_clicked(event):
                if not show_plot:
                    subprocess.Popen([sys.executable,'tetra_crush.py'])
                    running = False
                else:
                    pass
            if quit_button.is_clicked(event):
                if not show_plot:
                    running = False
                else:
                    pass
            if scoregraph_button.is_clicked(event):
                if not show_plot:
                    lb.plot_scores()
                    plot_image = pygame.image.load('Highscore_plot.png')
                    show_plot = True
                else:
                    pass
            if return_button.is_clicked(event):
                if show_plot:
                    show_plot = False
                    start_button.bg_color = BLACK
                    return_button.bg_color = None
                    return_button.text_color = BLACK
                else:
                    pass


        game_background(screen, BACKGROUND)
        if plot_image and show_plot:
            screen.blit(plot_image, (0,0))
            start_button.bg_color = None
            return_button.bg_color = BLACK
            return_button.text_color = WHITE
            return_button.draw(screen)

        start_button.draw(screen)
        quit_button.draw(screen)
        scoregraph_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()