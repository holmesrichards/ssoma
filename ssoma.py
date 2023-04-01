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

class Solver():
    SOMA_PIECES = {
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

    # For 2-set models

    DOUBLE_SOMA_PIECES = {
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

    BEDLAM_PIECES = {
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

    DIABOLICAL_PIECES = {
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

    SG_PIECES = {
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

    named_pieces = set()
    all_piece_postures = set()
    piece_copies = {}
    piece_mirrors = {}
    
    def __init__(self, volume=None, height=None, depth=None, width=None, pieces=SOMA_PIECES):
        if volume is None:
            volume = [[[""] * width for _ in range(depth)] for _ in range (height)]
        if height is None and width is None:
            height = len(volume)
            depth = len(volume[0])
            width = len(volume[0][0])
        self.height = height
        self.depth = depth
        self.width = width
        self.named_pieces = set(zip(pieces.keys(), pieces.values()))
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
    
    def find_solutions(self):
        self.llist = Linked_list_2D(self.height * self.depth * self.width + 1)
        pos_gen = self.generate_positions(self.all_piece_postures, self.width, self.depth, self.height)

        for line in pos_gen:
            for val in line:
                self.llist.append(val)
        
        self.delete_filled_on_start_cells(self.llist)

        self.starttime = time()
        self.prevtime = self.starttime
        self.dlx_alg(self.llist, self.start_volume)

        return len(self.solutions)
    
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

    def print_progress(self, message, interval):
        new_time = time()
        if (new_time - self.prevtime) >= interval:
            print(message)
            print(f"Time has elapsed: {timedelta(seconds=new_time - self.starttime)}")
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

    def dlx_alg(self, llist, volume):
        # If no rows left - all pieces are used
        if llist.head.down is llist.head:
            self.print_progress(f"{self.tried_variants_num} variants have been tried", 5.0)
            self.tried_variants_num += 1
            # If no columns left - all cells are filled, the solution is found.
            if llist.head.right is llist.head:
                solution = tuple(tuple(tuple(row) for row in plane) for plane in volume)
                if self.check_solution_uniqueness(solution):
                    print(f"Solution № {len(self.solutions) + 1}")
                    self.print_volume(solution)
                    self.solutions.add(solution)
                    self.reduced_solutions.add(self.reduce_solution(solution))
                return
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
            self.dlx_alg(llist, new_volume)

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

    def print_volume(self, volume):
        for y in range (len(volume[0])-1,-1,-1):
            for z in range(len(volume[0][0])-1,-1,-1):
                for x in range (len(volume)):
                    cell = volume[x][y][z]
                    print ("*" if cell == "" else cell, end="")
                print (" / ", end = "")
            print ()
        print("#" * 80) 

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
    "cube3":
    (
        ("***", "***", "***"),
        ("***", "***", "***"),
        ("***", "***", "***")
    ),  # should be 240 soma solutions, 13 diabolical, 1 sg

    "piano":
    (
        (".***.", "*****", "*****", "*****"),
        (".....", "*...*", "*****", "*...*")
    ),

    "giraffe":
    (
        ("....", "....", "....", "....", "....", "....", ".*.*"),
        (".*..", ".*..", ".*..", ".*..", ".*..", ".***", ".***"),
        ("**..", ".*..", ".*..", ".*..", ".*..", ".***", ".***"),
        ("....", "....", "....", "....", "....", "....", ".*.*")
    ),  # I find no solutions

    "grand_piano":
    (
        ("..***.", "..****"),
        (".****.", ".*****"),
        ("*****.", "******")
    ),

    "teddy_bear":
    (
        ("**.", "**.", "***", "**.", "**.", "***"),
        ("*..", "**.", "**.", "**.", "**.", "**."),
        ("...", "...", "*..", "...", "...", "*..")
    ),

    "gorilla":
    (
        ("..*..", "..*.."),
        ("*...*", "*****"),
        (".....", "*****"),
        (".....", "*****"),
        (".....", ".***."),
        (".....", ".***."),
        (".....", ".*.*.")
    ),  # only 1 solution    

    "blockhouse":  # 2 sets
    (
        (".......", "...*..."),
        (".*****.", ".*****."),
        (".*****.", ".*****."),
        (".*****.", "*******"),
        (".*****.", ".*****."),
        (".*****.", ".*****."),
        (".......", "...*..."),
    ),

    "gorillas":  # 2 sets
    (
        ("..*......*..", "..*......*.."),
        ("*...*..*...*", "*****..*****"),
        ("............", "*****..*****"),
        ("............", "*****..*****"),
        ("............", ".***....***."),
        ("............", ".***....***."),
        ("............", ".*.*....*.*.")  # should be 3 solutions
    ),  # only 1 solution    

    "cube4":  # Bedlam Cube
    (
        ("****", "****", "****", "****"),
        ("****", "****", "****", "****"),
        ("****", "****", "****", "****"),
        ("****", "****", "****", "****")
    )  # should be  solutions
}

def models (name):

    if name in model_dict:
        return model_dict[name]
    else:
        return None
    
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument (
        'model',
        type=str,
        nargs = "?",
        default = "cube3",
        help="Model to be solved, default = 'cube3'")

    parser.add_argument (
        '-p', '--puzzle',
        type=str,
        nargs="?",
        default = "soma",
        help="Puzzle to be used, default = 'soma'; list puzzles if no argument")

    parser.add_argument (
        '-m', '--models',
        action="store_true",
        help="List builtin models")

    args = parser.parse_args()

    if args.models:
        for m in model_dict:
            print (f"  {m}")
        return

    puzzle_dict = {
        "soma": [27, None, "Soma Cube (by Piet Hein)"],
        "double_soma": [54, Solver.DOUBLE_SOMA_PIECES, "2 sets Soma Cube"],
        "bedlam": [64, Solver.BEDLAM_PIECES, "Bedlam Cube (by Bruce Bedlam)"],
        "diabolical": [27, Solver.DIABOLICAL_PIECES, "Diabolical Cube (pub. by Angelo Lewis)"],
        "sg": [27, Solver.SG_PIECES, "Slothouber-Graatsma puzzle (by Jan Slothouber and William Graatsma)"],
    }
    
    start = models (args.model)
    if start == None:
        print (f"Unknown model {args.model}")
        return
    
    puzzle = args.puzzle
    if puzzle == None:
        for p in puzzle_dict:
            print (f"  {p:15} {puzzle_dict[p][2]}")
        return
    elif puzzle not in puzzle_dict:
        print (f"Unknown puzzle {puzzle}")
        return
    else:
        puz_stuf = puzzle_dict[puzzle]
    
    # Convert pattern to cartesian coordinates
    coords = []
    for y in range(len(start)):
        row_set = start[y]
        for z in range(len(row_set)):
            row = row_set[z]
            for x in range(len(row)):
                if start[y][z][x] == "*":
                    coords.append((x, len(start)-y-1, len(row_set)-z-1))
    coords = tuple(coords)

    expnum = puz_stuf[0]    
    fewmany = 'many' if len(coords) > expnum else 'few' if len(coords) < expnum else ""
    if fewmany != "":
        print (f"{args.model} has too {fewmany} cubes for {puzzle}: {len(coords)}")
        return

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

    if puz_stuf[1] == None:
        solver = Solver(volume=volume)
    else:
        solver = Solver(volume=volume, pieces=puz_stuf[1])
    
    solver.print_volume(solver.start_volume)
    n = solver.find_solutions()
    if n == 0:
        print ("*** No solutions")

if __name__ == "__main__":
    main()
