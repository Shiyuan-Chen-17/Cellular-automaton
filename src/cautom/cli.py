import random
import time
import sys
import termios
# Optional numpy for performance on large grids
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
import argparse

console = Console()

#Setup arguments for argparser
parser = argparse.ArgumentParser(description="A visual cellular automaton simulator")
parser.add_argument("--seed", help='Specify seed', type=int)
parser.add_argument("--prob", help='Specify the probability that each cell is alive (from 1-100)', type=int)
parser.add_argument("--infinite", action='store_true', help='Generate new seed on complete death')
parser.add_argument("--customrules", help="Specify custom game rules (B##/S##)", type=str)
parser.add_argument('--customcolors', help='Specify custom colours for living and dead cells', type=str)
parser.add_argument('--randomcolors', action='store_true', help='Make alive cells generate with random colors')
parser.add_argument('--age', action='store_true', help='Darken colours of cells as they get older')
_saved_settings = None
args=parser.parse_args()


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

def init_grid(seed):
    columns = console.size.width - 4
    rows = console.size.height // 2 - 1
    if args.seed and seed != None: 
        random_seed = args.seed
    else:
        random_seed = random.randint(0, 10000000000000)
    if args.prob: 
        living_probability = args.prob
    else:
        living_probability = random.randint(35, 65)
    print (random_seed)
    grid = [[0 for _ in range(columns)] for _ in range(rows)]
    random.seed(random_seed)
    for y in range(1, columns-1):
        for x in range(1, rows-1):
            state=random.randint(1, 100)
            if state<=living_probability:
                grid[x][y] = 1
    birth = [3]
    survive = [2, 3]

    if args.customrules:
        try:
            rules_raw = args.customrules.upper().split("/S")
            birth = [int(n) for n in rules_raw[0][1:]]
            survive = [int(n) for n in rules_raw[1]]
        except Exception:
            print("Invalid custom rule format. Use B##/S## (example: B3/S23)")
            sys.exit(1)
    if args.customcolors:
        try:
            colours_raw=args.customcolors.upper().split('/D')
            alive_colour_str = colours_raw[0][1:]
            dead_colour_str = colours_raw[1]
            alive_colour = [int(alive_colour_str[0:3]), int(alive_colour_str[3:6]), int(alive_colour_str[6:9])]
            dead_colour = [int(dead_colour_str[0:3]), int(dead_colour_str[3:6]), int(dead_colour_str[6:9])]

        except Exception:
            print("Invalid custom rule format. Use ARRRGGGBBB/DRRRGGGBBB")
            sys.exit(1)
    else:
        alive_colour = [0, 84, 81]
        dead_colour = [140, 3, 3]
    return rows, columns, grid, birth, survive, alive_colour, dead_colour


def sum_surrounding(grid, x, y):
    # Optimized: direct indexing instead of repeated lookups
    row_up = grid[x-1]
    row = grid[x]
    row_down = grid[x+1]
    return (
        row_down[y+1] + row_down[y] + row_down[y-1] +
        row[y+1] + row[y-1] +
        row_up[y+1] + row_up[y] + row_up[y-1]
    )


def update_array(grid, rows, columns, birth, survive):
    # Optimized: convert to sets for O(1) lookup instead of O(n)
    birth_set = set(birth)
    survive_set = set(survive)
    new_grid = [row[:] for row in grid]

    # Optimized: reduce function call overhead by inlining sum_surrounding
    for x in range(1, rows-1):
        row_up = grid[x-1]
        row = grid[x]
        row_down = grid[x+1]
        new_row = new_grid[x]
        
        for y in range(1, columns-1):
            # Inline neighbour calculation for better performance
            neighbours = (
                row_down[y+1] + row_down[y] + row_down[y-1] +
                row[y+1] + row[y-1] +
                row_up[y+1] + row_up[y] + row_up[y-1]
            )

            if row[y] == 0:
                if neighbours in birth_set:
                    new_row[y] = 1
                else:
                    new_row[y] = 0
            else:
                if neighbours in survive_set:
                    new_row[y] = row[y] + 1
                else:
                    new_row[y] = 0

    return new_grid


def update_array_numpy(grid_array, birth_set, survive_set):
    """NumPy-optimized update function for larger grids."""
    # Roll grid to get neighbours in each direction
    # This is much faster than nested loops for large grids
    n = grid_array
    
    # Count neighbours using array shifting
    neighbours = (
        np.roll(n, 1, axis=0) + np.roll(n, -1, axis=0) +
        np.roll(n, 1, axis=1) + np.roll(n, -1, axis=1) +
        np.roll(np.roll(n, 1, axis=0), 1, axis=1) +
        np.roll(np.roll(n, 1, axis=0), -1, axis=1) +
        np.roll(np.roll(n, -1, axis=0), 1, axis=1) +
        np.roll(np.roll(n, -1, axis=0), -1, axis=1)
    )
    
    # Handle edge wrapping - set edge cells to 0
    neighbours[0, :] = 0
    neighbours[-1, :] = 0
    neighbours[:, 0] = 0
    neighbours[:, -1] = 0
    
    # Create new grid
    new_grid = np.zeros_like(grid_array)
    
    # Apply rules using vectorized operations
    dead_cells = (grid_array == 0)
    alive_cells = ~dead_cells
    
    # Birth: dead cells with exactly birth count neighbours
    for b in birth_set:
        new_grid &= (neighbours != b)
        new_grid |= ((neighbours == b) & dead_cells)
    
    # Survival: alive cells with exactly survive count neighbours
    new_grid = np.zeros_like(grid_array)
    for b in birth_set:
        new_grid |= ((neighbours == b) & dead_cells)
    for s in survive_set:
        new_grid |= ((neighbours == s) & alive_cells)
    
    # Increment age for surviving cells
    surviving = np.zeros_like(grid_array, dtype=bool)
    for s in survive_set:
        surviving |= ((neighbours == s) & alive_cells)
    new_grid[surviving] = grid_array[surviving] + 1
    
    return new_grid


def render_grid(grid, alive_colours, dead_colours):
    # Optimized: pre-build style strings
    dead_style = f"rgb({dead_colours[0]},{dead_colours[1]},{dead_colours[2]})"
    alive_style = f"rgb({alive_colours[0]},{alive_colours[1]},{alive_colours[2]})"
    
    text = Text()

    for row in grid:
        for cell in row:
            if cell and not args.randomcolors:
                if args.age:
                    # Optimized: calculate color once per cell
                    age_factor = cell * 20
                    text.append("██", style=f"rgb({max(alive_colours[0] - age_factor, 0)},{max(alive_colours[1] - age_factor, 0)},{max(alive_colours[2] - age_factor, 0)})")
                else:
                    text.append("██", style=alive_style)
            elif cell and args.randomcolors:
                text.append("██", style=f"rgb({random.randint(0, 255)},{random.randint(0, 255)},{random.randint(0, 255)})")
            else:
                text.append("██", style=dead_style)
        text.append("\n")
    return Panel(text, title="Game of Life", border_style="cyan")

def main():
    rows, columns, grid, birth, survive, alive_colours, dead_colours = init_grid(None)
    
    # Pre-compute sets for O(1) lookup
    birth_set = set(birth)
    survive_set = set(survive)

    # Use numpy for large grids (optional optimization)
    use_numpy = False
    if rows * columns > 10000 and HAS_NUMPY:
        grid_array = np.array(grid, dtype=np.int32)
        use_numpy = True

    save_terminal_settings()
    disable_echo()

    try:
        with Live(render_grid(grid, alive_colours, dead_colours), refresh_per_second=20, screen=True) as live:
            while True:
                time.sleep(0.2)
                if use_numpy:
                    grid_array = update_array_numpy(grid_array, birth_set, survive_set)
                    grid = grid_array.tolist()
                else:
                    grid = update_array(grid, rows, columns, birth, survive)
                live.update(render_grid(grid, alive_colours, dead_colours))
                
                # Optimized: count alive cells more efficiently
                if use_numpy:
                    alive = np.count_nonzero(grid_array)
                else:
                    alive = sum(cell for row in grid for cell in row)
                if alive <= 1 and args.infinite:
                    rows, columns, grid, birth, survive, alive_colours, dead_colours = init_grid(True)
                    if use_numpy:
                        grid_array = np.array(grid, dtype=np.int32)
                    time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal_settings()

if __name__ == '__main__':
    main()
