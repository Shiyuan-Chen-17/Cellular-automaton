import random
import time
from rich.live import Live
from rich.text import Text


def init_grid():
    rows, columns = map(lambda x: x+2, map(int, input('Array size: ').split(', ')))
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
                new_grid[x][y] = 1
            elif grid[x][y] == 1 and (neighbors < 2 or neighbors > 3):
                new_grid[x][y] = 0

    return new_grid


def render_grid(grid):
    text = Text()

    for row in grid:
        for cell in row:
            if cell:
                text.append("██", style="green")
            else:
                text.append("  ")
        text.append("\n")

    return text


if __name__ == '__main__':
    rows, columns, grid = init_grid()

    with Live(render_grid(grid), refresh_per_second=20) as live:
        while True:
            time.sleep(0.2)
            grid = update_array(grid, rows, columns)
            live.update(render_grid(grid))

