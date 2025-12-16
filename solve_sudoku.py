import csv
import argparse
from typing import List, Optional, Tuple
import sys

Grid = List[List[int]]


# ------------------------
# I/O
# ------------------------

def read_sudoku_csv(filename: str = None) -> Grid:
    grid = []
    if filename is None or filename == "-":
        f = sys.stdin
    else:
        f = open(filename, newline="")

    with f:
        reader = csv.reader(f)
        for row in reader:
            grid.append([int(cell) for cell in row])

    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        raise ValueError("Sudoku grid must be exactly 9x9")
    return grid


def write_sudoku_csv(grid: Grid, filename: str) -> None:
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(grid)


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


# ------------------------
# Validation
# ------------------------

def is_valid_group(values: List[int]) -> bool:
    """Check a row/column/box contains no duplicates (excluding zeros)."""
    nums = [v for v in values if v != 0]
    return len(nums) == len(set(nums))


def validate_grid(grid: Grid) -> None:
    """Raise ValueError if the Sudoku grid is invalid."""
    for r in range(9):
        for c in range(9):
            val = grid[r][c]
            if not (0 <= val <= 9):
                raise ValueError(f"Invalid value {val} at row {r+1}, col {c+1}")

    # Rows
    for r in range(9):
        if not is_valid_group(grid[r]):
            raise ValueError(f"Duplicate value in row {r+1}")

    # Columns
    for c in range(9):
        col = [grid[r][c] for r in range(9)]
        if not is_valid_group(col):
            raise ValueError(f"Duplicate value in column {c+1}")

    # 3x3 boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = [
                grid[r][c]
                for r in range(br, br + 3)
                for c in range(bc, bc + 3)
            ]
            if not is_valid_group(box):
                raise ValueError(
                    f"Duplicate value in 3x3 box starting at row {br+1}, col {bc+1}"
                )


# ------------------------
# Solver
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

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if grid[r][c] == num:
                return False

    return True


def solve_sudoku(grid: Grid, stats: dict) -> bool:
    empty = find_empty(grid)
    if not empty:
        return True

    row, col = empty

    for num in range(1, 10):
        stats["attempts"] += 1

        if is_valid_move(grid, row, col, num):
            grid[row][col] = num

            if solve_sudoku(grid, stats):
                return True

            grid[row][col] = 0

    return False



# ------------------------
# CLI
# ------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Solve and/or validate a Sudoku puzzle from a CSV file"
    )

    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input CSV file (default: stdin)"
    )

    parser.add_argument(
        "-o", "--output",
        help="Write solved puzzle to CSV"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the puzzle before solving (or exit if no solve requested)"
    )

    parser.add_argument(
        "--no-pretty",
        action="store_true",
        help="Disable pretty-printed output"
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        grid = read_sudoku_csv(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    if args.validate:
        try:
            validate_grid(grid)
            print("Puzzle is valid.")
        except ValueError as e:
            print(f"Validation failed: {e}")
            return

    # If only validating and no output requested, stop here
    if args.validate and not args.output:
        return

    print("Original puzzle:")
    if args.no_pretty:
        for row in grid:
            print(row)
    else:
        print_grid(grid)

    stats = {"attempts": 0}

    if not solve_sudoku(grid, stats):
        print("No solution exists.")
        return

    print(f"Solved in {stats['attempts']:,} attempts.")


    print("Solved puzzle:")
    if args.no_pretty:
        for row in grid:
            print(row)
    else:
        print_grid(grid)

    if args.output:
        try:
            write_sudoku_csv(grid, args.output)
            print(f"Solved puzzle written to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}")


if __name__ == "__main__":
    main()
