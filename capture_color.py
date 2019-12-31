# "E:\Programming\Study\Python\display_pygame_THECOLORS.py"
# E:/Programming/Study/Python/THECOLORS_HTML.html

import sys
import numpy as np
import pygame

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GREY = pygame.Color('grey')
LIGHT_GREY = pygame.Color('lightgrey')
LIGHT_BLUE = pygame.Color('steelblue')
DARK_GREEN = pygame.Color('darkgreen')

WIDTH = 1024
HEIGHT = 768
GRID_WIDTH = 600
GRID_HEIGHT = 600
WIDTH0 = WIDTH - GRID_WIDTH # for controls in Pygame
MARGIN_TOP = 50
MARGIN_BOTTOM = HEIGHT - GRID_HEIGHT - MARGIN_TOP

COLOR_SCHEME = {
    'Standard': [(94,13,78), (189,21,80), (233,127,2), (248,202,0), (92,135,12), (2,152,166)],
    'Ocean': [(0,20,73), (1,38,119), (0,91,197), (0,180,252), (23,249,255), (24,213,166)],
    'Flames': [(65,0,48), (89,34,72), (116,25,88), (192,72,72), (240,114,65), (255,157,41)],
    'Another': [(59,140,136), (240,221,170), (228,124,93), (144,14,74), (21,43,60), (102,140,77)]
}
DEF_RECORD_TIME = 3600
DIFFICULTIES = {
    # name, max_turns, best_time, best_turns
    'Easy':     [11, DEF_RECORD_TIME, 11],
    'Medium':   [22, DEF_RECORD_TIME, 22],
    'Hard':     [35, DEF_RECORD_TIME, 35],
    'Extreme':  [45, DEF_RECORD_TIME, 45]
}

# for timer
TIMER_STOP = 0
timer_time = pygame.USEREVENT + 1


class CaptureColorGUI:
    """
    GUI class for Capture Color.
    """
    def __init__(self, color_grid):
        """ Set up a frame. """
        self._grid = color_grid
        self._cur_color = self._grid.get_lefttop_value()
        self._first_run = True

        pygame.init()
        self._screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Capture Color (by Andrei Ermishin)')

        self._btn_diff = pygame.Rect(170, 50, 100, 50)
        self._btn_colors = pygame.Rect(170, 170, 100, 50)
        self._btn_restart = pygame.Rect(170, HEIGHT - MARGIN_BOTTOM, 100, 50)

        self._colors_inc = 0
        self._diff_inc = 0
        self._schemes_lst = list(COLOR_SCHEME.keys())
        self._diffs_lst = list(DIFFICULTIES.keys())
        self._tile_colors = COLOR_SCHEME[self._schemes_lst[self._colors_inc]]
        self._difficulty = DIFFICULTIES[self._diffs_lst[self._diff_inc]]
        self._turns_left = self._difficulty[0]
        self._tile_size = GRID_WIDTH // (len(self._tile_colors) * (1+self._diff_inc))
        self._game_over = False
        self._game_won = False
        self._game_end_msg = ''
        self._count_time = 0
    
    def start(self):
        """ Start the GUI events loop. """
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.pos[0] < WIDTH0:
                        if self._btn_colors.collidepoint(event.pos):
                            self._change_colors()
                        elif self._btn_diff.collidepoint(event.pos):
                            self._change_difficulty()
                        elif self._btn_restart.collidepoint(event.pos):
                            self._restart()
                    else:
                        if event.pos[1] > HEIGHT - MARGIN_BOTTOM:
                            self._color_click(event.pos)
                
                if event.type == timer_time:
                    self._tick()
            
            self._draw(self._screen)
            pygame.display.flip()

            # It micro pauses the while loop to run 30 times a second max.
            clock.tick(30)
        
        pygame.time.set_timer(timer_time, TIMER_STOP)
        pygame.quit()
        sys.exit()
    
    def _draw_text(self, text, surface, location, font_size, color, bold=True):
        """ Draw text with center at location.center (pygame.Rect). """
        font = pygame.font.SysFont('arial', font_size, bold=bold)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = location.center
        surface.blit(text_surface, text_rect)

    def _button(self, text, surface, location, color, color_act, mouse_pos):
        """ Draw button with hovering. """
        _color = color_act if location.collidepoint(mouse_pos) else color
        pygame.draw.rect(surface, _color, location)

        self._draw_text(text, surface, location, 24, BLACK)
    
    def _draw_controls(self, surface, m_pos):
        """ Draw buttons, labels, best scores and tip for first run. """
        self._button(self._diffs_lst[self._diff_inc],
                     surface, self._btn_diff, GREY, LIGHT_BLUE, m_pos)
        self._button(self._schemes_lst[self._colors_inc],
                     surface, self._btn_colors, GREY, LIGHT_BLUE, m_pos)
        self._button('Restart',
                     surface, self._btn_restart, GREY, LIGHT_BLUE, m_pos)
        
        self._draw_text('Difficulty:', surface,
                        pygame.Rect(40, 50, 100, 50), 22, LIGHT_GREY, False)
        self._draw_text('Color scheme:', surface,
                        pygame.Rect(40, 170, 100, 50), 22, LIGHT_GREY, False)
        
        self._draw_text(f'{self._turns_left} / {self._difficulty[0]}', surface,
                        pygame.Rect(WIDTH-100, 5, 100, 45), 34, WHITE)
        self._draw_text(self._format_time(self._count_time), surface,
                        pygame.Rect(WIDTH0+10, 5, 50, 30), 24, GREY)
        
        if self._game_over:
            self._draw_text(self._game_end_msg, surface,
                            pygame.Rect(WIDTH0 + GRID_WIDTH//2 - 50,
                                        MARGIN_TOP + GRID_HEIGHT//2 - 25,
                                        100, 70),
                            70, WHITE)
        if self._first_run:
            self._draw_text('To start', surface,
                            pygame.Rect(WIDTH0-80, HEIGHT - 2*MARGIN_BOTTOM,
                                        60, 20),
                            20, LIGHT_GREY, False)
            self._draw_text('click color', surface,
                            pygame.Rect(WIDTH0-80, HEIGHT - MARGIN_BOTTOM*9//5,
                                        60, 20),
                            20, LIGHT_GREY, False)
            pygame.draw.arc(surface, LIGHT_GREY,
                            [WIDTH0 - 50, HEIGHT - MARGIN_BOTTOM*7//3,
                             100, MARGIN_BOTTOM * 3//2],
                            np.pi, np.pi * 3/2)
            arc_end = WIDTH0, HEIGHT - MARGIN_BOTTOM*5//6
            pygame.draw.line(surface, LIGHT_GREY,
                             arc_end, (arc_end[0] - 15, arc_end[1] - 15))
            pygame.draw.line(surface, LIGHT_GREY,
                             arc_end, (arc_end[0] - 18, arc_end[1] + 3))
    
    def _draw_grid(self, surface):
        """ Draw the color grid. """
        for (row, col), color_idx in np.ndenumerate(self._grid.get_values()):
            pygame.draw.rect(surface, self._tile_colors[color_idx],
                             [WIDTH0 + col*self._tile_size,
                              MARGIN_TOP + row*self._tile_size,
                              self._tile_size,
                              self._tile_size])
        # Draw bound
        pygame.draw.rect(surface, LIGHT_GREY,
                         [WIDTH0, MARGIN_TOP, GRID_WIDTH, GRID_HEIGHT], 2)
        # Draw current scheme colors:
        _width = GRID_WIDTH // len(self._tile_colors)
        for color_idx in range(len(self._tile_colors)):
            pygame.draw.rect(surface, self._tile_colors[color_idx],
                             [WIDTH0 + _width//4 + color_idx*_width,
                              HEIGHT - MARGIN_BOTTOM*8//10,
                              _width*2//4,
                              MARGIN_BOTTOM*6//10])
    
    def _draw_scores(self, surface):
        """ Draw highscores. """
        self._draw_text('***********  Highscores  ***********', surface,
                        pygame.Rect(20, 270, WIDTH0-40, 30), 26, LIGHT_GREY)
        idx = 0
        for diff, (_max_turns, time, turns) in DIFFICULTIES.items():
            if time != DEF_RECORD_TIME:
                rec = f'{diff}:   {turns} turns in {self._format_time(time)}s'
                self._draw_text(rec, surface,
                                pygame.Rect(20, 310 + 35*idx, WIDTH0-40, 35),
                                20, DARK_GREEN)
            idx += 1
        self._draw_text('********************************', surface,
                        pygame.Rect(20, 320 + 35*len(DIFFICULTIES),
                                    WIDTH0-40, 30),
                        26, LIGHT_GREY)
    
    def _draw(self, surface):
        """ Draw controls, color grid. """
        surface.fill(BLACK)

        mouse_pos = pygame.mouse.get_pos()

        self._draw_grid(surface)
        self._draw_controls(surface, mouse_pos)
        self._draw_scores(surface)
    
    def _change_colors(self):
        """ Change scheme colors. """
        self._colors_inc = (self._colors_inc + 1) % len(COLOR_SCHEME)
        self._tile_colors = COLOR_SCHEME[self._schemes_lst[self._colors_inc]]
    
    def _change_difficulty(self):
        """ Change difficulty of the game. """
        self._first_run = False
        self._diff_inc = (self._diff_inc + 1) % len(DIFFICULTIES)
        self._difficulty = DIFFICULTIES[self._diffs_lst[self._diff_inc]]
        self._turns_left = self._difficulty[0]
        self._new_game()
    
    def _new_game(self):
        """ Create a new grid with size corresponding to difficulty. """
        new_size = len(self._tile_colors) * (1+self._diff_inc) if self._diff_inc != 2 else 20
        self._grid = ColorGrid(len(self._tile_colors), new_size)

        self._tile_size = GRID_WIDTH // new_size
        self._cur_color = self._grid.get_lefttop_value()
        self._game_over = False
        self._count_time = 0
        pygame.time.set_timer(timer_time, TIMER_STOP)
    
    def _restart(self):
        """ Update color grid to initial state. """
        self._first_run = False
        self._grid.reset_values()
        self._turns_left = self._difficulty[0]
        self._cur_color = self._grid.get_lefttop_value()
        self._game_over = False
        self._count_time = 0
        pygame.time.set_timer(timer_time, TIMER_STOP)
    
    def _check_win(self):
        """ Check if all cells have same color and track for game state. """
        is_winner = self._grid.all_items_equal(self._cur_color)

        if is_winner:
            # There is a record!
            if self._count_time < self._difficulty[1]:
                self._difficulty[1] = self._count_time
                self._difficulty[2] = self._difficulty[0]-self._turns_left
                self._game_end_msg = 'Record!!!'
            else:
                self._game_end_msg = 'You win!'
            self._game_over = True
            pygame.time.set_timer(timer_time, TIMER_STOP)
            return True
        elif self._turns_left == 0:
            self._game_end_msg = 'You loose.'
            self._game_over = True
            pygame.time.set_timer(timer_time, TIMER_STOP)
        return False
    
    def _color_click(self, pos):
        """
        Compute index of clicked color, update the grid and turns left.
        Check for win and start timer.
        """
        if not self._game_over:
            new_color = self._cur_color
            if HEIGHT-MARGIN_BOTTOM*8//10 <= pos[1] <= HEIGHT-MARGIN_BOTTOM*2//10:
                _width = GRID_WIDTH // len(self._tile_colors)
                x_pos = (pos[0] - WIDTH0) % _width
                if _width//4 <= x_pos <= _width*3//4:
                    new_color = (pos[0] - WIDTH0) // _width
            
            if new_color != self._cur_color:
                self._first_run = False
                if self._turns_left == self._difficulty[0]:
                    pygame.time.set_timer(timer_time, 1000)
                self._grid.update_grid(new_color)
                self._cur_color = new_color
                self._turns_left -= 1
                self._game_won = self._check_win()
    
    def _tick(self):
        """ Increment by 1 at one second event. """
        self._count_time += 1
    
    def _format_time(self, time):
        """ Return formatted string 'min:sec' from time in seconds. """
        secs = time % 60
        mins = time // 60
        return f'{secs:02d}' if time < 60 else f'{mins:02d}:{secs:02d}'


class ColorGrid:
    """
    Square grid of tiles filled with numbers corresponding to colors.
    """
    def __init__(self, num_values, _size):
        """ Initialize 2D numpy array of size _size and random values. """
        self._num_values = num_values
        self._size = _size
        self._grid = np.random.randint(num_values, size=(_size, _size))
    
    def get_values(self):
        """ Return numpy.ndarray object containing color indexes. """
        return self._grid
    
    def reset_values(self):
        """ Refresh the color grid with new random values. """
        self._grid[:,:] = np.random.randint(self._num_values,
                                          size=(self._size, self._size))
    
    def get_lefttop_value(self):
        """ Get value (color index) of cell (0, 0) in the grid. """
        return self._grid[0, 0]
    
    def _four_neighbors(self, row, col):
        """ Return horiz/vert neighbors of cell (row, col). """
        ans = []
        if col > 0:
            ans.append((row, col - 1))
        if col < self._size - 1:
            ans.append((row, col + 1))
        if row > 0:
            ans.append((row - 1, col))
        if row < self._size - 1:
            ans.append((row + 1, col))
        return ans
    
    def update_grid(self, new_color):
        """
        (BFS) Find all neighbors of cell (0, 0) with same color.
        Set these found cells to a new color.
        """
        old_color = self.get_lefttop_value()

        start_node = (0, 0)
        visited = [start_node]
        queue = []  # queue based on list with index start_of_queue to pop()
        queue.append(start_node)
        start_of_queue = 0
        while start_of_queue < len(queue):
            cur_node = queue[start_of_queue]    # do pop(start_of_queue)
            start_of_queue += 1
            for neighbor in self._four_neighbors(*cur_node):
                if self._grid[neighbor[0], neighbor[1]] == old_color and neighbor not in visited:
                    visited.append(neighbor)
                    queue.append(neighbor)

        self._grid[[row for row, _ in visited], [col for _, col in visited]] = new_color
    
    def all_items_equal(self, value):
        """ Return True if all elements of the grid are equal to value. """
        return (self._grid == value).all()


def main():
    grid_size = len(COLOR_SCHEME['Standard'])
    CaptureColorGUI(ColorGrid(grid_size, grid_size)).start()


if __name__ == "__main__":
    main()
