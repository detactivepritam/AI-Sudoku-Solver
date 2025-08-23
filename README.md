# AI Sudoku Solver

This project is an advanced AI-based Sudoku solver implemented in Python. It uses constraint propagation and search techniques to solve even the hardest Sudoku puzzles.

## Features
- Supports both string and 2D list input formats for Sudoku puzzles
- Uses constraint propagation (elimination, hidden singles, naked pairs, pointing pairs)
- Efficient backtracking search with heuristics
- Validates solution correctness
- Prints the Sudoku board in a readable format

## Usage
1. Clone or download this repository.
2. Run the solver with:
   ```
   python main.py
   ```
3. You can modify the puzzle in `main.py` by changing the `hard` string or the board variable.

## Example
```
Input:
. . . . . . 9 . 7
. . . 4 2 . 1 8 .
. . . 7 . 5 . 2 6
1 . . 9 . 4 . . .
. 5 . . . . . 4 .
. . . 5 . 7 . . 9
9 2 . 1 0 8 . . .
. 3 4 . 5 9 . . .
5 . 7 . . . . . .
```

## How it works
- The solver uses constraint satisfaction and propagation to reduce possible values for each cell.
- When stuck, it uses backtracking search with heuristics to try possible values.
- Advanced techniques like naked pairs and pointing pairs are used for efficiency.

## Requirements
- Python 3.7+
## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
