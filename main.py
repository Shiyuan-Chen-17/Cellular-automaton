import random
import time
import sys
import termios
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
console = Console()

_saved_settings = None

def save_terminal_settings():
    global _saved_settings
    fd = sys.stdin.fileno()
    _saved_settings = termios.tcgetattr(fd)
    return _saved_settings

def restore_terminal_settings():
    global _saved_settings
    if _saved_settings:
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, _saved_settings)

def disable_echo():
    fd = sys.stdin.fileno()
    new_attr = termios.tcgetattr(fd)
    new_attr[3] = new_attr[3] & ~termios.ECHO 
    termios.tcsetattr(fd, termios.TCSANOW, new_attr)

def init_grid():
    columns = console.size.width - 4
    rows = console.size.height // 2 - 1
    living_probability, random_seed = map(int, input('living_probability, random seed: ').split(', '))
    grid = [[0 for _ in range(columns)] for _ in range(rows)]
    random.seed(random_seed)
    for y in range(1, columns-1):
        for x in range(1, rows-1):
            state=random.randint(1, 100)
            if state<living_probability:
                grid[x][y] = 1

    return rows, columns, grid


def sum_surrounding(grid, x, y):
    return (
        grid[x+1][y] +
        grid[x-1][y] +
        grid[x][y+1] +
        grid[x][y-1] +
        grid[x+1][y+1] +
        grid[x+1][y-1] +
        grid[x-1][y+1] +
        grid[x-1][y-1]
    )


def update_array(grid, rows, columns):
    new_grid = [row[:] for row in grid]

    for x in range(1, rows-1):
        for y in range(1, columns-1):

            neighbors = sum_surrounding(grid, x, y)

            if grid[x][y] == 0 and neighbors == 3:
                new_grid[x][y] =1
            elif grid[x][y] != 0 and (neighbors < 2 or neighbors > 3):
                new_grid[x][y] = 0
            elif grid[x][y] != 0 and (neighbors == 2 or neighbors == 3):
                new_grid[x][y] += 1

    return new_grid


def render_grid(grid):
    text = Text()

    for row in grid:
        for cell in row:
            if cell:
                text.append("██", style="rgb(0,84,81)")
            else:
                text.append("██", style="rgb(140,3,3)")
        text.append("\n")
    return Panel(text, title="Game of Life", border_style="cyan")


if __name__ == '__main__':
    rows, columns, grid = init_grid()

    save_terminal_settings()
    disable_echo()

    try:
        with Live(render_grid(grid), refresh_per_second=20) as live:
            while True:
                time.sleep(0.2)
                grid = update_array(grid, rows, columns)
                live.update(render_grid(grid))
    finally:
        restore_terminal_settings()
