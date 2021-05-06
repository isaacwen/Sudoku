# Isaac Wen
# This program gets sudoku puzzles from nine.websudoku.com and stores them
# locally

import urllib.request
from sudoku_backtracking import *
from bs4 import BeautifulSoup

# Produces the HTML for a specified difficulty of sudoku puzzle
def get_html(num):
    url = "https://nine.websudoku.com/?level=" + str(num)
    data = urllib.request.urlopen(url)
    data = data.read()
    return str(data)

# Produces the 81 digits representing the solution to a sudoku puzzle and
# the mask from the HTML produces by get_html
def get_sol(str):
    soup = BeautifulSoup(str, 'html.parser')
    puzzle_html = soup.select("#cheat")
    puzzle = puzzle_html[0]['value']
    mask_html = soup.select("#editmask")
    mask = mask_html[0]['value']
    return (puzzle, mask)

# Masks a given sudoku puzzle using a given mask
def mask_sol(sol_mask):
    (sol, mask) = sol_mask
    actual_puz = ""
    for i in range(81):
        if mask[i] == "1":
            actual_puz = actual_puz + "0"
        else:
            actual_puz = actual_puz + sol[i]
    return actual_puz

# Generates a puzzle and its solution given a difficulty from 1 - 4
def get_puzzle(num):
    html = get_html(num)
    sol_mask = get_sol(html)
    (sol, mask) = sol_mask
    puzzle = mask_sol(sol_mask)
    return (puzzle, sol)

# Generates puzzles based on the user's difficulty specification
def generate_main():
    difficulty = str(input("What difficulty puzzle would you like?\n(Enter"
                           " a difficulty from 1 to 4, 1 being the "
                           "easiest): "))
    (puz, sol) = get_puzzle(difficulty)
    puzzle = SudokuAI(puz)
    solution = SudokuAI(sol)
    print("The following is a puzzle of difficulty {0}:".format(difficulty))
    print(puzzle)
    next = input("Press ENTER to view the solution.")
    print(solution)
    choice = input("Would you like to view another puzzle? (Y to view): ")
    if choice == "Y":
        generate_main()
    else:
        return

# generate_main()