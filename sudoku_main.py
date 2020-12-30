# Isaac Wen
# This program uses pygame to produce an interactive interface for the user
# to solve sudoku puzzles as well as input puzzles for the program to solve

# NOTE: This program has the same functionality as sudoku_pygame, however
# all the cumulative code used for this program is duplicated in this program
# instead of being called from separate files
#   - some documentation may be omitted from the original files; see the
#     original files to find all relevant documentation for the functions

import time
import copy
import pyautogui
import urllib.request
import pygame

# ===========================================================================
# The following code is from sudoku_backtracking.py
# ===========================================================================

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

# ===========================================================================
# ===========================================================================

# ===========================================================================
# The following code is from sudoku_scraper.py
# ===========================================================================

# Produces the HTML for a specified difficulty of sudoku puzzle
def get_html(num):
    url = "https://nine.websudoku.com/?level=" + str(num)
    data = urllib.request.urlopen(url)
    data = data.read()
    return str(data)

# Produces the 81 digits representing the solution to a sudoku puzzle and
# the mask from the HTML produces by get_html
def get_sol(str):
    html = str
    split1 = html.split("ID=\"cheat\" TYPE=hidden VALUE=\"")
    puzzle = split1[1][:81]
    split2 = split1[1].split("ID=\"editmask\" TYPE=hidden VALUE=\"")
    mask = split2[1][:81]
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

# ===========================================================================
# ===========================================================================

# ===========================================================================
# The following code is from sudoku_pygame.py
# ===========================================================================

# Initialize the game
pygame.init()

# Magic numbers for width and height of the screen
screen_width = 750
screen_height = 500

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the Program Name and Icon
pygame.display.set_caption("All-In-One Sudoku")
icon = pygame.image.load("sudoku.png")
pygame.display.set_icon(icon)

# Magic numbers for various RGB color combinations
rgb_white = pygame.Color(255, 255, 255)
rgb_black = pygame.Color(0, 0, 0)
rgb_grey = pygame.Color(230, 230, 230)
rgb_blue = pygame.Color(0, 0, 255)
rgb_red = pygame.Color(255, 0, 0)

# ===========================================================================
# This section contains all the functions that make up the home page

# Font customization for the font of the main home page text and the home
# page button text
home_font = pygame.font.Font('freesansbold.ttf', 50)
button_font = pygame.font.Font('freesansbold.ttf', 24)

# The desired characteristics of the buttons on the home screen
home_button_coords1 = (250, 220)
home_button_coords2 = (250, 300)
home_button_width = 250
home_button_height = 50


# Returns a list of rectangles the represents the buttons on the home
# screen
def home_buttons():
    buttons = []
    # Produce the two buttons desired, and adds them to the list
    button1 = pygame.Rect(home_button_coords1,
                          (home_button_width, home_button_height))
    buttons.append(button1)
    button2 = pygame.Rect(home_button_coords2,
                          (home_button_width, home_button_height))
    buttons.append(button2)
    return buttons


# List of rectangles representing the two buttons on the home screen
home_button_rects = home_buttons()
# Rectangle representing the home button to get to the interactive sudoku
# puzzle
home_sudoku_button = home_button_rects[0]
# Rectangle representing the home button to get to the automatic sudoku
# solver
home_solver_button = home_button_rects[1]


# Draws the home screen text and buttons
def draw_home():
    home_title = home_font.render("All-in-One Sudoku", True, rgb_black)
    screen.blit(home_title, (152, 100))
    # Draws the buttons on the home screen
    for button in home_button_rects:
        pygame.draw.rect(screen, rgb_white, button)
    # Prints the texts for the buttons on the home screen
    button1_text = button_font.render("Try a Puzzle", True, rgb_black)
    screen.blit(button1_text, (306, 233))
    button2_text = button_font.render("Automatic Solver", True, rgb_black)
    screen.blit(button2_text, (272, 313))


# END =======================================================================


# ===========================================================================
# This section contains all the functions that make up the difficulty select
# page

# Font customization for the font of the main home page text and the home
# page button text
difficulty_font = pygame.font.Font('freesansbold.ttf', 25)
diff_button_font = pygame.font.Font('freesansbold.ttf', 45)

# The desired characteristics of the buttons on the difficulty screen
diff_button_coords1 = (155, 325)
diff_button_coords2 = (285, 325)
diff_button_coords3 = (415, 325)
diff_button_coords4 = (545, 325)
diff_button_width = 50
diff_button_height = 65


# Returns a list of rectangles the represents the buttons on the home
# screen
def diff_buttons():
    buttons = []
    # Produce the two buttons desired, and adds them to the list
    button1 = pygame.Rect(diff_button_coords1,
                          (diff_button_width, diff_button_height))
    buttons.append(button1)
    button2 = pygame.Rect(diff_button_coords2,
                          (diff_button_width, diff_button_height))
    buttons.append(button2)
    button3 = pygame.Rect(diff_button_coords3,
                          (diff_button_width, diff_button_height))
    buttons.append(button3)
    button4 = pygame.Rect(diff_button_coords4,
                          (diff_button_width, diff_button_height))
    buttons.append(button4)
    return buttons


# List of rectangles representing the buttons on the difficulty screen
diff_button_rects = diff_buttons()
# Rectangles representing the four difficulty buttons
diff1_button = diff_button_rects[0]
diff2_button = diff_button_rects[1]
diff3_button = diff_button_rects[2]
diff4_button = diff_button_rects[3]


# Draws the difficulty screen text and buttons
def draw_difficulty():
    difficulty_title = difficulty_font. \
        render("What puzzle difficulty would you like?", True, rgb_black)
    screen.blit(difficulty_title, (138, 250))
    # Draws the four difficulty buttons
    for button in diff_button_rects:
        pygame.draw.rect(screen, rgb_white, button)
    # Prints the texts for the buttons on the difficulty screen
    (x, y) = diff_button_coords1
    shiftX = 14
    shiftY = 14
    button1_text = diff_button_font.render("1", True, rgb_black)
    screen.blit(button1_text, (x + shiftX, y + shiftY))
    (x, y) = diff_button_coords2
    button2_text = diff_button_font.render("2", True, rgb_black)
    screen.blit(button2_text, (x + shiftX, y + shiftY))
    (x, y) = diff_button_coords3
    button3_text = diff_button_font.render("3", True, rgb_black)
    screen.blit(button3_text, (x + shiftX, y + shiftY))
    (x, y) = diff_button_coords4
    button4_text = diff_button_font.render("4", True, rgb_black)
    screen.blit(button4_text, (x + shiftX, y + shiftY))


# Desired difficulty by the user, determined through which button they
# pressed
user_difficulty = 0
# END =======================================================================


# ===========================================================================
# This section contains all the functions that make up the interactive sudoku
# puzzle

# Calculations for desired margins between sudoku board and the size of each
# solution square tile on the board based on the screen width and height
board_margin = 24  # Margin between the board and the edge of the screen
board_size = screen_height - 2 * board_margin
tile_size = 48
tile_margin = 2  # Space between two tiles, not accounting for 3x3
tile_size2 = tile_margin + tile_size  # Size of one tile + margin

# Font Customization for the numbers in the sudoku board
num_font = pygame.font.Font('freesansbold.ttf', 32)
solution_font = pygame.font.Font('freesansbold.ttf', 12)


# Draws the background for the sudoku board
def draw_board_background():
    pygame.draw.rect(screen, rgb_black,
                     (board_margin, board_margin, board_size, board_size))


# Produces a list corresponding to the coordinates at which each of the 81
# tiles will be placed
def get_board_coords():
    # List of the Rect of all 81 tiles on the sudoku board
    tile_list = []

    for row in range(0, 9):
        # Shifts all rows at the top of each group of three down one pixel
        # and all rows at the bottom of each group of three up one pixel to
        # highlight the divisions between 3x3 solution squares
        shiftY = 0
        if row % 3 == 0:
            shiftY = 1
        elif row % 3 == 2:
            shiftY = -1

        for col in range(0, 9):
            # Similarly shifts columns left and right one pixel to highlight
            # 3x3 solution squares
            shiftX = 0
            if col % 3 == 0:
                shiftX = 1
            elif col % 3 == 2:
                shiftX = -1

            # Adds the shifts to enhance margins of 3x3 solution squares
            rectX = board_margin + tile_margin + col * tile_size2 + shiftX
            rectY = board_margin + tile_margin + row * tile_size2 + shiftY

            # Adds the rectangle to the list
            tile_list.append((rectX, rectY))

    return tile_list


# Produces a list of all the Rect representing all the tiles on the board
# from a list of coordinates, with each having a size of tile_size
def get_rects(loc):
    rects_list = []
    for coords in loc:
        (x, y) = coords
        rects_list.append(pygame.Rect(x, y, tile_size, tile_size))
    return rects_list


# Draws all rectangles from a list of Rect, with each being white
def draw_rects(lor):
    for rect in lor:
        pygame.draw.rect(screen, rgb_white, rect)


# Constants for the shifts of the number in the tiles to make them look
# decent
tile_digitX = 14
tile_digitY = 10


# Draws each digit from a string of n digits, or leaves empty if the digit
# is 0, centered in a square of size tile_size at the corresponding
# coordinate in a list of n coordinates
def draw_nums(str_num, loc):
    for i in range(0, 81):
        n = str_num[i]
        if int(n) == 0:
            continue
        (x, y) = loc[i]
        num = num_font.render(n, True, rgb_black)
        # Draws all of the non-zero numbers from the list of digits, with
        # a x,y shift that makes the number placement in the tiles look
        # decent
        screen.blit(num, (x + tile_digitX, y + tile_digitY))


# Returns a dictionary with the key-value pair being the indices for all
# 0's in the given string of digits and the corresponding coordinates from
# the given list of coordinates
#   - if the third parameter is equal to 'f', then the indices are the keys,
#     and if the third parameter is equal to 'b', then the indices are the
#     values
def get_zeros(str_num, loc, mode):
    zero_dict = {}
    for i in range(0, 81):
        n = str_num[i]
        if int(n) != 0:
            continue
        if mode == 'f':
            zero_dict[i] = loc[i]
        elif mode == 'b':
            zero_dict[loc[i]] = i
    return zero_dict


# Draws the solution onto the board, based on a list of digits representing
# the solution and the dictionary generated by get_zeros for the
# corresponding problem where the indices are the keys ('f')
def draw_solution(str_num, dict_coords, user_tries):
    indices = list(dict_coords.keys())
    for index in indices:
        n = str_num[index]
        n_user = user_tries[index]
        (x, y) = dict_coords[index]
        if n == n_user:
            num = solution_font.render(n, True, rgb_black)
        else:
            num = solution_font.render(n, True, rgb_red)
        screen.blit(num, (x + 35, y + 36))
    return


# Generates a puzzle and solution of difficulty specified by the user
def generate_puzzle(num):
    (puzzle, solution) = get_puzzle(num)
    user_tries = puzzle
    zero_coords = get_zeros(puzzle, coords, 'f')
    coords_zeros = get_zeros(puzzle, coords, 'b')
    return (puzzle, solution, user_tries, zero_coords, coords_zeros)


# END========================================================================

# ===========================================================================
# This section contains all the functions that allow the user to input
# numbers into the interactive sudoku puzzle

# Determines if the coordinates for the mouse are over a tile that which has
# coordinates as one of the keys in coords_zero, and returns the coordinates
# if so, otherwise returns False
#   - as each tile is 48x48 pixels, this will just check if any of the keys
#     is within 48 units upwards and to the left of the mouse coordinates
def on_tile(mouse_coords, coords_zero):
    list_coords = coords_zero.keys()
    (xm, ym) = mouse_coords
    for coords in list_coords:
        (x, y) = coords
        if xm - x <= tile_size and xm - x >= 0 and ym - y <= tile_size \
                and ym - y >= 0:
            return coords
    return False


# Determines if the user's mouse input is pressing a tile which is editable
# (that is, isn't a preset number from the puzzle), and returns the
# coordinates of the puzzle if so and the user's previous input on that tile,
# otherwise returns false
def tile_editable(mouse_coords, coords_zero, user_tries):
    editable = on_tile(mouse_coords, coords_zero)
    if editable == False:
        return False
    index = coords_zero[editable]
    previous_input = user_tries[index]
    return (editable, index, previous_input)


# Displays all the numbers in user_tries if the corresponding number in the
# original puzzle is a zero (that is, it's not a preset number)
#   - the keys in zero_coords are the indices to all the numbers in the
#     original puzzle that are zero, or not preset
#   - the third parameter specifies the color in which the numbers will be
#     drawn
def display_user_input(user_tries, zero_coords, text_color):
    all_indices = zero_coords.keys()
    for index in all_indices:
        n = user_tries[index]
        if n == '0':
            continue
        # This is the same drawing scheme as in draw_nums
        (x, y) = zero_coords[index]
        num = num_font.render(n, True, text_color)
        screen.blit(num, (x + tile_digitX, y + tile_digitY))


# Changes the list of user's inputs based on a new input and the index which
# the new input should replace one of the old inputs
def change_user_inputs(user_tries, new_input, index):
    old_inputs = user_tries
    new_inputs = user_tries[:index] + new_input + user_tries[(index + 1):]
    return new_inputs


# END========================================================================

# ===========================================================================
# This section contains all the functions that will produce the sidebar
# buttons for the solver and interactive sudoku screen

# Sidebar button text
sidebar_font = pygame.font.Font('freesansbold.ttf', 22)

# YShift of text to make the sidebar text look decent in the button
sidebar_shiftY = 15

# Sidebar button specifications
sidebar_width = 200
sidebar_height = 50
sidebar_top_margin = 75
# X coordinate for the sidebar buttons
sidebarX = (500 - board_margin) + ((screen_width - 500 + board_margin)
                                   - sidebar_width) / 2
# Y coordinates for the sidebar buttons (will be 3)
sidebarY_list = [75, 150, 225]


# Returns a list of Rect representing the three sidebar buttons
def sidebar_rects():
    rects = []
    for i in sidebarY_list:
        rect = pygame.Rect(sidebarX, i, sidebar_width, sidebar_height)
        rects.append(rect)
    return rects


# Constant for the Rect representing the three sidebar buttons
(s_button1, s_button2, s_button3) = sidebar_rects()

# Constants for the copies of the sidebar buttons in the interactive sudoku
# puzzle
sudoku_sbutton1 = copy.copy(s_button1)  # The New Puzzle Button
sudoku_sbutton2 = copy.copy(s_button2)  # The See Solution Button
sudoku_sbutton3 = copy.copy(s_button3)  # The Quit Button


# Draws the sidebar buttons and text for the interactive sudoku puzzle
def draw_sudoku_sidebar():
    pygame.draw.rect(screen, rgb_white, sudoku_sbutton1)
    text1 = sidebar_font.render('New Puzzle', True, rgb_black)
    screen.blit(text1, (sidebarX + 40, sidebarY_list[0] + sidebar_shiftY))
    pygame.draw.rect(screen, rgb_white, sudoku_sbutton2)
    text2 = sidebar_font.render('See Solution', True, rgb_black)
    screen.blit(text2, (sidebarX + 34, sidebarY_list[1] + sidebar_shiftY))
    pygame.draw.rect(screen, rgb_white, sudoku_sbutton3)
    text3 = sidebar_font.render('Quit', True, rgb_black)
    screen.blit(text3, (sidebarX + 75, sidebarY_list[2] + sidebar_shiftY))


# Constants for the copies of the sidebar buttons in the interact solution
# display
solution_sbutton1 = copy.copy(s_button1)
solution_sbutton2 = copy.copy(s_button3)


# Draws the sidebar buttons and text for the interact solution display
def draw_solution_sidebar():
    pygame.draw.rect(screen, rgb_white, solution_sbutton1)
    text1 = sidebar_font.render('New Puzzle', True, rgb_black)
    screen.blit(text1, (sidebarX + 40, sidebarY_list[0] + sidebar_shiftY))
    pygame.draw.rect(screen, rgb_white, solution_sbutton2)
    text3 = sidebar_font.render('Quit', True, rgb_black)
    screen.blit(text3, (sidebarX + 75, sidebarY_list[2] + sidebar_shiftY))


# Constants for the copies of the sidebar buttons in the solver display
solver_sbutton1 = copy.copy(s_button1)
solver_sbutton2 = copy.copy(s_button3)


# Draws the sidebar buttons and text for the interact solution display
def draw_solver_sidebar():
    pygame.draw.rect(screen, rgb_white, solver_sbutton1)
    text1 = sidebar_font.render('Find Solution', True, rgb_black)
    screen.blit(text1, (sidebarX + 33, sidebarY_list[0] + sidebar_shiftY))
    pygame.draw.rect(screen, rgb_white, solver_sbutton2)
    text3 = sidebar_font.render('Quit', True, rgb_black)
    screen.blit(text3, (sidebarX + 75, sidebarY_list[2] + sidebar_shiftY))


# Constants for the copies of the sidebar buttons in the solver solution
# display
solver_solution_sbutton1 = copy.copy(s_button1)
solver_solution_sbutton2 = copy.copy(s_button3)


# Draws the sidebar buttons and text for the solver solution display
def draw_solver_solution_sidebar():
    pygame.draw.rect(screen, rgb_white, solver_solution_sbutton1)
    text1 = sidebar_font.render('Solve Another', True, rgb_black)
    screen.blit(text1, (sidebarX + 33, sidebarY_list[0] + sidebar_shiftY))
    pygame.draw.rect(screen, rgb_white, solver_solution_sbutton2)
    text3 = sidebar_font.render('Quit', True, rgb_black)
    screen.blit(text3, (sidebarX + 75, sidebarY_list[2] + sidebar_shiftY))


# END========================================================================

# ===========================================================================
# This sections contains all the functions for the solver and the solver
# solution

# Generates a dictionary with the coordinates for all the tiles on the board
# as the keys and 0 through 80 as the values (representing the indices in a
# string of length 81)
#   - ^ if the mode is set as 'f', if the mode is set as 'b' then the
#     coordinates will be the values and the indices will be the keys
def make_zero_dict(coords, mode):
    zero_dict = {}
    for i in range(81):
        if mode == 'f':
            zero_dict[coords[i]] = i
        elif mode == 'b':
            zero_dict[i] = coords[i]
    return zero_dict


# Creates the necessary constants to use the functions defined for the
# interactive sudoku display for the solver
def solver_constants():
    coords_zero = make_zero_dict(coords, 'f')
    zero_coords = make_zero_dict(coords, 'b')
    user_tries = '000000000000000000000000000000000000000' \
                 '000000000000000000000000000000000000000000'
    return (coords_zero, zero_coords, user_tries)


# Turns a 9x9 matrix of num into a string of 81 num
#   - undos the matrix creation by sudoku.py
def undo_matrix(matrix):
    num_str = ""
    for row in matrix:
        for num in row:
            num_str = num_str + str(num)
    return num_str


# Generates the solution to a given puzzle, if there is one, and masks it so
# that all numbers in the original puzzle are 0's in the solution
#   - if there is no solution, return False
def generate_solution(puzzle):
    user_board = SudokuAI(puzzle)
    board_works = user_board.solve_board()
    if not board_works:
        return False
    solution = undo_matrix(user_board.board)
    return solution


# Customize the error message text
error_font = pygame.font.Font('freesansbold.ttf', 18)
error_coords = (513, 350)


# Draws an error message on the side saying that there is no valid solution
# for the entered puzzle
def draw_error():
    error_text1 = error_font.render('The entered puzzle',
                                    True, rgb_black)
    error_text2 = error_font.render('is unsolvable.', True, rgb_black)
    (x, y) = error_coords
    screen.blit(error_text1, (x + 13, y))
    screen.blit(error_text2, (x + 40, y + 30))


# END========================================================================
# Constants generated from the previous functions
# List of coordinates of all tiles in the board
coords = get_board_coords()
# List of the Rect objects representing all of the tiles
rects = get_rects(coords)

# Functions representing the various screens that will be shown in the
# program
# Constant for the display that should be shown
display_state = "home"


# The initial home screen ('home')
def display_home():
    draw_home()


# The difficulty screen ('difficulty')
def display_difficulty():
    draw_difficulty()


# The screen for the interactive sudoku puzzle ('sudoku interact')
def display_sudoku_interact(puzzle):
    draw_board_background()
    draw_rects(rects)
    draw_sudoku_sidebar()
    draw_nums(puzzle, coords)


# The screen for the interactive sudoku puzzle with the solutions shown
# ('interact solution')
def display_interact_solutions(puzzle, solution, user_tries):
    draw_board_background()
    draw_rects(rects)
    draw_solution_sidebar()
    draw_nums(puzzle, coords)
    zeros_coords = get_zeros(puzzle, coords, 'f')
    draw_solution(solution, zeros_coords, user_tries)


# The screen for the solver ('solver')
def display_solver():
    draw_board_background()
    draw_rects(rects)
    draw_solver_sidebar()


# The screen for the solver's solution display ('solver solution')
def display_solver_solution(user_tries, zero_coords, solution):
    draw_board_background()
    draw_rects(rects)
    draw_solver_solution_sidebar()
    if solution == False:
        draw_error()
        display_user_input(user_tries, zero_coords, rgb_red)
    else:
        draw_nums(solution, coords)


# Presetting the ability for the user to edit tiles in the puzzle to False
valid_tile = False

# Game Loop
running = True
while running:
    # Gets the position of the mouse
    mouse = pygame.mouse.get_pos()

    # Checks if the user presses the exit button for the window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # This allows the user to interact with the buttons on the home
            # screen and use those buttons to go to other screens
            if display_state == 'home':
                if home_sudoku_button.collidepoint(mouse):
                    display_state = 'difficulty'
                elif home_solver_button.collidepoint(mouse):
                    (coords_zero, zero_coords, user_tries) = \
                        solver_constants()
                    display_state = 'solver'
            # This allows the user to interact with the buttons on the
            # difficulty screen and use those buttons to go to the
            # sudoku interact screen and to choose their difficulty
            elif display_state == 'difficulty':
                if diff1_button.collidepoint(mouse):
                    display_state = 'sudoku interact'
                    # This will generate a puzzle and solution, set the
                    # board representing all user's edits to it equal to the
                    # original board, and generate the corresponding
                    # dictionaries from get_zeros for the puzzle
                    (puzzle, solution, user_tries, zero_coords, coords_zero) \
                        = generate_puzzle(1)
                    # Determines if the user has selected a valid tile to
                    # input numbers
                    valid_tile = False
                elif diff2_button.collidepoint(mouse):
                    display_state = 'sudoku interact'
                    (puzzle, solution, user_tries, zero_coords, coords_zero) \
                        = generate_puzzle(2)
                    valid_tile = False
                elif diff3_button.collidepoint(mouse):
                    display_state = 'sudoku interact'
                    (puzzle, solution, user_tries, zero_coords, coords_zero) \
                        = generate_puzzle(3)
                    valid_tile = False
                elif diff4_button.collidepoint(mouse):
                    display_state = 'sudoku interact'
                    (puzzle, solution, user_tries, zero_coords, coords_zero) \
                        = generate_puzzle(4)
                    valid_tile = False
            # Allows the user to interact with the sudoku interactive display and
            # the solver
            elif display_state == 'sudoku interact' or display_state == 'solver':
                # This allow the user to enter values into the tiles

                # If the mouse click is not on a tile, then we are going to
                # change it so the user cannot edit tiles, as they haven't
                # selected one
                if on_tile(mouse, coords_zero) == False:
                    valid_tile = False
                else:
                    valid_tile = True
                    # Retrieves the data for the coordinates of the tile that
                    # the user has pressed, as well as the number currently
                    # on the tile
                    (tile_coords, index, previous_input) = \
                        tile_editable(mouse, coords_zero, user_tries)
                # Allows the user to press the sidebar buttons on the sudoku
                # interactive display
                if display_state == 'sudoku interact':
                    if sudoku_sbutton1.collidepoint(mouse):
                        display_state = 'difficulty'
                    elif sudoku_sbutton2.collidepoint(mouse):
                        display_state = 'interact solution'
                    elif sudoku_sbutton3.collidepoint(mouse):
                        display_state = 'home'
                # Allows the user to press the sidebar buttons on the solver
                if display_state == 'solver':
                    if solver_sbutton1.collidepoint(mouse):
                        display_state = 'solver solution'
                        solution = generate_solution(user_tries)
                    elif solver_sbutton2.collidepoint(mouse):
                        display_state = 'home'
            # Allows the user to interact with the interact solution display
            elif display_state == 'interact solution':
                # Allows the user to press the sidebar buttons
                if solution_sbutton1.collidepoint(mouse):
                    display_state = 'difficulty'
                elif solution_sbutton2.collidepoint(mouse):
                    display_state = 'home'
            # Allows the user to interact with the solver solution display
            elif display_state == 'solver solution':
                # Allows the user to press the sidebar buttons
                if solver_solution_sbutton1.collidepoint(mouse):
                    display_state = 'solver'
                    # Resets the constants
                    (coords_zero, zero_coords, user_tries) = \
                        solver_constants()
                elif solver_solution_sbutton2.collidepoint(mouse):
                    display_state = 'home'

        # If the user has already selected a tile in the interactive sudoku
        # display or the solver, then all their following inputs will be
        # edits to the number in that tile
        if event.type == pygame.KEYDOWN and valid_tile == True and \
                (display_state == 'sudoku interact' or
                 display_state == 'solver'):
            if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                user_tries = change_user_inputs(user_tries, '1', index)
            elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                user_tries = change_user_inputs(user_tries, '2', index)
            elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                user_tries = change_user_inputs(user_tries, '3', index)
            elif event.key == pygame.K_4 or event.key == pygame.K_KP4:
                user_tries = change_user_inputs(user_tries, '4', index)
            elif event.key == pygame.K_5 or event.key == pygame.K_KP5:
                user_tries = change_user_inputs(user_tries, '5', index)
            elif event.key == pygame.K_6 or event.key == pygame.K_KP6:
                user_tries = change_user_inputs(user_tries, '6', index)
            elif event.key == pygame.K_7 or event.key == pygame.K_KP7:
                user_tries = change_user_inputs(user_tries, '7', index)
            elif event.key == pygame.K_8 or event.key == pygame.K_KP8:
                user_tries = change_user_inputs(user_tries, '8', index)
            elif event.key == pygame.K_9 or event.key == pygame.K_KP9:
                user_tries = change_user_inputs(user_tries, '9', index)
            elif event.key == pygame.K_BACKSPACE:
                user_tries = change_user_inputs(user_tries, '0', index)

    # Sets the background color
    screen.fill(rgb_grey)

    # This will change the display depending on the display_state
    if display_state == 'home':
        display_home()
    elif display_state == 'difficulty':
        display_difficulty()
    elif display_state == 'sudoku interact':
        display_sudoku_interact(puzzle)
        # This will highlight a tile if the user selects it, that is, will
        # draw a tile over top of the original board
        if valid_tile == True:
            (x, y) = tile_coords
            pygame.draw.rect(screen, rgb_grey, (x, y, tile_size, tile_size))
        # This will display all of the user's inputs so far
        display_user_input(user_tries, zero_coords, rgb_blue)
    elif display_state == 'interact solution':
        display_interact_solutions(puzzle, solution, user_tries)
        display_user_input(user_tries, zero_coords, rgb_blue)
    elif display_state == 'solver':
        display_solver()
        # Same code as above, will hightlight the tile if the user selects it
        if valid_tile == True:
            (x, y) = tile_coords
            pygame.draw.rect(screen, rgb_grey, (x, y, tile_size, tile_size))
        display_user_input(user_tries, zero_coords, rgb_black)
    elif display_state == 'solver solution':
        display_solver_solution(user_tries, zero_coords, solution)

    # This will update the screen
    pygame.display.update()

# ===========================================================================
# ===========================================================================
