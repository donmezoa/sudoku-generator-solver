# sudoku-generator-solver
Sudoku puzzle generator and solver with uniqueness checks, difficulty modes, and CLI workflows.


Solve sudoku python script
The solve sudoku python script solves a standard 9×9 Sudoku puzzle. It uses a backtracking depth-first search algorithm. The solver checks each row, column, and 3×3 box to ensure that every number placed is valid. If it reaches a conflict, it backtracks and tries another number until the puzzle is solved.

The script includes a counter for the number of attempts the solver makes. Each candidate number placed in a cell increases the counter. This count serves as a simple measure of the puzzle's difficulty. After solving, the script prints the solved grid and the total number of attempts.

The script can read puzzles from a CSV file or from standard input. It checks that the input is exactly 9×9 and that all entries are integers. If the grid is invalid, it raises an error. This allows the script to be used in pipelines or automated workflows.

Overall, solve sudoku python script provides a reliable solver with a straightforward interface. It produces both a solution and a simple metric for how difficult the puzzle was for the solver.

Generate sudoku python script 
The generate sudoku python script generates new Sudoku puzzles with a guaranteed unique solution. It starts by generating a fully solved 9×9 grid using the same backtracking solver from solve sudoku python script. From the full grid, it removes numbers to create the puzzle. After removing each number, it checks that the puzzle still has a single solution.
The script supports four difficulty levels: easy, medium, hard, and extreme. Difficulty is controlled by the number of clues left in the puzzle. Easy puzzles have about 40 clues, medium puzzles have 32, hard puzzles have 25, and extreme puzzles have around 21. The extreme mode is designed to challenge the solver by producing puzzles that require many recursive steps to solve.

generate_sudoku.py includes a seed option for reproducibility. Users can supply a seed with --seed or let the script generate one. The seed is printed to standard error so that it does not interfere with piped output. The script also supports --no-pretty, which prints the grid in raw CSV format. This allows the output to be piped directly into solve_sudoku.py.

The script includes helper functions for printing, CSV output, counting solutions, and solving grids with node counting. These functions make it easy to generate puzzles, check uniqueness, and measure difficulty.


