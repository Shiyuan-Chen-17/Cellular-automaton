import random
import time
import sys
import termios
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

    return rows, columns, grid, birth, survive


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


def update_array(grid, rows, columns, birth, survive):
    new_grid = [row[:] for row in grid]

    for x in range(1, rows-1):
        for y in range(1, columns-1):

            neighbours = sum_surrounding(grid, x, y)

            if grid[x][y] == 0 and neighbours in birth:
                new_grid[x][y] = 1
            elif grid[x][y] != 0 and neighbours in survive:
                new_grid[x][y] += 1
            else:
                new_grid[x][y] = 0

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

def main():
    rows, columns, grid, birth, survive = init_grid(None)

    save_terminal_settings()
    disable_echo()

    try:
        with Live(render_grid(grid), refresh_per_second=20, screen=True) as live:
            while True:
                time.sleep(0.2)
                grid = update_array(grid, rows, columns, birth, survive)
                live.update(render_grid(grid))
                alive = 0
                for row in grid:
                    for cell in row:
                        if cell:
                            alive += 1
                if alive <= 1 and args.infinite:
                    rows, columns, grid, birth, survive = init_grid(True)
                    time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal_settings()

if __name__ == '__main__':
    main()
