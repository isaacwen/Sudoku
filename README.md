# Sudoku
## General Information
Using the backtracking algorithm, web scraping, and PyGame, I created a Sudoku game replicating the
features of popular Sudoku games, with additional features:
* like most other Sudoku games, the user can generate and interact with random puzzles of varying difficulties
* the user can also input a Sudoku puzzle and a solution will be generated for that puzzle (if it is solvable)

All puzzles generated are sources from nine.websudoku.com

## File Information
sudoku_main.py contains all the relevant code for this project. This code is split between the other files,
as follows:
* sudoku_backtracking.py contains all relevant code which implements the backtracking algorithm to solve an arbitrary puzzle
* sudoku_scraper.py contains all relevant code which implements web scraping to produce the random puzzles
* sudoku_pygame.py contains all relevant code used to implement PyGame to create the user interface for the game

Additional modules that may need to be downloaded include:
* time
* copy
* pyautogui
* urllib.request
* pygame
