#!/usr/bin/python3

"""
Soma Cube solver by Rich Holmes
derived from Pentominos solver by MiniMax
https://codereview.stackexchange.com/questions/233300/solving-pentomino-puzzles-by-using-knuths-algorithm-x

No licensing information is shown in MiniMax's listing. For my
contributions CC0 1.0 applies.
"""

"""
Some terminology:

*Cells* are individual little cubes. They are organized into:

*Rows*, 1-dimensional arrays of cells. They run in the x direction,
 with x=0 at the left, x=*width* at the right. Rows are organized into:

*Planes*, 2-dimensional. Rows in a plane run in the y direction, with
 y=0 at the front and y=*depth* at the back. Planes are organized
 into:

*Volume*, 3-dimensional. Planes in the volume run in the z direction,
 with z=0 at the bottom and z=*height* at the top.

(None of this is to be confused with the matrix used by the X
algorithm.)
"""

from time import time
from datetime import timedelta
from copy import deepcopy
import argparse
from termcolor import colored
import json


class Node():
    def __init__(self, value):
        self.value = value
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.row_head = None
        self.col_head = None
    __slots__ = ('value', 'up', 'down', 'left', 'right', 'row_head', 'col_head')

class Linked_list_2D():
    def __init__(self, width):
        self.width = width
        self.head = None
        self.size = 0

    def append(self, value):
        new_node = Node(value)

        if self.head is None:
            self.head = left_neigh = right_neigh = up_neigh = down_neigh = new_node
        elif self.size % self.width == 0:
            up_neigh = self.head.up
            down_neigh = self.head
            left_neigh = right_neigh = new_node
        else:
            left_neigh = self.head.up.left
            right_neigh = left_neigh.right
            if left_neigh is left_neigh.up:
                up_neigh = down_neigh = new_node
            else:
                up_neigh = left_neigh.up.right
                down_neigh = up_neigh.down

        new_node.up = up_neigh
        new_node.down = down_neigh
        new_node.left = left_neigh
        new_node.right = right_neigh
        # Every node has links to the first node of row and column
        # These nodes are used as the starting point to deletion and insertion
        new_node.row_head = right_neigh
        new_node.col_head = down_neigh

        up_neigh.down = new_node
        down_neigh.up = new_node
        right_neigh.left = new_node
        left_neigh.right = new_node

        self.size += 1

    def print_list(self, separator=' '):
        for row in self.traverse_node_line(self.head, "down"):
            for col in self.traverse_node_line(row, "right"):
                print(col.value, end=separator)
            print()

    def traverse_node_line(self, start_node, direction):
        cur_node = start_node
        while cur_node:
            yield cur_node
            cur_node = getattr(cur_node, direction)
            if cur_node is start_node:
                break

    def col_nonzero_nodes(self, node):
        cur_node = node
        while cur_node:
            if cur_node.value and cur_node.row_head is not self.head:
                yield cur_node
            cur_node = cur_node.down
            if cur_node is node:
                break

    def row_nonzero_nodes(self, node):
        cur_node = node
        while cur_node:
            if cur_node.value and cur_node.col_head is not self.head:
                yield cur_node
            cur_node = cur_node.right
            if cur_node is node:
                break

    def delete_row(self, node):
        cur_node = node
        while cur_node:
            up_neigh = cur_node.up
            down_neigh = cur_node.down

            if cur_node is self.head:
                self.head = down_neigh
                if cur_node is down_neigh:
                    self.head = None

            up_neigh.down = down_neigh
            down_neigh.up = up_neigh

            cur_node = cur_node.right
            if cur_node is node:
                break

    def insert_row(self, node):
        cur_node = node
        while cur_node:
            up_neigh = cur_node.up
            down_neigh = cur_node.down

            up_neigh.down = cur_node
            down_neigh.up = cur_node

            cur_node = cur_node.right
            if cur_node is node:
                break

    def insert_col(self, node):
        cur_node = node
        while cur_node:
            left_neigh = cur_node.left
            right_neigh = cur_node.right

            left_neigh.right = cur_node
            right_neigh.left = cur_node

            cur_node = cur_node.down
            if cur_node is node:
                break

    def delete_col(self, node):
        cur_node = node
        while cur_node:
            left_neigh = cur_node.left
            right_neigh = cur_node.right

            if cur_node is self.head:
                self.head = right_neigh
                if cur_node is right_neigh:
                    self.head = None

            left_neigh.right = right_neigh
            right_neigh.left = left_neigh

            cur_node = cur_node.down
            if cur_node is node:
                break

class Puzzle():
    def __init__(self, desc, defmodel, pieces):
        self.desc = desc
        self.defmodel = defmodel
        self.pieces = pieces
        self.ncubes = 0
        for p in pieces:
            for plane in pieces[p]:
                for row in plane:
                    for cell in row:
                        self.ncubes += 1 if cell == 1 else 0

soma_puzzle = Puzzle(
    "Soma Cube (by Piet Hein)",
    "cube3",
    {
        'W': (((1,1), (1,0)),),

        'Y': (((1,1,1), (1,0,0)),),

        'G': (((1,1,1), (0,1,0)),),

        'O': (((1,1,0), (0,1,1)),),

        'L': (((1,1), (1,0)),
              ((0,0), (1,0))),

        'R': (((1,1), (1,0)),
              ((0,1), (0,0))),

        'B': (((1,1), (1,0)),
              ((1,0), (0,0)))
    }
)

double_soma_puzzle = Puzzle(# For 2-set models
    "2 sets Soma Cube",
    "blockhouse",
    {
        'W': (((1,1), (1,0)),),

        'Y': (((1,1,1), (1,0,0)),),

        'G': (((1,1,1), (0,1,0)),),

        'O': (((1,1,0), (0,1,1)),),

        'L': (((1,1), (1,0)),
              ((0,0), (1,0))),

        'R': (((1,1), (1,0)),
              ((0,1), (0,0))),

        'B': (((1,1), (1,0)),
              ((1,0), (0,0))),

        'w': (((1,1), (1,0)),),

        'y': (((1,1,1), (1,0,0)),),

        'g': (((1,1,1), (0,1,0)),),

        'o': (((1,1,0), (0,1,1)),),

        'l': (((1,1), (1,0)),
              ((0,0), (1,0))),

        'r': (((1,1), (1,0)),
              ((0,1), (0,0))),

        'b': (((1,1), (1,0)),
              ((1,0), (0,0)))
    }
)

bedlam_puzzle = Puzzle(
    "Bedlam Cube (by Bruce Bedlam)",
    "cube4",
    {
        '0': (((0,1,0),),
              ((1,1,1),),
              ((0,0,1),)),
        '1': (((0,1,0),),
              ((1,1,1),),
              ((0,1,0),)),
        '2': (((1,1,0),),
              ((0,1,1),),
              ((0,0,1),)),
        '3': (((0,0,1), (0,1,1)),
              ((0,0,0), (1,1,0))),
        '4': (((0,1,0), (1,1,1)),
              ((0,0,0), (0,1,0))),
        '5': (((0,1,0), (0,1,1)),
              ((0,0,0), (1,1,0))),
        '6': (((0,1,0), (0,1,0)),
              ((0,0,0), (1,1,1))),
        '7': (((1,0,0), (1,1,1)),
              ((0,0,0), (1,0,0))),
        '8': (((0,0,1), (1,1,1)),
              ((0,0,0), (1,0,0))),
        '9': (((0,0,0), (1,1,1)),
              ((0,0,1), (0,0,1))),
        'A': (((0,0,0), (0,1,1)),
              ((1,1,0), (0,1,0))),
        'B': (((0,1,0), (1,1,1)),
              ((0,0,0), (1,0,0))),
        'C': (((1,0), (1,1)),
              ((0,0), (0,1))),
    }
)

diabolical_puzzle = Puzzle(
    "Diabolical Cube (pub. by Angelo Lewis)",
    "cube3",
    {
        '2': (((1,1),),),
        '3': (((1,1),),
              ((1,0),)),
        '4': (((1,1),),
              ((1,1),)),
        '5': (((1,1),),
              ((1,0),),
              ((1,1),)),
        '6': (((1,1,1),),
              ((1,1,0),),
              ((1,0,0),)),
        '7': (((1,1,0),),
              ((1,1,0),),
              ((1,1,1),))
    }
)

sg_puzzle = Puzzle(
    "Slothouber-Graatsma puzzle (by Jan Slothouber and William Graatsma)",
    "cube3",
    {
        'a' : (((1,1), (1,1)),),
        'b' : (((1,1), (1,1)),),
        'c' : (((1,1), (1,1)),),
        'd' : (((1,1), (1,1)),),
        'e' : (((1,1), (1,1)),),
        'f' : (((1,1), (1,1)),),
        'g' : (((1,),),),
        'h' : (((1,),),),
        'i' : (((1,),),)
    }
)

conway_puzzle = Puzzle(
    "Conway puzzle (Blocks-In-a-Box) (by John Conway)",
    "cube5",
    {
        'a' : (((1,1,1,1), (1,1,1,1)),),
        'b' : (((1,1,1,1), (1,1,1,1)),),
        'c' : (((1,1,1,1), (1,1,1,1)),),
        'd' : (((1,1,1,1), (1,1,1,1)),),
        'e' : (((1,1,1,1), (1,1,1,1)),),
        'f' : (((1,1,1,1), (1,1,1,1)),),
        'g' : (((1,1,1,1), (1,1,1,1)),),
        'h' : (((1,1,1,1), (1,1,1,1)),),
        'i' : (((1,1,1,1), (1,1,1,1)),),
        'j' : (((1,1,1,1), (1,1,1,1)),),
        'k' : (((1,1,1,1), (1,1,1,1)),),
        'l' : (((1,1,1,1), (1,1,1,1)),),
        'm' : (((1,1,1,1), (1,1,1,1)),),
        'n' : (((1,1), (1,1)),),
        'o' : (((1,1), (1,1)),
               ((1,1), (1,1)),),
        'p' : (((1,1,1),),),
        'q' : (((1,1,1),),),
        'r' : (((1,1,1),),),
    }
)

pentomino_puzzle = Puzzle(
    "Solid Pentominoes (by Solomon Golomb)",
    "r06x10",
    {
        'F' : (((0,1,1), (1,1,0), (0,1,0),),),
        'I' : (((1,1,1,1,1),),),
        'L' : (((1,1,1,1), (1,0,0,0),),),
        'N' : (((1,1,0,0), (0,1,1,1),),),
        'P' : (((1,1), (1,1), (1,0),),),
        'T' : (((1,1,1), (0,1,0), (0,1,0),),),
        'U' : (((1,0,1), (1,1,1),),),
        'V' : (((1,0,0), (1,0,0), (1,1,1),),),
        'W' : (((1,0,0), (1,1,0), (0,1,1),),),
        'X' : (((0,1,0), (1,1,1), (0,1,0),),),
        'Y' : (((0,0,1,0), (1,1,1,1),),),
        'Z' : (((1,1,0), (0,1,0), (0,1,1),),),
    }
)

class Solver():
    named_pieces = set()
    all_piece_postures = set()
    piece_copies = {}
    piece_mirrors = {}

    def __init__(self, volume=None, height=None, depth=None, width=None, puzzle=soma_puzzle):
        if volume is None:
            volume = [[[""] * width for _ in range(depth)] for _ in range (height)]
        if height is None and width is None:
            height = len(volume)
            depth = len(volume[0])
            width = len(volume[0][0])
        self.height = height
        self.depth = depth
        self.width = width
        self.named_pieces = set(zip(puzzle.pieces.keys(), puzzle.pieces.values()))
        self.solutions = set()
        self.reduced_solutions = set()
        self.llist = None
        self.start_volume = volume
        self.tried_variants_num = 0
        self.all_piece_postures = self.unique_piece_postures(self.named_pieces)
        self.piece_copies = self.get_piece_copies()
        self.piece_mirrors = self.get_piece_mirrors()

    def get_piece_copies(self):
        """
        Return dictionary of pieces identical to other pieces
        """
        spc = {}
        for p1 in self.named_pieces:
            for p2 in self.all_piece_postures:
                if p1[1] == p2[1]:
                    if p1[0] not in spc or \
                       p2[0] < spc[p1[0]]:
                        spc[p1[0]] = p2[0]
        return spc

    def get_piece_mirrors(self):
        """
        Return dictionary of pieces that are mirrors of other pieces
        """
        spm = {}
        for p1 in self.named_pieces:
            for p2 in self.all_piece_postures:
                if p1[1] == p2[1][::-1]:
                    if p1[0] not in spm or \
                       p2[0] < spm[p1[0]]:
                        spm[p1[0]] = p2[0]
        return spm

    def reduce_solution(self, sol):
        """
        Replace each piece in sol with its canonical identical piece
        """
        sol2 = tuple(tuple(tuple(cell if cell not in self.piece_copies else self.piece_copies[cell] \
                  for cell in row) for row in plane) for plane in sol)
        return sol2

    def find_solutions(self, stop=False):
        self.llist = Linked_list_2D(self.height * self.depth * self.width + 1)
        pos_gen = self.generate_positions(self.all_piece_postures, self.width, self.depth, self.height)

        for line in pos_gen:
            for val in line:
                self.llist.append(val)

        self.delete_filled_on_start_cells(self.llist)

        self.starttime = time()
        self.prevtime = self.starttime
        self.dlx_alg(self.llist, self.start_volume, stop)

    # Converts a one dimensional's element index to two dimensional's coordinates
    def num_to_coords(self, num):
        plane = num // (self.depth * self.width)
        num = num - plane * self.depth * self.width
        row = num // self.width
        cell = num - row * self.width
        return plane, row, cell

    def delete_filled_on_start_cells(self, llist):
        for col_head_node in llist.row_nonzero_nodes(llist.head):
            plane, row, cell = self.num_to_coords(col_head_node.value - 1)
            if self.start_volume[plane][row][cell]:
                llist.delete_col(col_head_node)

    def print_progress(self, message, interval, force=False):
        new_time = time()
        if (new_time - self.prevtime) >= interval or force:
            print(f"Elapsed time: {timedelta(seconds=new_time - self.starttime)} / {message}")
            self.prevtime = new_time

    def check_solution_uniqueness(self, sol):
        sol = self.reduce_solution(sol)

        for sola in [sol, self.reflect(sol)]:
            if sola in self.reduced_solutions:
                return
            for _ in range(3):
                sola = self.rotatez(sola)
                if sola in self.reduced_solutions:
                    return
            sola = self.rotatez(sola)

            for _ in range(3):
                sola = self.rotatex(sola)
                if sola in self.reduced_solutions:
                    return
                for _ in range(3):
                    sola = self.rotatez(sola)
                    if sola in self.reduced_solutions:
                        return
                sola = self.rotatez(sola)
            sola = self.rotatex(sola)

            sola = self.rotatez(sola)
            sola = self.rotatex(sola)
            if sola in self.reduced_solutions:
                return
            for _ in range(3):
                sola = self.rotatez(sola)
                if sola in self.reduced_solutions:
                    return
            sola = self.rotatez(sola)

            sola = self.rotatex(sola)
            sola = self.rotatex(sola)
            if sola in self.reduced_solutions:
                return
            for _ in range(3):
                sola = self.rotatez(sola)
                if sola in self.reduced_solutions:
                    return
        return 1

    def dlx_alg(self, llist, volume, stop=False):
        self.print_progress(f"{self.tried_variants_num} variants have been tried, {len(self.solutions)} solution{'' if len(self.solutions) == 1 else 's'} found", 5.0)
        # If no rows left - all pieces are used
        if llist.head.down is llist.head:
            self.tried_variants_num += 1
            # If no columns left - all cells are filled, the solution is found.
            if llist.head.right is llist.head:
                solution = tuple(tuple(tuple(row) for row in plane) for plane in volume)
                if self.check_solution_uniqueness(solution):
                    self.solutions.add(solution)
                    self.reduced_solutions.add(self.reduce_solution(solution))
                return True
        # Search a column with a minimum of intersected rows
        min_col, min_col_sum = self.find_min_col(llist, llist.head)
        # The performance optimization - stops branch analyzing if empty columns appears
        if min_col_sum == 0:
            self.tried_variants_num += 1
            return

        intersected_rows = []
        for node in llist.col_nonzero_nodes(min_col):
            intersected_rows.append(node.row_head)
        # Pick one row (the variant of piece) and try to solve puzzle with it
        for selected_row in intersected_rows:
            rows_to_restore = []
            new_volume = self.add_posture_to_volume(selected_row, volume)
            # If some piece is used, any other variants (postures) of this piece
            # could be discarded in this branch
            for posture_num_node in llist.col_nonzero_nodes(llist.head):
                if posture_num_node.value == selected_row.value:
                    rows_to_restore.append(posture_num_node)
                    llist.delete_row(posture_num_node)

            cols_to_restore = []
            for col_node in llist.row_nonzero_nodes(selected_row):
                for row_node in llist.col_nonzero_nodes(col_node.col_head):
                    # Delete all rows which are using the same cell as the picked one,
                    # because only one piece can fill the specific cell
                    rows_to_restore.append(row_node.row_head)
                    llist.delete_row(row_node.row_head)
                # Delete the columns the picked piece fill, they are not
                # needed in this branch anymore
                cols_to_restore.append(col_node.col_head)
                llist.delete_col(col_node.col_head)
            # Pass the shrinked llist and the volume with the picked piece added
            # to the next processing
            found = self.dlx_alg(llist, new_volume, stop)
            if stop and found:
                return found

            for row in rows_to_restore:
                llist.insert_row(row)

            for col in cols_to_restore:
                llist.insert_col(col)

    def find_min_col(self, llist, min_col):
        min_col_sum = float("inf")
        for col in llist.row_nonzero_nodes(llist.head):
            tmp = sum(1 for item in llist.col_nonzero_nodes(col))
            if tmp < min_col_sum:
                min_col = col
                min_col_sum = tmp
        return min_col, min_col_sum

    def add_posture_to_volume(self, posture_plane, prev_steps_result):
        new_volume = prev_steps_result.copy()
        for node in self.llist.row_nonzero_nodes(posture_plane):
                plane, row, cell = self.num_to_coords(node.col_head.value - 1)
                new_volume[plane][row][cell] = node.row_head.value
        return new_volume

    def print_volume(self, volume, notation={}, colors={}, file=None):
        for y in range (len(volume[0])-1,-1,-1):
            for z in range(len(volume[0][0])-1,-1,-1):
                for x in range (len(volume)):
                    cell = volume[x][y][z]
                    if cell == "":
                        nc = colored ("*", "grey", "on_white") if colors != {} else "*"
                    else:
                        nc = notation[cell] if cell in notation else cell
                        if colors != {}:
                            if cell in colors:
                                nc = colored (nc, colors[cell][0], colors[cell][1])
                            else:
                                nc = colored (nc, "grey", "on_white")
                    print (nc, end="", file=file)
                print (" / ", end = "", file=file)
            print (file=file)
        print("#" * 80, file=file)

    def unique_piece_postures(self, named_pieces):
        postures = set(named_pieces)

        all_postures = set(postures)
        for name, posture in postures:
            for _ in range(3):
                posture = self.rotatez(posture)
                all_postures.add((name, posture))
            posture = self.rotatez(posture)

            for _ in range(3):
                posture = self.rotatex(posture)
                all_postures.add((name, posture))
                for _ in range(3):
                    posture = self.rotatez(posture)
                    all_postures.add((name, posture))
                posture = self.rotatez(posture)
            posture = self.rotatex(posture)

            posture = self.rotatez(posture)
            posture = self.rotatex(posture)
            all_postures.add((name, posture))
            for _ in range(3):
                posture = self.rotatez(posture)
                all_postures.add((name, posture))
            posture = self.rotatez(posture)

            posture = self.rotatex(posture)
            posture = self.rotatex(posture)
            all_postures.add((name, posture))
            for _ in range(3):
                posture = self.rotatez(posture)
                all_postures.add((name, posture))

        return all_postures
    # Generates entries for all possible positions of every piece's posture.
    # Then the items of these entries will be linked into the 2 dimensional circular linked list
    # The entry looks like:
    # piece's name  {volume cells filled by piece}  empty volume's cells
    #            |       | | | | |                       | | |
    #            5 0 0 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ................
    def generate_positions(self, postures, width, depth, height):
        def apply_posture(name, posture, x, y, z, wdth, dpth, hght):
            # Flattening of 2d list
            line = [cell for plane in self.start_volume for row in plane for cell in row]
            # Puts the piece onto the flattened start volume
            for r in range(hght):
                for f in range(dpth):
                    for c in range(wdth):
                        if posture[r][f][c]:
                            num = ((r + z) * depth + f + y) * width + x + c
                            if line[num]:
                                return
                            line[num] = posture[r][f][c]
            # And adds name into the beginning
            line.insert(0, name)
            return line
        # makes columns header in a llist
        yield [i for i in range(height * depth * width + 1)]

        for name, posture in postures:
            posture_height = len(posture)
            posture_depth = len(posture[0])
            posture_width = len(posture[0][0])
            for plane in range(height):
                if plane + posture_height > height:
                    break
                for row in range(depth):
                    if row + posture_depth > depth:
                        break
                    for cell in range(width):
                        if cell + posture_width > width:
                            break
                        new_line = apply_posture(name, posture, cell, row, plane, posture_width, posture_depth, posture_height)
                        if new_line:
                            yield new_line

    def reflect(self, fig):
        """
        Mirror, and replace each piece in fig with its canonical mirror piece
        """
        fig2 = tuple(tuple(tuple(cell if cell not in self.piece_mirrors else self.piece_mirrors[cell] \
                                 for cell in row) for row in plane) for plane in fig[::-1])
        return fig2

    def rotatez(self, fig):
        return tuple(zip(*fig[::-1]))

    def rotatex(self, fig):
        return tuple(tuple(zip(*fig[i][::-1])) for i in range(len(fig)))

# Some models to build

# In these patterns each entry is a set of rows, with vertically
# aligned rows forming a plane
# Number of entries is depth, entries in each entry is height,
# len of each string is width.
# x increases across len of string
# y decreases across pattern
# z decreases across row_set
# So what you see here is the top plane on the left, bottom plane
# on the right.

model_dict = {
    "cube3": """
*** / *** / ***
*** / *** / ***
*** / *** / ***
""",      # should be 240 soma solutions, 13 diabolical, 1 sg

    "piano": """
.***. / ***** / ***** / *****
..... / *...* / ***** / *...*
""",

    "giraffe": """
.... / .... / .... / .... / .... / .... / .*.*
.*.. / .*.. / .*.. / .*.. / .*.. / .*** / .***
**.. / .*.. / .*.. / .*.. / .*.. / .*** / .***
.... / .... / .... / .... / .... / .... / .*.*
""",  # I find no solutions

    "gorilla": """
..*.. / ..*..
*...* / *****
..... / *****
..... / *****
..... / .***.
..... / .***.
..... / .*.*.
""",  # only 1 solution

    "blockhouse": """
....... / ...*...
.*****. / .*****.
.*****. / .*****.
.*****. / *******
.*****. / .*****.
.*****. / .*****.
....... / ...*...
""",  # 2 sets

    "gorillas": """
..*......*.. / ..*......*..
*...*..*...* / *****..*****
............ / *****..*****
............ / *****..*****
............ / .***....***.
............ / .***....***.
............ / .*.*....*.*.
""",  # 2 sets, should be 3 solutions

    "cube4":  """
**** / **** / **** / ****
**** / **** / **** / ****
**** / **** / **** / ****
**** / **** / **** / ****
""",  # Bedlam Cube, should be  solutions

    "cube5": """
***** / ***** / ***** / ***** / *****
***** / ***** / ***** / ***** / *****
***** / ***** / ***** / ***** / *****
***** / ***** / ***** / ***** / *****
***** / ***** / ***** / ***** / *****
""",    # Conway, should be  solutions

    "r06x10": """
**********
**********
**********
**********
**********
**********
""" # Pentominoes, should be 2339 solutions

}

def models (name):

    if name in model_dict:
        return model_dict[name]
    else:
        return None

def string_to_coords (strng):
    """
Convert string to tuple of coordinates
"""
    nplanes = 0
    plane = 0
    nrows = 0
    ncells = 0
    for c in strng.strip()+"\n":
        if c == "\n":
            nrows += 1
            if plane >= nplanes and ncells > 0:
                nplanes = plane + 1
            plane = 0
        elif c == "/":
            plane += 1
        elif c == "*" or c == ".":
            ncells += 1

    cl = []
    plane = nplanes-1
    row = nrows-1
    cell = 0
    for c in strng.strip()+"\n":
        if c == "\n":
            plane = nplanes-1
            row -= 1
            cell = 0
        elif c == "/":
            plane -= 1
            cell = 0
        elif c == "*" or c == ".":
            if c == "*":
                cl.append((cell, row, plane))
            cell += 1

    return tuple(cl)

def readmodel (filename):
    m = []
    try:
        with open (filename, "r") as f:
            strng = "".join(f.readlines())
    except:
        print (f"Could not read {filename}")
        return None
    return string_to_coords(strng)

def parsemodel (modelname):
    mdl = models (modelname)
    if mdl == None:
        print (f"Unknown model {modelname}")
        return

    return string_to_coords (mdl)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument (
        'model_file',
        type=str,
        nargs="?",
        help="File with model to be solved")

    parser.add_argument (
        "-o", '--output_file',
        type=str,
        help="File for solutions output (.txt or .json)")

    parser.add_argument (
        '-p', '--puzzle',
        type=str,
        nargs="?",
        default = "soma",
        help="Puzzle to be used, default = 'soma'; list puzzles if no argument")

    parser.add_argument (
        '-m', '--model',
        type=str,
        nargs="?",
        default="_def",
        help="Builtin model to be solved, default depends on puzzle, list models if no argument")

    parser.add_argument (
        '-n', '--notation',
        type=str,
        help="For soma/double_soma: Use notation 'num' (numeric), 'somap' (SA SOMAP), or 'ww' (Winning Ways, default); for pentominoes: 'gol' (Golomb, default) or 'con' (Conway)")

    parser.add_argument (
        '-c', '--colors',
        action = "store_true",
        help = "Colorize model printouts when possible"
        )

    parser.add_argument (
        '-s', '--stop',
        action = "store_true",
        help = "Stop after first solution found"
        )

    parser.add_argument (
        '-q', '--quiet',
        action = "store_true",
        help = "Do not show solutions"
        )

    args = parser.parse_args()

    puzzle_dict = {
        "soma": soma_puzzle,
        "double_soma": double_soma_puzzle,
        "bedlam": bedlam_puzzle,
        "diabolical": diabolical_puzzle,
        "sg": sg_puzzle,
        "conway": conway_puzzle,
        "pentominoes": pentomino_puzzle,
    }

    puzzle_name = args.puzzle
    if puzzle_name == None:
        for p in puzzle_dict:
            print (f"  {p:15} {puzzle_dict[p].desc} ({puzzle_dict[p].ncubes} cubes, default model {puzzle_dict[p].defmodel})")
        return
    elif puzzle_name not in puzzle_dict:
        print (f"Unknown puzzle {puzzle_name}")
        return
    puzzle = puzzle_dict[puzzle_name]

    # Convert pattern to cartesian coordinates

    coords = []
    if args.model_file:
        coords = readmodel (args.model_file)
        if coords == None:
            return
    elif args.model == None:
        for m in model_dict:
            print (f"  {m}")
        return
    elif args.model == "_def":
        coords = parsemodel (puzzle.defmodel)
    else:
        coords = parsemodel (args.model)

    expnum = puzzle.ncubes
    fewmany = 'many' if len(coords) > expnum else 'few' if len(coords) < expnum else ""
    if fewmany != "":
        print (f"*** {args.model if args.model!='_def' else 'Model'} has too {fewmany} cubes for {puzzle_name}: {len(coords)}")
        if fewmany == "many":
            return

    notation = {}
    colors = {}
    if puzzle_name == "soma" or puzzle_name == "double_soma":
        notation_name = "ww" if args.notation == None else args.notation
        notation = {}
        if args.colors:
            colors = {"W": ["white", "on_grey"], "Y": ["yellow", "on_white"], "G": ["green", "on_white"],
                      "O": ["yellow", "on_grey"], "L": ["blue", "on_white"], "R": ["red", "on_white"],
                      "B": ["grey", "on_white"],
                      "w": ["white", "on_grey"], "y": ["yellow", "on_white"], "g": ["green", "on_white"],
                      "o": ["yellow", "on_grey"], "l": ["blue", "on_white"], "r": ["red", "on_white"],
                      "b": ["grey", "on_white"],
                      }
        if notation_name == 'num':
            notation = {"W": "1", "Y": "2", "G": "3", "O": "4", "L": "5", "R": "6", "B": "7",
                        "w": "1", "y": "2", "g": "3", "o": "4", "l": "5", "r": "6", "b": "7"}
        elif notation_name == 'somap':
            notation = {"W": "B", "L": "U", "B": "A",
                        "w": "b", "l": "u", "b": "a"}
            if args.colors:
                colors = {"W": ["magenta", "on_grey"], "Y": ["yellow", "on_white"], "G": ["green", "on_white"],
                          "O": ["yellow", "on_grey"], "L": ["blue", "on_white"], "R": ["red", "on_white"],
                          "B": ["grey", "on_white"],
                          "w": ["magenta", "on_grey"], "y": ["yellow", "on_white"], "g": ["green", "on_white"],
                          "o": ["yellow", "on_white"], "l": ["blue", "on_white"], "r": ["red", "on_white"],
                          "b": ["grey", "on_white"],
                          }
        elif notation_name == "ww":
            pass
        else:
            print (f"*** Unrecognized notation '{notation_name}' ignored")
    elif puzzle_name == "pentominoes":
        notation_name = "gol" if args.notation == None else args.notation
        if notation_name == 'con':
            notation = {"F": "R", "I": "O", "L": "Q", "N": "S"}
        elif notation_name == "gol":
            notation = {}
        else:
            print (f"*** Unrecognized notation '{notation_name}' ignored")

    # Get dimensions of volume
    d = [0, 0, 0]
    for c in coords:
        for i in range(3):
            if c[i] >= d[i]:
                d[i] = c[i] + 1

    # Build volume with dead cells marked
    volume = [[["."] * d[2] for _ in range(d[1])] for _ in range (d[0])]
    for c in coords:
        volume[c[0]][c[1]][c[2]] = ""

    solver = Solver(volume=volume, puzzle=puzzle)

    solver.print_volume(solver.start_volume)
    try:
        solver.find_solutions(stop=args.stop)
    except:
        print ("*** Terminated")

    n = len(solver.solutions)
    solver.print_progress(f"{solver.tried_variants_num} variants have been tried, {n} solution{'' if n == 1 else 's'} found", 5.0, force=True)

    ofn = args.output_file
    ojson = False if not ofn else ofn[-5:] == ".json"
    otxt = False if not ofn else ofn[-4:] == ".txt"

    if ofn:
        try:
            of = open (ofn, "w")
        except:
            print (f"*** Cannot open output file {ofn}")
    if (not args.quiet) or ofn:
        i = 0
        sarr = []
        for s in solver.solutions:
            i += 1
            if not args.quiet:
                print(f"Solution № {i}")
                solver.print_volume(s, notation, colors)
            if otxt:
                print(f"Solution № {i}", file=of)
                solver.print_volume(s, notation, colors, file=of)
            elif ojson:
                sarr.append (s)
    if ojson:
        json.dump(sarr, of)
    if ofn:
        of.close()
        
if __name__ == "__main__":
    main()
