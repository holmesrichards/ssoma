#!/usr/bin/python3

"""
Soma Cube (and other polycube dissections) solver by Rich Holmes
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
import re

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

puzzle_dict = {}

class Solver():
    named_pieces = set()
    all_piece_postures = set()
    piece_copies = {}
    piece_mirrors = {}

    def __init__(self, volume=None, height=None, depth=None, width=None, puzzle=None):
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
                    if p1[0] not in spc:
                        spc[p1[0]] = [p2[0]]
                    elif p2[0] not in spc[p1[0]]:
                        spc[p1[0]].append(p2[0])
        sk = list(spc.keys())
        for k in sk:
            if len(spc[k]) == 1:
                del spc[k]
            else:
                spc[k].sort()

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
        Replace each piece in sol with an identical piece in canonical order
        """
        dct = {}
        s = [[['.' for cell in row] for row in plane] for plane in sol]
        for ip in range(len(sol)):
            for ir in range(len(sol[0])):
                for ic in range(len(sol[0][0])):
                    cell = sol[ip][ir][ic]
                    if cell not in self.piece_copies:
                        s[ip][ir][ic] = cell
                    else:
                        if cell not in dct:
                            for d in self.piece_copies[cell]:
                                if d not in dct.values():
                                    dct[cell] = d
                                    break
                        s[ip][ir][ic] = dct[cell]
        sol2 = tuple(tuple(tuple(cell for cell in row) for row in plane) for plane in s)
        return sol2

    def find_solutions(self, stop=None):
        self.llist = Linked_list_2D(self.height * self.depth * self.width + 1)
    
        pos_gen = self.generate_positions(self.all_piece_postures, self.width, self.depth, self.height)
        for line in pos_gen:
            for val in line:
                self.llist.append(val)

        self.delete_filled_on_start_cells(self.llist)

        self.starttime = time()
        self.prevtime = self.starttime
        self.dlx_alg(self.llist, self.start_volume, stop)

    cube_type = \
    [
        [
            [0, 1, 0],
            [1, 2, 1],
            [0, 1, 0]
        ],
        [
            [1, 2, 1],
            [2, 3, 2],
            [1, 2, 1]
        ],
        [
            [0, 1, 0],
            [1, 2, 1],
            [0, 1, 0]
        ]
    ]

    def cube_counting_poss(self):
        # If this is 3x3x3 then count cube possibilities
        if self.width != 3 or self.depth != 3 or self.height != 3:
            return
        pos_gen = self.generate_positions(self.all_piece_postures, self.width, self.depth, self.height)
        vefcs = {}
        for g in pos_gen:
            if g[0] == 0:
                continue
            vefc = [0, 0, 0, 0]
            for row in range(3):
                for plane in range(3):
                    for cell in range(3):
                        gcrp = g[1+cell+self.width*(row+self.depth*plane)]
                        vefc[self.cube_type[plane][row][cell]] += gcrp
            if g[0] in vefcs:
                if vefc not in vefcs[g[0]]:
                    vefcs[g[0]].append(vefc)
            else:
                vefcs[g[0]] = [vefc]

        pick = [0 for _ in range(len(vefcs.keys()))]
        vefca = [vefcs[k] for k in sorted(vefcs.keys())]
        labels = sorted(vefcs.keys())

        possibles = []
        while True:
            j = len(vefca)-1
            while pick[j] == len(vefca[j])-1:
                pick[j] = 0
                j -= 1
                if j < 0:
                    break
            if j < 0:
                break
            pick[j] += 1
            sum = [0, 0, 0, 0]
            for j in range(len(vefca)):
                for i in range(len(sum)):
                    sum[i] += vefca[j][pick[j]][i]
            if sum == [8, 12, 6, 1]:
                possibles.append([vefca[j][pick[j]] for j in range(len(vefca))])

        return [vefca, labels, possibles]
        
    def cube_counting_act(self, sol):
        # If this is 3x3x3 then count cube actualities
        if self.width != 3 or self.depth != 3 or self.height != 3:
            return
        vefcs = {}
        for plane in range(3):
            for row in range(3):
                for cell in range(3):
                    k = sol[plane][row][cell]
                    if k not in vefcs:
                        vefcs[k] = [0, 0, 0, 0]
                    vefcs[k][self.cube_type[cell][row][plane]] += 1
        return vefcs
        
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
        for sola in [sol, self.reflect(sol)]:
            if self.reduce_solution(sola) in self.reduced_solutions:
                return
            for _ in range(3):
                sola = self.rotatez(sola)
                if self.reduce_solution(sola) in self.reduced_solutions:
                    return
            sola = self.rotatez(sola)

            for _ in range(3):
                sola = self.rotatex(sola)
                if self.reduce_solution(sola) in self.reduced_solutions:
                    return
                for _ in range(3):
                    sola = self.rotatez(sola)
                    if self.reduce_solution(sola) in self.reduced_solutions:
                        return
                sola = self.rotatez(sola)
            sola = self.rotatex(sola)

            sola = self.rotatez(sola)
            sola = self.rotatex(sola)
            if self.reduce_solution(sola) in self.reduced_solutions:
                return
            for _ in range(3):
                sola = self.rotatez(sola)
                if self.reduce_solution(sola) in self.reduced_solutions:
                    return
            sola = self.rotatez(sola)

            sola = self.rotatex(sola)
            sola = self.rotatex(sola)
            if self.reduce_solution(sola) in self.reduced_solutions:
                return
            for _ in range(3):
                sola = self.rotatez(sola)
                if self.reduce_solution(sola) in self.reduced_solutions:
                    return
        return 1

    def dlx_alg(self, llist, volume, stop=None):
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
            self.dlx_alg(llist, new_volume, stop)
            if stop != None and len(self.solutions) >= stop:
                return

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
        print(file=file)

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
            line = [0 if cell=='' else 1 for plane in self.start_volume for row in plane for cell in row]
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

def string_convert (strng, to_bits=False):
    """
Convert string to tuple of coordinates or of 1/0
"""
    nplanes = 0
    plane = 0
    nrows = 0
    ncells = 0
    cell = 0
    empty_row  = True
    empty_planes = 0
    for c in strng.strip()+"\n":
        if c == "\n":
            nrows += 1
            if empty_row:
                empty_planes += 1
            elif cell > ncells:
                ncells = cell
            if plane-empty_planes >= nplanes:
                nplanes = plane - empty_planes + 1
            plane = 0
            empty_row = True
            cell = 0
        elif c == "/":
            plane += 1
            if empty_row:
                empty_planes += 1
            elif cell > ncells:
                ncells = cell
            empty_row = True
            cell = 0
        elif c == "*" or c == ".":
            cell += 1
            if c == "*":
                empty_row = False
                empty_planes = 0
                
    cl = [[[0 for _ in range(ncells)] for _ in range(nrows)] for _ in range(nplanes)] if to_bits else []
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
        elif c == "*":
            if to_bits:
                cl[nplanes-1-plane][nrows-1-row][cell] = 1
            else:
                cl.append((cell, row, plane))
            cell += 1
        elif c == ".":
            cell += 1

    if to_bits:
        return tuple(tuple(tuple(cl[p][r][c] for c in range(ncells)) for r in range(nrows)) for p in range(nplanes))
    else:
        return tuple(cl)

def readpuzzles (filename):
    try:
        f = open (filename, "r")
    except:
        print (f"*** Could not read {filename}")
        return None

    puzzlename = ""
    desc = ""
    defmodel = ""
    piecename = ""
    strng = ""
    pieces = {}
    pdict = {}
    for l in f:
        ls = l.strip()
        if ls == "-":   # end of puzzle
            if strng != "":
                pieces[piecename] = string_convert(strng, True)
            pdict[puzzlename] = Puzzle(desc, defmodel, pieces)
            puzzlename = ""
            desc = ""
            defmodel = ""
            piecename = ""
            strng = ""
            pieces = {}
        elif ls == "":  # end of piece if strng not empty
            if strng == "":
                continue
            pieces[piecename] = string_convert(strng, True)
            piecename = ""
            strng = ""
        elif puzzlename == "":
            puzzlename = ls
        elif desc == "":
            desc = ls
        elif defmodel == "":
            defmodel = ls
        elif piecename == "":
            piecename = ls
        else:
            strng += l

    if strng != "":
        pieces[piecename] = string_convert(strng, True)
    if puzzlename != "":
        pdict[puzzlename] = Puzzle(desc, defmodel, pieces)

    return pdict
        
def readmodels (filename):
    try:
        f = open (filename, "r")
    except:
        print (f"Could not read {filename}")
        yield None

    modelname = ""
    strng = ""
    for l in f:
        ls = l.strip()
        if ls == "":
            if strng == "":
                continue
            yield [modelname, string_convert(strng)]
            modelname = ""
            strng = ""
        elif modelname == "":
            if re.search("^[ ./*]*$", ls):
                modelname = "..."
                strng = l
            else:
                modelname = ls
        else:
            strng += l
            
    if strng != "":
        yield [modelname, string_convert(strng)]

def solvepuzzle (modelname, coords, puzzle_name, notation, colors, stopp, output_file, output_format, quiet):
    puzzle = puzzle_dict[puzzle_name]
    expnum = puzzle.ncubes
    fewmany = 'many' if len(coords) > expnum else 'few' if len(coords) < expnum else ""
    if fewmany != "":
        print (f"*** {modelname} has too {fewmany} cubes for {puzzle_name}: {len(coords)}")
        if fewmany == "many" or len(coords) == 0:
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

    solver = Solver(volume=volume, puzzle=puzzle)
            
    if (not quiet) or output_file:
        if output_format == "txt":
            print (f"{modelname}", file=output_file)    
            solver.print_volume(solver.start_volume, file=output_file)

    try:
        solver.find_solutions(stop=stopp)
    except KeyboardInterrupt:
        print ("*** Terminated")

    n = len(solver.solutions)
    solver.print_progress(f"{puzzle_name} / {modelname} / {solver.tried_variants_num} variants have been tried, {n} solution{'' if n == 1 else 's'} found", 5.0, force=True)

    if (not quiet) or output_file:
        i = 0
        sarr = []
        for s in solver.solutions:
            i += 1
            vefcs = solver.cube_counting_act(s) if modelname == "Cube3" else None
            if not quiet:
                print(f"Solution № {i}")
                if vefcs:
                    for k in sorted(vefcs.keys()):
                        print (f"{k}: {vefcs[k]}", end=" ")
                    print ()
                solver.print_volume(s, notation, colors)
            if output_file != None:
                if output_format == "txt":
                    print(f"Solution № {i}", file=output_file)
                    if vefcs:
                        for k in sorted(vefcs.keys()):
                            print (f"{k}: {vefcs[k]}", end=" ", file=output_file)
                        print (file=output_file)
                    solver.print_volume(s, notation, colors, file=output_file)
                elif output_format == "json":
                    sarr.append (s)
        if i == 0 and output_format == "txt":
            print ("*** No solutions", file=output_file)
        if output_format != "json":
            print("#" * 80, file=output_file)
    if output_format == "json":
        nsarr = [modelname, coords, puzzle_name, sarr]
        json.dump(nsarr, output_file)
        print (file=output_file)


def main():
    global puzzle_dict
    
    parser = argparse.ArgumentParser()

    parser.add_argument (
        '-i', '--input_file',
        type=str,
        default="models.txt",
        help="File with model(s) to be solved")

    parser.add_argument (
        '-pi', '--puzzle_input_file',
        type=str,
        default="puzzles.txt",
        help="File with puzzles")

    parser.add_argument (
        "-o", '--output_file',
        type=str,
        help="File for solutions output (.txt or .json)")

    parser.add_argument (
        '-p', '--puzzle',
        type=str,
        nargs="?",
        default = "_def",
        help="Puzzle to be used; list puzzles if no argument")

    parser.add_argument (
        '-m', '--model',
        type=str,
        nargs="?",
        default="_def",
        help="Model to be solved, default depends on puzzle, list models if no argument")

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
        type = int,
        help = "Stop after n solutions found"
        )

    parser.add_argument (
        '-q', '--quiet',
        action = "store_true",
        help = "Do not show solutions"
        )

    parser.add_argument (
        '-cc', '--cube_counting',
        action = "store_true",
        help = "Do cube counting for 3x3x3 cube and exit"
        )
    
    args = parser.parse_args()

    # Get puzzle definition from text file

    puzzle_dict = readpuzzles(args.puzzle_input_file if args.puzzle_input_file else "puzzles.txt")
    if not puzzle_dict:
        return
           
    if args.puzzle == None:
        for p in puzzle_dict:
            print (f"  {p:15} {puzzle_dict[p].desc} ({puzzle_dict[p].ncubes} cubes, default model {puzzle_dict[p].defmodel})")
        return
    elif args.puzzle == "_def":
        puzzle_name = "soma" if "soma" in puzzle_dict else list(puzzle_dict.keys())[0]
    elif args.puzzle in puzzle_dict:
        puzzle_name = args.puzzle
    else:
        print (f"Unknown puzzle {args.puzzle}")
        return
    puzzle = puzzle_dict[puzzle_name]
    
    try:
        nf = open("notation.json", "r")
    except:
        print ("*** Cannot read notations.json file")
        nf = None

    # Get notation and colors from json file
    
    notation_json = json.load(nf) if nf else None
        
    notation = {}
    colors = {}
    anot = args.notation
    
    if notation_json and puzzle_name in notation_json:
        pn = notation_json[puzzle_name]
        if anot:
            if anot in pn:
                notation_name = anot
            else:
                print (f"*** Unrecognized notation '{anot}' for puzzle '{puzzle_name}' ignored")
                notation_name = None
        else:
            notation_name = pn["default"] if "default" in pn else None
        if notation_name:
            notation = pn[notation_name]["notation"] if "notation" in pn[notation_name] else {}
            colors = pn[notation_name]["colors"] if args.colors and "colors" in pn[notation_name] else {}

    # Get model from text file, convert to cartesian coordinates and solve

    coords = []

    if args.model == None:  # -m with no argument, list models
        for [m, coords] in readmodels (args.input_file):
            print (f"  {m}")
        return

    ofn = args.output_file
    ofform = "json" if ofn and ofn[-5:] == ".json" \
        else ("txt" if not ofn or ofn[-4:] == ".txt" \
              else "")
    if ofn and ofform == "":
        print (f"** Unrecognized output file type {ofn}")
        return
    
    of = None
    if ofn:
        try:
            of = open (ofn, "w")
        except:
            print (f"*** Cannot open output file {ofn}")

    if args.cube_counting:
        puzzle = puzzle_dict[puzzle_name]
        if puzzle.ncubes != 27:
            print ("*** Not a 27 cube puzzle")
            return

        solver = Solver(height=3, depth=3, width=3, puzzle=puzzle)
        [vefca, labels, possibles] = solver.cube_counting_poss()
        if ofform == "txt":
            print ("*** Piece positions:", file=of)
            for j in range (len(vefca)):
                print (f"{labels[j]}: {', '.join([str(v) for v in vefca[j]])}", file=of)
            print ("\n*** Position combinations:", file=of)
            for j in range (len(vefca)):
                print (f"For {labels[j]} central:", file=of)
                n = 0
                for p in possibles:
                    if p[j][3] == 1:
                        n += 1
                        print ("   ", end="")
                        for jj in range (len(vefca)):
                            print (f"{labels[jj]}: {p[jj]}", end=" ", file=of)
                        print(file=of)
                if n == 0:
                    print ("   Not possible", file=of)
        elif ofform == "json":
            json.dump(labels, of)
            json.dump(vefca, of)
            json.dump(possibles, of)
            
        return
    
    found = False
    targetmodel = puzzle_dict[puzzle_name].defmodel if args.model == '_def' else args.model
    for [modelname, coords] in readmodels (args.input_file):
        if coords == None:
            return
        if targetmodel == '*' or targetmodel == modelname:
            solvepuzzle (modelname, coords, puzzle_name, notation, colors, args.stop, of, ofform, args.quiet)
            found = True
    if not found:
        if args.model == None:
            print ("*** No model found in {args.input_file}")
        else:
            print (f"*** '{targetmodel}' not found in {args.input_file}")

    if ofn:
        of.close()

        
if __name__ == "__main__":
    main()
    
