import random
import sys
import pygame


class LifeGame:

    def __init__(self, screen_width=800, screen_height=600, cell_size=10, alive_color=(0, 255, 255),
                 dead_color=(0, 0, 0), max_fps=10):
        """
        Initialize grid, set default game state, initialize screen

        :param screen_width: Game window width
        :param screen_height: Game window height
        :param cell_size: Diameter of circles.
        :param alive_color: RGB tuple e.g. (255,255,255) for cells
        :param dead_color: RGB tuple e.g. (255,255,255)
        :param max_fps: Framerate cap to limit game speed
        """
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.alive_color = alive_color
        self.dead_color = dead_color

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clear_screen()
        pygame.display.flip()

        self.max_fps = max_fps

        self.active_grid = 0
        self.num_cols = int(self.screen_width / self.cell_size)
        self.num_rows = int(self.screen_height / self.cell_size)
        self.grids = []
        self.init_grids()
        self.set_grid()

        self.paused = False
        self.game_over = False

    def init_grids(self):
        """
        Create and stores the default active and inactive grid

        :return: None
        """

        def create_grid():
            """
            Generate an empty 2 grid

            """
            rows = []
            for row_num in range(self.num_rows):
                list_of_columns = [0] * self.num_cols
                rows.append(list_of_columns)
            return rows

        self.grids.append(create_grid())
        self.grids.append(create_grid())

    def set_grid(self, value=None, grid=0):
        """
        Set an entire grid at once. Set to a single value or random 0/1.

        """
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if value is None:
                    cell_value = random.randint(0, 1)
                else:
                    cell_value = value
                self.grids[grid][r][c] = cell_value

    def draw_grid(self):
        """
        Given the grid and cell states, draw the cells on the screen

        """
        self.clear_screen()
        for c in range(self.num_cols):
            for r in range(self.num_rows):
                if self.grids[self.active_grid][r][c] == 1:
                    color = self.alive_color
                else:
                    color = self.dead_color
                pygame.draw.circle(self.screen,
                                   color,
                                   (int(c * self.cell_size + (self.cell_size / 2)),
                                    int(r * self.cell_size + (self.cell_size / 2))),
                                   int(self.cell_size / 2),
                                   0)
        pygame.display.flip()

    def clear_screen(self):
        """
        Fill whole screen with dead color

        """
        self.screen.fill(self.dead_color)

    def get_cell(self, row_num, col_num):
        """
        Get the alive/dead (0/1) state of a specific cell in active grid

         Defaults to 0 (dead)
        """
        try:
            cell_value = self.grids[self.active_grid][row_num][col_num]
        except:
            cell_value = 0
        return cell_value

    def check_cell_neighbors(self, row_index, col_index):
        """
        Get the number of alive neighbor cells, and determine the state of the cell
        for the next generation. Determine whether it lives, dies, survives, or is born.

        """

        find_alive_neighbors = lambda a, b, c, d, e, f, g, h: a + b + c + d + e + f + g + h
        num_alive_neighbors = find_alive_neighbors(self.get_cell(row_index - 1, col_index - 1),
                                                   self.get_cell(row_index - 1, col_index),
                                                   self.get_cell(row_index - 1, col_index + 1),
                                                   self.get_cell(row_index, col_index - 1),
                                                   self.get_cell(row_index, col_index + 1),
                                                   self.get_cell(row_index + 1, col_index - 1),
                                                   self.get_cell(row_index + 1, col_index + 1),
                                                   self.get_cell(row_index + 1, col_index))

        # Rules for life and death
        if self.grids[self.active_grid][row_index][col_index] == 1:  # alive
            if num_alive_neighbors > 3:  # Overpopulation
                return 0
            if num_alive_neighbors < 2:  # Underpopulation
                return 0
            if num_alive_neighbors == 2 or num_alive_neighbors == 3:
                return 1
        elif self.grids[self.active_grid][row_index][col_index] == 0:  # dead
            if num_alive_neighbors == 3:
                return 1  # come to life

        return self.grids[self.active_grid][row_index][col_index]

    def update_generation(self):
        """
        Inspect current generation state, prepare next generation

        """
        self.set_grid(0, self.inactive_grid())
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                next_gen_state = self.check_cell_neighbors(r, c)
                self.grids[self.inactive_grid()][r][c] = next_gen_state
        self.active_grid = self.inactive_grid()

    def inactive_grid(self):
        """
        Simple helper function to get the index of the inactive grid
        If active grid is 0 will return 1 and vice-versa.

        """
        return (self.active_grid + 1) % 2

    def handle_events(self):
        """
        Handle any keypresses
        s - start/stop (pause) the game
        q - quit
        r - randomize grid

        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                print("key pressed")
                if event.unicode == 's':
                    print("Toggling pause.")
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True
                elif event.unicode == 'r':
                    print("Randomizing grid.")
                    self.active_grid = 0
                    self.set_grid(None, self.active_grid)  # randomize
                    self.set_grid(0, self.inactive_grid())  # set to 0
                    self.draw_grid()
                elif event.unicode == 'q':
                    print("Exiting.")
                    self.game_over = True
            if event.type == pygame.QUIT:
                sys.exit()

    def run(self):
        """
        Initialize game and loop forever until quit state

        """

        clock = pygame.time.Clock()

        while True:
            if self.game_over:
                return

            self.handle_events()

            if not self.paused:
                self.update_generation()
                self.draw_grid()

            clock.tick(self.max_fps)
