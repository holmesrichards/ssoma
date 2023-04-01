# ssoma.py

A Python script to solve Soma Cube puzzles and other cube-based dissection puzzles.

Based on a Pentominoes solver by "MiniMax" ([https://codereview.stackexchange.com/questions/233300/solving-pentomino-puzzles-by-using-knuths-algorithm-x
](https://codereview.stackexchange.com/questions/233300/solving-pentomino-puzzles-by-using-knuths-algorithm-x)).

Default behavior is to solve the cube puzzle with Soma pieces, but other models and puzzles can be specified.

Shows only solutions that are not the same under rotation or reflection (with mirror image pieces, e.g. Soma 5 and 6, interchanged).

On my computer it finds all 240 Soma Cube solutions in under 5 seconds. Then it spends another 35 seconds looking for other solutions.

## Usage

```
ssoma.py [-h] [-p [PUZZLE]] [-m [MODEL]] [-n NOTATION] [model_file]

positional arguments:
  model_file            File with model to be solved

options:
  -h, --help            show this help message and exit
  -p [PUZZLE], --puzzle [PUZZLE]
                        Puzzle to be used, default = 'soma'; list puzzles if no argument
  -m [MODEL], --model [MODEL]
                        Builtin model to be solved, default depends on puzzle, list models if no argument
  -n NOTATION, --notation NOTATION
                        (For soma/double_soma) Use notation 'num' (numeric), 'somap' (SA SOMAP), or 'ww' (Winning Ways, default)
```

Puzzles that can be specified with the `-p` argument are:
```
  soma            Soma Cube (by Piet Hein) (27 cubes)
  double_soma     2 sets Soma Cube (54 cubes)
  bedlam          Bedlam Cube (by Bruce Bedlam) (64 cubes)
  diabolical      Diabolical Cube (pub. by Angelo Lewis) (27 cubes)
  sg              Slothouber-Graatsma puzzle (by Jan Slothouber and William Graatsma) (27 cubes)
  conway          Conway puzzle (Blocks-In-a-Box) (by John Conway) (125 cubes)
```
(`conway` is included mainly just to show how bad brute force is for it! I have not had the patience to run it long enough for it to find a solution.)

The model to be solved is read from the specified file, or if no file is given, the builtin model specified with the `-m` argument is used. Builtin models that can be specified are:

(For Soma, Diabolical, or Slothouber-Graatsma:)
```
  cube3  [default]
```
(For Soma:)
```
  piano
  giraffe
  gorilla
```
(For double Soma:)
```
  blockhouse [default]
  gorillas
```
(For Bedlam:)
```
  cube4 [default]
```
(For Conway:)
```
  cube5 [default]
```

For Soma, notations that can be specified with the `-n` argument are as follows:

| Numeric | SOMAP (from Soma Addict) | Winning Ways (from Berlecamp, Conway, and Guy)  |
|----|----|----|
| 1  | B = Brown | W = White |
| 2  | Y = Yellow | Y = Yellow |
| 3  | G = Green | G = Green |
| 4  | O = Orange | O = Orange |
| 5  | U = blUe  | L = bLue |
| 6  | R = Red  | R = Red |
| 7  | A = blAck | B = Black |

For double set Soma puzzles, alphabetic notation is repeated with lowercase letters for the second set; numeric re-uses numbers.

## Input

The model can be specified in an input file, looking like this:
```
*.... / *.... / *.... 
*.... / *.... / *.... 
***.. / ***.. / ***..
..*.. / ..*.. / ..*..
..*** / ..*** / ..***
```
Layers are shown top to bottom, terminated by slashes; "\*" denotes a cube, "." is a cubical void. Other characters are ignored.

## Output

Output looks like this:

```
$ python3 ssoma.py -m gorilla
..*.. / ..*.. / 
*...* / ***** / 
..... / ***** / 
..... / ***** / 
..... / .***. / 
..... / .***. / 
..... / .*.*. / 
################################################################################
Elapsed time: 0:00:00.039574 / 77 variants have been tried, 1 solutions found
Solution № 1
..R.. / ..R.. / 
B...L / BBRRL / 
..... / BOOLL / 
..... / OOGGG / 
..... / .YYG. / 
..... / .YWW. / 
..... / .Y.W. / 
################################################################################
```

First is shown the model. Layers are shown top to bottom, terminated by slashes; "\*" denotes a cube, "." is a cubical void.
After this, every 5 seconds and at end of analysis a status update line is printed. At end of analysis all solutions are printed.
