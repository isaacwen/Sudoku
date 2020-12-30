# Isaac Wen
# This program solves a given Sudoku board by using the backtracking method,
# and produces the solution as well as giving the user the option to have
# the solution automatically input into the puzzle by simulating the number
# keys and the TAB key on the keyboard

# For the design of this program, the board will be represented as a matrix:
# m = [[0,0,0,0,0,0,0,0,0],
#      [0,0,0,0,0,0,0,0,0],
#      [0,0,0,0,0,0,0,0,0],
#      [0,0,0,0,0,0,0,0,0],
#      [0,0,0,0,0,0,0,0,0],
#      [0,0,0,0,0,0,0,0,0],
#      [0,0,0,0,0,0,0,0,0],
#      [0,0,0,0,0,0,0,0,0],
#      [0,0,0,0,0,0,0,0,0]]
#   - if a spot on the board has a value occupying it, then it will have
#     that numerical value
#   - otherwise, if that spot on the board is an unknown value for the
#     solver to determine, it will have a 0
#   - the user's input will be as a 81-digit number, which corresponds
#     to each spot in the board from the top left, going right through each
#     row, then down the rows to end at the bottom right

#   - additionally, each 3x3 solution square will be denoted by a tuple,
#     as such
# m = [[-----|-----|-----],
#      [(0,0)|(0,1)|(0,2)],
#      [-----|-----|-----],
#      [-----|-----|-----],
#      [(1,0)|(1,1)|(1,2)],
#      [-----|-----|-----],
#      [-----|-----|-----],
#      [(2,0)|(2,1)|(2,2)],
#      [-----|-----|-----]]

import copy
import time
import pyautogui

# Takes 81 numbers and produces a 9x9 matrix using those numbers, starting
# from the top left corner, going across the columns in that row, then
# going down the rows to end up at the bottom right corner
def make_nine_by_nine(str):
    nums = str
    matrix = []
    for i in range(9):
        row = []
        for j in range(9):
            row.append(int(nums[i*9 + j]))
        matrix.append(row)
    return matrix

# This class generates an empty Board, or a 9x9 matrix with all 0's
class EmptyBoard():
    empty_board1 = "00000000000000000000000000000000000000000000000000000000"
    empty_board2 = empty_board1 + "0000000000000000000000000"
    def __init__(self, board = empty_board2):
        empty_matrix = make_nine_by_nine(board)
        self.board = copy.copy(empty_matrix)

    def __str__(self):
        display = ""
        for row in self.board:
            display = display + str(row) + "\n"
        return display

    # Takes a value in the form of (row, column, value) and replaces the
    # spot (row, column) in self.board with value
    def add_value(self, value):
        (r,c,v) = value
        try:
            self.board[r-1][c-1] = v
        except IndexError:
            print("ERROR: A 9x9 board only has 9 rows and columns.")

    # Gets a value from a given row-col location on the board
    def get_value(self, row_col):
        (r,c) = row_col
        return self.board[r-1][c-1]


# This class is a sudoku board, adding functions such as testing for the
# correctness of rows and columns according to sudoku rules
class SudokuBoard(EmptyBoard):
    pass

    # This function allows us to add multiple values at the same time
    def add_values(self, values = []):
        for value in values:
            self.add_value(value)
        return

    # This function will return True if a row has no duplicate numbers, and
    # false otherwise
    def row_good(self, row):
        row_list = self.board[row-1]
        return is_unique(row_list)

    # This function returns True if a given column has no duplicate numbers,
    # and false otherwise
    def column_good(self, column):
        column_values = []
        for row in self.board:
            column_values.append(row[column - 1])
        return is_unique(column_values)

    # This function returns True if the solution square for which a number
    # at a given row, column pair falls into has no duplicate values, and
    # false otherwise
    def square_good(self, row_column):
        (r, c) = row_column
        # Thus calculates the tuple identifying the solution square, as
        # described earlier
        (ssquare_row, ssquare_col) = ((r-1)//3, (c-1)//3)
        ssquare_values = []
        # Collects all the values in a given solution square
        for row in range(ssquare_row * 3, ssquare_row * 3 + 3):
            for col in range(ssquare_col * 3, ssquare_col * 3 + 3):
                ssquare_values.append(self.board[row][col])
        return is_unique(ssquare_values)

    # This function returns True if the adding the value value means that the
    # board remains valid or False if sudoku rules have been violated
    def add_confirm(self, value):
        (r,c,v) = value
        orig_value = self.get_value((r,c))
        self.add_value((r,c,v))
        can_add = self.square_good((r,c)) and self.row_good(r) \
                  and self.column_good(c)
        self.add_value((r,c,orig_value))
        return can_add

    # Determines if the initial board has any repeating numbers, that is
    # is not a valid board before inputs
    #   - will return false if any of the rows, columns, or solution squares
    #     has duplicate numbers, or false otherwise
    def board_good(self):
        for row in range(1,10):
            if self.row_good(row) == False:
                return False
        for col in range(1,10):
            if self.column_good(col) == False:
                return False
        # List of one square row_col pair from each solution square
        row_col_pairs = [(1,1), (4,1), (7,1), (1,4), (4,4), (7,4), (1,7),
                         (4,7), (7,7)]
        for pair in row_col_pairs:
            if self.square_good(pair) == False:
                return False
        return True

# This function determines if all non-zero numbers in a given list are unique
def is_unique(lon):
    for num in lon:
        if num == 0:
            continue
        elif lon.count(num) > 1:
            return False
    return True


# This class will contain all relevant functions to automatically solving a
# sudoku board
class SudokuAI(SudokuBoard):
    pass

    # This function will determine the row-column pair of the next 0 in the
    # board given a row-column position on the board, going left through the
    # columns then down through the rows, or will return True if there is no
    # more 0's
    def next_zero(self, row_col):
        (r, c) = row_col
        # Converts the user-input rows and columns to the user input
        (ind_r, ind_c) = (r-1, c-1)
        for rest_rows in range(ind_r, 9):
            for cols in range(0, 9):
                if rest_rows == ind_r and cols <= ind_c:
                    continue
                elif self.board[rest_rows][cols] == 0:
                    return (rest_rows + 1, cols + 1)
        return True

    # This function determines all possible values that could occupy the
    # position in the table at row_col, returns True if one of the values
    # from 1 to 9 fits as well as if one of the values from 1 to 9 fits the
    # next spot where there is a 0 in the table
    def try_value(self, row_col):
        # If the board is already solved, then this will just return True
        if row_col == True:
            return True
        (r, c) = row_col
        values = []
        for num in range(1,10):
            if self.add_confirm((r,c,num)):
                values.append(num)
        # Test if any of the values mean that all the subsequent 0 spots
        # have a possible value
        for value in values:
            self.add_value((r, c, value))
            if self.next_zero(row_col) == True:
                return True
            elif self.try_value(self.next_zero(row_col)) == True:
                return True
        # If none of the values work, reset the value to 0
        self.add_value((r,c,0))
        return False

    # Finds the first 0 in the board
    def first_zero(self):
        return self.next_zero((1,0))

    # Solves the instance of board, if it is solvable, and returns True,
    # otherwise returns False
    def solve_board(self):
        # If the board has duplicate numbers in row, columns, or solution
        # squares, will return false
        if self.board_good() == False:
            return False
        board_works = self.try_value(self.first_zero())
        return board_works

    # Automatically inputs the solution using numbers and TAB
    def input_nums(self):
        inputs = self.board
        count1 = 0
        count2 = 0
        start = input("Press ENTER to start the countdown for the input.")
        print("The input will start in")
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)
        for row in inputs:
            for num in row:
                string_num = str(num)
                pyautogui.press(string_num)
                if count2 < 8:
                    pyautogui.press('tab')
                count2 += 1
            if count1 < 8:
                pyautogui.press('tab')
            else:
                pyautogui.press('enter')
            count1 += 1
            count2 = 0
        return


# Runs the program where a board is asked as input and is solved
def sudoku_main():
    matrix = str(input("Enter a sudoku board in the form of a list of 81 "
                       "digits, where empty \nspots are represented by "
                       "0's or press Enter to view the preloaded board: "))
    if matrix == "":
        # This is the pre-installed board
        user_board = SudokuAI("700002080000706900900450200052800000100327"
                              "008000009420003078009008105000010200005")
    else:
        try:
            user_board = SudokuAI(matrix)
        except:
            print("You did not enter a valid matrix.")
            sudoku_main()

    print('The board you entered is as follows:')
    print(user_board)
    print('Solving...')
    board_works = user_board.solve_board()
    if board_works:
        print(user_board)
        want_input = str(input("Would you like the computer to "
                               "automatically type in the solution? "
                               "(Y or N): "))
        if want_input == "Y":
            user_board.input_nums()
        another_step = str(input("Would you like to enter another board?"
                                 " (Y or N): "))
        if another_step == "Y":
            sudoku_main()
    else:
        print("The board you entered is unsolvable.")
        sudoku_main()

# sudoku_main()