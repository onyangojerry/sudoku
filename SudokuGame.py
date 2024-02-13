
import copy
import time

"""
We have noticed that utilizing get_most_constrained_cell always returned a solution faster than using 
get_any_available_cell. get_most_constrained_cell returned times of 0.02, 0.07, and 3.91 seconds, compared to 0.17, 
2.51, and 25.89 seconds returned by get_any_available_cell. For the second experiment, we noticed that adding the 
propagate method helped solve the problem much quicker than without it. We assume that the propagate method helps to 
find the one remaining spot, and add a number just through a single iteration which helps save time.
"""


class SudokuState:
    def __init__(self):
        """
        Creates the Sudoku board.
        """
        self.size = 9
        self.num_placed = 0
        self.board = []  # empty list to append the rows
        for i in range(self.size):  # creates the sudoku board which is size by size
            row = []  # empty list to append the columns
            for j in range(self.size):
                row.append(SudokuEntry())
            self.board.append(row)

    def remove_conflict(self, row, col, num):
        """
        If entry at the row and column has not been filled in yet, removes the number from the list of possible values
        at this entry.
        :param row: (int) Row that hasn't been filled in
        :param col: (int) Column that hasn't been filled in
        :param num: (int) Number to be removed from list of possible values
        :return: None
        """
        if not self.board[row][col].is_fixed():  # checks if the value is not fixed
            self.board[row][col].eliminate(num)  # removes the already existing number if the value is not fixed

    def remove_all_conflicts(self, row, col, num):
        """
        Updates unfilled entries in same row, column, subgrid so that they no longer have the given number as an option.
        :param row: (int) Row that the number has been placed in
        :param col: (int) Column that the number has been placed in
        :param num: (int) Number that has been placed
        :return: None
        """
        for i in range(self.size):  # iterates through the board
            self.remove_conflict(i, col, num)  # removes the conflict in row

        for j in range(self.size):  # iterates through the column
            self.remove_conflict(row, j, num)  # removes conflict in column

        for k in range(self.size):  # iterates through the board
            for l in range(self.size):
                if self.get_subgrid_number(k, l) == self.get_subgrid_number(row, col):  # identifies the subgrid
                    self.remove_conflict(k, l, num)  # removes conflict

    def add_number(self, row, col, num):
        """
        Adds the given number at row, column.
        :param row: (int) Row to add number in
        :param col: (int) Column to add number in
        :param num: (int) Number to be added
        :return: None
        """
        self.board[row][col].fix(num)  # puts number num at this entry
        self.num_placed += 1  # updates the number of entries added
        self.remove_all_conflicts(row, col, num)  # checks through the row column and sub grid to remove conflicts

    def get_most_constrained_cell(self):
        """
        Creates tuple that returns the entry that is not filled in yet that has the fewest possible options remaining.
        :return: (tuple) Tuple containing the row and column of the most constrained entry in board.
        """
        dom = self.size
        location = None
        for row in range(self.size):  # iterates through the board
            for col in range(self.size):
                if not self.board[row][col].is_fixed() and self.board[row][col].width() <= dom:
                    dom = self.board[row][col].width()
                    location = (row, col)  # returns the location in form of a tuple
        return location

    def solution_is_possible(self):
        """
        Checks if a solution is possible by checking if all entries on the board still have at least one possible value
        that they can take.
        :return: (bool) True if all entries can take on at least one possible value, False otherwise
        """
        for row in range(self.size):  # iterates through the board
            for col in range(self.size):
                if self.board[row][col].has_conflict():  # checks if number is fixed and removes it if not fixed
                    return False
        return True

    def next_states(self):
        """
        Checks for least constrained everytime and returns a list of all possible next states by getting most
        constrained cell, and fixing a number there.
        :return: (list) List of next states that can be reached from current state
        """
        next_state = []  # empty list to append all possible next states
        row, col = self.get_most_constrained_cell()  # recognizes the elements of the tuple with least possible domains
        for value in self.board[row][col].values():  # iterates through the board
            new_board = copy.deepcopy(self)  # creates a new copy of the board
            new_board.add_number(row, col, value)  # adds number to the location
            new_board.propagate()  # increases the search speed
            if new_board.solution_is_possible():  # checks if the position is valid
                next_state.append(new_board)  # adds the position the new list
        return next_state

    def is_goal(self):
        """
        Checks if all the spots in the sudoku board have been filled.
        :return: (bool) True if goal state, False otherwise
        """
        return self.size * self.size == self.num_placed

    def get_subgrid_number(self, row, col):
        """
        Returns a number between 1 and 9 representing the subgrid
        that this row, col is in.  The top left subgrid is 1, then
        2 to the right, then 3 in the upper right, etc.
        """
        row_q = int(row / 3)
        col_q = int(col / 3)
        return row_q * 3 + col_q + 1

    def get_any_available_cell(self):
        """
        An uninformed cell finding variant.  If you use
        this instead of find_most_constrained_cell
        the search will perform a depth first search.
        """
        for r in range(self.size):
            for c in range(self.size):
                if not self.board[r][c].is_fixed():
                    return (r, c)
        return None

    def propagate(self):
        for ri in range(self.size):
            for ci in range(self.size):
                if not self.board[ri][ci].is_fixed() and \
                        self.board[ri][ci].width() == 1:
                    self.add_number(ri, ci, self.board[ri][ci].values()[0])
                    if self.solution_is_possible():
                        self.propagate()
                        return

    def get_raw_string(self):
        board_str = ""

        for r in self.board:
            board_str += str(r) + "\n"

        return "num placed: " + str(self.num_placed) + "\n" + board_str

    def __str__(self):
        """
        prints all numbers assigned to cells.  Unassigned cells (i.e.
        those with a list of options remaining are printed as blanks
        """
        board_string = ""

        for r in range(self.size):
            if r % 3 == 0:
                board_string += " " + "-" * (self.size * 2 + 5) + "\n"

            for c in range(self.size):
                entry = self.board[r][c]

                if c % 3 == 0:
                    board_string += "| "

                board_string += str(entry) + " "

            board_string += "|\n"

        board_string += " " + "-" * (self.size * 2 + 5) + "\n"

        return "num placed: " + str(self.num_placed) + "\n" + board_string


# -----------------------------------------------------------------------
# Make all of your changes to the SudokuState class above.
# only when you're running the last experiments will
# you need to change anything below here and then only
# the different problem inputs

class SudokuEntry:
    def __init__(self):
        self.fixed = False
        self.domain = list(range(1, 10))

    def is_fixed(self):
        return self.fixed

    def width(self):
        return len(self.domain)

    def values(self):
        return self.domain

    def has_conflict(self):
        return len(self.domain) == 0

    def __str__(self):
        if self.fixed:
            return str(self.domain[0])
        return "_"

    def __repr__(self):
        if self.fixed:
            return str(self.domain[0])
        return str(self.domain)

    def fix(self, n):
        assert n in self.domain
        self.domain = [n]
        self.fixed = True

    def eliminate(self, n):
        if n in self.domain:
            assert not self.fixed
            self.domain.remove(n)


# -----------------------------------
# Even though this is the same DFS code
# that we used last time, our next_states
# function is making an "informed" decision
# so this algorithm performs similarly to
# best first search.


def dfs(state):
    """
    Recursive depth first search implementation

    Input:
    Takes as input a state.  The state class MUST have the following
    methods implemented:
    - is_goal(): returns True if the state is a goal state, False otherwise
    - next_states(): returns a list of the VALID states that can be
    reached from the current state

    Output:
    Returns a list of ALL states that are solutions (i.e. is_goal
    returned True) that can be reached from the input state.
    """
    # if the current state is a goal state, then return it in a list
    if state.is_goal():
        return [state]
    else:
        # make a list to accumulate the solutions in
        result = []

        for s in state.next_states():
            result += dfs(s)

        return result


# ------------------------------------
# three different board configurations:
# - problem1
# - problem2
# - heart (example from class notes)


def problem1():
    b = SudokuState()
    b.add_number(0, 1, 7)
    b.add_number(0, 7, 1)
    b.add_number(1, 2, 9)
    b.add_number(1, 3, 7)
    b.add_number(1, 5, 4)
    b.add_number(1, 6, 2)
    b.add_number(2, 2, 8)
    b.add_number(2, 3, 9)
    b.add_number(2, 6, 3)
    b.add_number(3, 1, 4)
    b.add_number(3, 2, 3)
    b.add_number(3, 4, 6)
    b.add_number(4, 1, 9)
    b.add_number(4, 3, 1)
    b.add_number(4, 5, 8)
    b.add_number(4, 7, 7)
    b.add_number(5, 4, 2)
    b.add_number(5, 6, 1)
    b.add_number(5, 7, 5)
    b.add_number(6, 2, 4)
    b.add_number(6, 5, 5)
    b.add_number(6, 6, 7)
    b.add_number(7, 2, 7)
    b.add_number(7, 3, 4)
    b.add_number(7, 5, 1)
    b.add_number(7, 6, 9)
    b.add_number(8, 1, 3)
    b.add_number(8, 7, 8)
    return b


def problem2():
    b = SudokuState()
    b.add_number(0, 1, 2)
    b.add_number(0, 3, 3)
    b.add_number(0, 5, 5)
    b.add_number(0, 7, 4)
    b.add_number(1, 6, 9)
    b.add_number(2, 1, 7)
    b.add_number(2, 4, 4)
    b.add_number(2, 7, 8)
    b.add_number(3, 0, 1)
    b.add_number(3, 2, 7)
    b.add_number(3, 5, 9)
    b.add_number(3, 8, 2)
    b.add_number(4, 1, 9)
    b.add_number(4, 4, 3)
    b.add_number(4, 7, 6)
    b.add_number(5, 0, 6)
    b.add_number(5, 3, 7)
    b.add_number(5, 6, 5)
    b.add_number(5, 8, 8)
    b.add_number(6, 1, 1)
    b.add_number(6, 4, 9)
    b.add_number(6, 7, 2)
    b.add_number(7, 2, 6)
    b.add_number(8, 1, 4)
    b.add_number(8, 3, 8)
    b.add_number(8, 5, 7)
    b.add_number(8, 7, 5)
    return b


def heart():
    b = SudokuState()
    b.add_number(1, 1, 4)
    b.add_number(1, 2, 3)
    b.add_number(1, 6, 6)
    b.add_number(1, 7, 7)
    b.add_number(2, 0, 5)
    b.add_number(2, 3, 4)
    b.add_number(2, 5, 2)
    b.add_number(2, 8, 8)
    b.add_number(3, 0, 8)
    b.add_number(3, 4, 6)
    b.add_number(3, 8, 1)
    b.add_number(4, 0, 2)
    b.add_number(4, 8, 5)
    b.add_number(5, 1, 5)
    b.add_number(5, 7, 4)
    b.add_number(6, 2, 6)
    b.add_number(6, 6, 7)
    b.add_number(7, 3, 5)
    b.add_number(7, 5, 1)
    b.add_number(8, 4, 8)
    return b


# --------------------------------
# Code that actual runs a sudoku problem, times it
# and prints out the solution.
# You can vary which problem your running on between
# problem1(), problem2() and heart() by changing the line
# below
#
# Uncomment this code when you have everything implemented and you
# want to solve some of the sample problems!

# problem = heart()
# print("Starting board:")
# print(problem)
#
# start_time = time.time()
# solutions = dfs(problem)
# search_time = time.time() - start_time
#
# print("Search took " + str(round(search_time, 2)) + " seconds")
# print("There was " + str(len(solutions)) + " solution.\n\n")
# if len(solutions) > 0:
#     print(solutions[0])

"""
Problem 1
get_most_constrained_cell
Starting board:
num placed: 28
 -----------------------
| _ 7 _ | _ _ _ | _ 1 _ |
| _ _ 9 | 7 _ 4 | 2 _ _ |
| _ _ 8 | 9 _ _ | 3 _ _ |
 -----------------------
| _ 4 3 | _ 6 _ | _ _ _ |
| _ 9 _ | 1 _ 8 | _ 7 _ |
| _ _ _ | _ 2 _ | 1 5 _ |
 -----------------------
| _ _ 4 | _ _ 5 | 7 _ _ |
| _ _ 7 | 4 _ 1 | 9 _ _ |
| _ 3 _ | _ _ _ | _ 8 _ |
 -----------------------
Search took 0.02 seconds
There was 1 solution.
num placed: 81
 -----------------------
| 4 7 2 | 6 8 3 | 5 1 9 |
| 3 1 9 | 7 5 4 | 2 6 8 |
| 5 6 8 | 9 1 2 | 3 4 7 |
 -----------------------
| 1 4 3 | 5 6 7 | 8 9 2 |
| 2 9 5 | 1 4 8 | 6 7 3 |
| 7 8 6 | 3 2 9 | 1 5 4 |
 -----------------------
| 6 2 4 | 8 9 5 | 7 3 1 |
| 8 5 7 | 4 3 1 | 9 2 6 |
| 9 3 1 | 2 7 6 | 4 8 5 |
 -----------------------

get_any_available_cell
Starting board:
num placed: 28
 -----------------------
| _ 7 _ | _ _ _ | _ 1 _ |
| _ _ 9 | 7 _ 4 | 2 _ _ |
| _ _ 8 | 9 _ _ | 3 _ _ |
 -----------------------
| _ 4 3 | _ 6 _ | _ _ _ |
| _ 9 _ | 1 _ 8 | _ 7 _ |
| _ _ _ | _ 2 _ | 1 5 _ |
 -----------------------
| _ _ 4 | _ _ 5 | 7 _ _ |
| _ _ 7 | 4 _ 1 | 9 _ _ |
| _ 3 _ | _ _ _ | _ 8 _ |
 -----------------------
Search took 0.17 seconds
There was 1 solution.
num placed: 81
 -----------------------
| 4 7 2 | 6 8 3 | 5 1 9 |
| 3 1 9 | 7 5 4 | 2 6 8 |
| 5 6 8 | 9 1 2 | 3 4 7 |
 -----------------------
| 1 4 3 | 5 6 7 | 8 9 2 |
| 2 9 5 | 1 4 8 | 6 7 3 |
| 7 8 6 | 3 2 9 | 1 5 4 |
 -----------------------
| 6 2 4 | 8 9 5 | 7 3 1 |
| 8 5 7 | 4 3 1 | 9 2 6 |
| 9 3 1 | 2 7 6 | 4 8 5 |
 -----------------------


Problem 2
get_most_constrained_cell
Starting board:
num placed: 27
 -----------------------
| _ 2 _ | 3 _ 5 | _ 4 _ |
| _ _ _ | _ _ _ | 9 _ _ |
| _ 7 _ | _ 4 _ | _ 8 _ |
 -----------------------
| 1 _ 7 | _ _ 9 | _ _ 2 |
| _ 9 _ | _ 3 _ | _ 6 _ |
| 6 _ _ | 7 _ _ | 5 _ 8 |
 -----------------------
| _ 1 _ | _ 9 _ | _ 2 _ |
| _ _ 6 | _ _ _ | _ _ _ |
| _ 4 _ | 8 _ 7 | _ 5 _ |
 -----------------------
Search took 0.07 seconds
There was 1 solution.
num placed: 81
 -----------------------
| 8 2 9 | 3 1 5 | 6 4 7 |
| 4 6 3 | 2 7 8 | 9 1 5 |
| 5 7 1 | 9 4 6 | 2 8 3 |
 -----------------------
| 1 5 7 | 6 8 9 | 4 3 2 |
| 2 9 8 | 5 3 4 | 7 6 1 |
| 6 3 4 | 7 2 1 | 5 9 8 |
 -----------------------
| 7 1 5 | 4 9 3 | 8 2 6 |
| 9 8 6 | 1 5 2 | 3 7 4 |
| 3 4 2 | 8 6 7 | 1 5 9 |
 -----------------------

get_any_available_cell
Starting board:
num placed: 27
 -----------------------
| _ 2 _ | 3 _ 5 | _ 4 _ |
| _ _ _ | _ _ _ | 9 _ _ |
| _ 7 _ | _ 4 _ | _ 8 _ |
 -----------------------
| 1 _ 7 | _ _ 9 | _ _ 2 |
| _ 9 _ | _ 3 _ | _ 6 _ |
| 6 _ _ | 7 _ _ | 5 _ 8 |
 -----------------------
| _ 1 _ | _ 9 _ | _ 2 _ |
| _ _ 6 | _ _ _ | _ _ _ |
| _ 4 _ | 8 _ 7 | _ 5 _ |
 -----------------------
Search took 2.51 seconds
There was 1 solution.
num placed: 81
 -----------------------
| 8 2 9 | 3 1 5 | 6 4 7 |
| 4 6 3 | 2 7 8 | 9 1 5 |
| 5 7 1 | 9 4 6 | 2 8 3 |
 -----------------------
| 1 5 7 | 6 8 9 | 4 3 2 |
| 2 9 8 | 5 3 4 | 7 6 1 |
| 6 3 4 | 7 2 1 | 5 9 8 |
 -----------------------
| 7 1 5 | 4 9 3 | 8 2 6 |
| 9 8 6 | 1 5 2 | 3 7 4 |
| 3 4 2 | 8 6 7 | 1 5 9 |
 -----------------------


 Heart Problem
 get_most_constrained_cell
 Starting board:
num placed: 20
 -----------------------
| _ _ _ | _ _ _ | _ _ _ |
| _ 4 3 | _ _ _ | 6 7 _ |
| 5 _ _ | 4 _ 2 | _ _ 8 |
 -----------------------
| 8 _ _ | _ 6 _ | _ _ 1 |
| 2 _ _ | _ _ _ | _ _ 5 |
| _ 5 _ | _ _ _ | _ 4 _ |
 -----------------------
| _ _ 6 | _ _ _ | 7 _ _ |
| _ _ _ | 5 _ 1 | _ _ _ |
| _ _ _ | _ 8 _ | _ _ _ |
 -----------------------
Search took 3.91 seconds
There was 1 solution.
num placed: 81
 -----------------------
| 7 2 8 | 9 3 6 | 5 1 4 |
| 9 4 3 | 1 5 8 | 6 7 2 |
| 5 6 1 | 4 7 2 | 9 3 8 |
 -----------------------
| 8 3 4 | 7 6 5 | 2 9 1 |
| 2 1 7 | 8 4 9 | 3 6 5 |
| 6 5 9 | 2 1 3 | 8 4 7 |
 -----------------------
| 1 8 6 | 3 2 4 | 7 5 9 |
| 3 7 2 | 5 9 1 | 4 8 6 |
| 4 9 5 | 6 8 7 | 1 2 3 |
 -----------------------

 get_any_available_cell
 Starting board:
num placed: 20
 -----------------------
| _ _ _ | _ _ _ | _ _ _ |
| _ 4 3 | _ _ _ | 6 7 _ |
| 5 _ _ | 4 _ 2 | _ _ 8 |
 -----------------------
| 8 _ _ | _ 6 _ | _ _ 1 |
| 2 _ _ | _ _ _ | _ _ 5 |
| _ 5 _ | _ _ _ | _ 4 _ |
 -----------------------
| _ _ 6 | _ _ _ | 7 _ _ |
| _ _ _ | 5 _ 1 | _ _ _ |
| _ _ _ | _ 8 _ | _ _ _ |
 -----------------------
Search took 25.89 seconds
There was 1 solution.
num placed: 81
 -----------------------
| 7 2 8 | 9 3 6 | 5 1 4 |
| 9 4 3 | 1 5 8 | 6 7 2 |
| 5 6 1 | 4 7 2 | 9 3 8 |
 -----------------------
| 8 3 4 | 7 6 5 | 2 9 1 |
| 2 1 7 | 8 4 9 | 3 6 5 |
| 6 5 9 | 2 1 3 | 8 4 7 |
 -----------------------
| 1 8 6 | 3 2 4 | 7 5 9 |
| 3 7 2 | 5 9 1 | 4 8 6 |
| 4 9 5 | 6 8 7 | 1 2 3 |
 -----------------------

Propagate Method
get_most_constrained_cell
Starting board:
num placed: 20
 -----------------------
| _ _ _ | _ _ _ | _ _ _ |
| _ 4 3 | _ _ _ | 6 7 _ |
| 5 _ _ | 4 _ 2 | _ _ 8 |
 -----------------------
| 8 _ _ | _ 6 _ | _ _ 1 |
| 2 _ _ | _ _ _ | _ _ 5 |
| _ 5 _ | _ _ _ | _ 4 _ |
 -----------------------
| _ _ 6 | _ _ _ | 7 _ _ |
| _ _ _ | 5 _ 1 | _ _ _ |
| _ _ _ | _ 8 _ | _ _ _ |
 -----------------------
Search took 1.88 seconds
There was 1 solution.
num placed: 81
 -----------------------
| 7 2 8 | 9 3 6 | 5 1 4 |
| 9 4 3 | 1 5 8 | 6 7 2 |
| 5 6 1 | 4 7 2 | 9 3 8 |
 -----------------------
| 8 3 4 | 7 6 5 | 2 9 1 |
| 2 1 7 | 8 4 9 | 3 6 5 |
| 6 5 9 | 2 1 3 | 8 4 7 |
 -----------------------
| 1 8 6 | 3 2 4 | 7 5 9 |
| 3 7 2 | 5 9 1 | 4 8 6 |
| 4 9 5 | 6 8 7 | 1 2 3 |
 -----------------------

 get_any_available_cell
 Starting board:
num placed: 20
 -----------------------
| _ _ _ | _ _ _ | _ _ _ |
| _ 4 3 | _ _ _ | 6 7 _ |
| 5 _ _ | 4 _ 2 | _ _ 8 |
 -----------------------
| 8 _ _ | _ 6 _ | _ _ 1 |
| 2 _ _ | _ _ _ | _ _ 5 |
| _ 5 _ | _ _ _ | _ 4 _ |
 -----------------------
| _ _ 6 | _ _ _ | 7 _ _ |
| _ _ _ | 5 _ 1 | _ _ _ |
| _ _ _ | _ 8 _ | _ _ _ |
 -----------------------
Search took 3.5 seconds
There was 1 solution.
num placed: 81
 -----------------------
| 7 2 8 | 9 3 6 | 5 1 4 |
| 9 4 3 | 1 5 8 | 6 7 2 |
| 5 6 1 | 4 7 2 | 9 3 8 |
 -----------------------
| 8 3 4 | 7 6 5 | 2 9 1 |
| 2 1 7 | 8 4 9 | 3 6 5 |
| 6 5 9 | 2 1 3 | 8 4 7 |
 -----------------------
| 1 8 6 | 3 2 4 | 7 5 9 |
| 3 7 2 | 5 9 1 | 4 8 6 |
| 4 9 5 | 6 8 7 | 1 2 3 |
 -----------------------
"""
