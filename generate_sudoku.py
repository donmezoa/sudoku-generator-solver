import argparse
import csv
import random
from typing import List, Optional, Tuple
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

Grid = List[List[int]]

# ------------------------
# Solver primitives
# ------------------------

def find_empty(grid: Grid) -> Optional[Tuple[int, int]]:
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return r, c
    return None


def is_valid_move(grid: Grid, row: int, col: int, num: int) -> bool:
    if num in grid[row]:
        return False

    for r in range(9):
        if grid[r][col] == num:
            return False

    br = (row // 3) * 3
    bc = (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if grid[r][c] == num:
                return False

    return True


# ------------------------
# Solver w/ node counting
# ------------------------

def solve_sudoku_with_stats(grid: Grid, stats: dict) -> bool:
    empty = find_empty(grid)
    if not empty:
        return True

    row, col = empty
    for num in random.sample(range(1, 10), 9):
        if is_valid_move(grid, row, col, num):
            grid[row][col] = num
            stats["nodes"] += 1

            if solve_sudoku_with_stats(grid, stats):
                return True

            grid[row][col] = 0

    return False



def count_solutions(grid: Grid, limit: int = 2) -> int:
    empty = find_empty(grid)
    if not empty:
        return 1

    row, col = empty
    count = 0

    for num in range(1, 10):
        if is_valid_move(grid, row, col, num):
            grid[row][col] = num
            count += count_solutions(grid, limit)
            grid[row][col] = 0

            if count >= limit:
                return count

    return count


# ------------------------
# Generator
# ------------------------

DIFFICULTY_CLUES = {
    "easy": 40,
    "medium": 32,
    "hard": 25,
    "extreme": 21
}


def generate_full_grid() -> Grid:
    grid = [[0] * 9 for _ in range(9)]
    solve_sudoku_with_stats(grid, {"nodes": 0})
    return grid


def generate_puzzle_base(difficulty: str) -> Grid:
    clues = DIFFICULTY_CLUES[difficulty]
    full = generate_full_grid()
    puzzle = [row[:] for row in full]

    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    for r, c in cells:
        if 81 - removed <= clues:
            break

        backup = puzzle[r][c]
        puzzle[r][c] = 0

        test = [row[:] for row in puzzle]
        if count_solutions(test, limit=2) != 1:
            puzzle[r][c] = backup
        else:
            removed += 1

    return puzzle


def generate_extreme_puzzle(
    min_nodes: int = 75_000,
    max_attempts: int = 100
) -> Grid:
    """
    Generate a puzzle that is empirically hard for the solver.
    """
    for attempt in range(1, max_attempts + 1):
        puzzle = generate_puzzle_base("extreme")

        test = [row[:] for row in puzzle]
        stats = {"nodes": 0}
        solve_sudoku_with_stats(test, stats)

        if stats["nodes"] >= min_nodes:
            print(
                f"Extreme puzzle accepted "
                f"(attempt {attempt}, nodes={stats['nodes']})", file=sys.stderr
            )
            return puzzle

        print(
            f"Extreme puzzle accepted "
            f"(attempt {attempt}, nodes={stats['nodes']:,})", file=sys.stderr
        )

    raise RuntimeError("Failed to generate extreme puzzle")


# ------------------------
# I/O
# ------------------------

def print_grid(grid: Grid) -> None:
    for i, row in enumerate(grid):
        if i % 3 == 0 and i != 0:
            print("-" * 21)
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            print(val if val != 0 else ".", end=" ")
        print()
    print()


def write_csv(grid: Grid, filename: str) -> None:
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(grid)

def print_csv(grid: Grid) -> None:
    """Print grid in CSV format to stdout."""
    writer = csv.writer(sys.stdout)
    writer.writerows(grid)

def write_pdf(grid: Grid, filename: str, seed: int = None, difficulty: str = None):
    """
    Write the Sudoku grid to a PDF file.
    Empty cells (0) are left blank for solving.
    Includes seed and difficulty at the bottom.
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    margin = 50
    grid_size = min(width, height) - 2 * margin - 50  # leave space for text at bottom
    cell_size = grid_size / 9

    # Draw grid lines
    for i in range(10):
        line_width = 2 if i % 3 == 0 else 1
        c.setLineWidth(line_width)
        # horizontal
        c.line(margin, margin + i*cell_size, margin + grid_size, margin + i*cell_size)
        # vertical
        c.line(margin + i*cell_size, margin, margin + i*cell_size, margin + grid_size)

    # Draw numbers
    c.setFont("Helvetica", int(cell_size * 0.6))
    for r in range(9):
        for c_idx in range(9):
            val = grid[r][c_idx]
            if val != 0:
                x = margin + c_idx * cell_size + cell_size / 2
                y = margin + (8 - r) * cell_size + cell_size / 2  # invert y-axis
                c.drawCentredString(x, y - cell_size*0.3, str(val))  # adjust vertical

    # Add seed and difficulty at the bottom
    c.setFont("Helvetica", 12)
    info_y = margin - 30
    info_text = ""
    if difficulty:
        info_text += f"Difficulty: {difficulty}"
    if seed is not None:
        if info_text:
            info_text += " | "
        info_text += f"Seed: {seed}"
    c.drawString(margin, info_y, info_text)

    c.save()

# ------------------------
# CLI
# ------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Sudoku puzzles with guaranteed uniqueness"
    )

    parser.add_argument(
        "difficulty",
        choices=["easy", "medium", "hard", "extreme"],
        help="Puzzle difficulty"
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible puzzles"
    )

    parser.add_argument(
        "-o", "--output",
        help="Write puzzle to CSV"
    )

    parser.add_argument(
        "--no-pretty",
        action="store_true",
        help="Disable pretty printing"
    )
    parser.add_argument(
        "--pdf",
        help="Write the puzzle to a PDF file for printing",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Always have a seed
    if args.seed is None:
        seed = random.randrange(1_000_000_000)
        random.seed(seed)
    else:
        seed = args.seed
        random.seed(seed)

    print(f"Seed: {seed}", file=sys.stderr)

    if args.difficulty == "extreme":
        puzzle = generate_extreme_puzzle()
    else:
        puzzle = generate_puzzle_base(args.difficulty)

    print(f"Generated {args.difficulty} puzzle:", file=sys.stderr)

    if args.no_pretty:
        print_csv(puzzle)
    else:
        print_grid(puzzle)

    if args.pdf:
        write_pdf(puzzle, args.pdf, seed=seed, difficulty=args.difficulty)
        print(f"Puzzle written to {args.pdf}")



    if args.output:
        write_csv(puzzle, args.output)
        print(f"Puzzle written to {args.output}")



if __name__ == "__main__":
    main()
