# ssoma.py

A Python script to solve Soma Cube puzzles and other cube-based dissection puzzles.

Based on a Pentominoes solver by "MiniMax" ([https://codereview.stackexchange.com/questions/233300/solving-pentomino-puzzles-by-using-knuths-algorithm-x
](https://codereview.stackexchange.com/questions/233300/solving-pentomino-puzzles-by-using-knuths-algorithm-x)).

Default behavior is to solve the cube model with the Soma puzzle pieces, but other models and puzzles can be specified.

Shows only solutions that are not the same under rotation or reflection (with mirror image pieces, e.g. Soma 5 and 6, interchanged).

On my computer it finds all 240 Soma Cube solutions in under 5 seconds. Then it spends another 35 seconds looking for other solutions.

## Usage

```
usage: ssoma.py [-h] [-i INPUT_FILE] [-o OUTPUT_FILE] [-p [PUZZLE]] [-m [MODEL]] [-n NOTATION] [-c] [-s] [-q]

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        File with model(s) to be solved
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        File for solutions output (.txt or .json)
  -p [PUZZLE], --puzzle [PUZZLE]
                        Puzzle to be used, default = 'soma'; list puzzles if no argument
  -m [MODEL], --model [MODEL]
                        Model to be solved, default depends on puzzle, list models if no argument
  -n NOTATION, --notation NOTATION
                        For soma/double_soma: Use notation 'num' (numeric), 'somap' (SA SOMAP), or 'ww' (Winning Ways, default); for pentominoes: 'gol' (Golomb, default) or 'con' (Conway)
  -c, --colors          Colorize model printouts when possible
  -s, --stop            Stop after first solution found
  -q, --quiet           Do not show solutions

```

### Puzzles

Puzzle can be specified with the `-p` argument; they are defined in the file `puzzles.txt`:
```
  soma            Soma Cube (by Piet Hein) (27 cubes)
  double_soma     2 sets Soma Cube (54 cubes)
  bedlam          Bedlam Cube (by Bruce Bedlam) (64 cubes)
  diabolical      Diabolical Cube (pub. by Angelo Lewis) (27 cubes)
  sg              Slothouber-Graatsma puzzle (by Jan Slothouber and William Graatsma) (27 cubes)
  conway          Conway puzzle (Blocks-In-a-Box) (by John Conway) (125 cubes)
  pentominoes     Solid Pentominoes (by Solomon Golomb) (60 cubes, default model r06x10)
  miku            J. G. Mikusinski's cube (27 cubes, default model cube3)
```
(`conway` is included mainly just to show how bad brute force is for it! I have not had the patience to run it long enough for it to find a solution.)

If `-p` is used with no puzzle name, available puzzles are listed.

### Models to solve

Model(s) to solve are read from the input file specified or the default `models.txt`.

* If the `-m` option is not given, the default model for the selected puzzle is solved.
* If the `-m` option is given with '*' for a model name, then all the models are solved.
* If the `-m` option is given with a model name, then the model with the given name is solved.
* If the `-m` option is given with no model name, the available model names are listed.

### Notations

Puzzle definitions have a default notation built in but alternate notations can be chosen with the `-n` argument. These, and corresponding color definitions, are specified in the `notation.json` file.

For Soma, notations are as follows:

| Numeric<br/>`-n num` | SOMAP (from Soma Addict)<br/>`-n somap` | Winning Ways (from Berlecamp, Conway, and Guy)<br/>`-n ww`  |
|----|----|----|
| 1  | B = Brown | W = White |
| 2  | Y = Yellow | Y = Yellow |
| 3  | G = Green | G = Green |
| 4  | O = Orange | O = Orange |
| 5  | U = blUe  | L = bLue |
| 6  | R = Red  | R = Red |
| 7  | A = blAck | B = Black |

For double set Soma puzzles, alphabetic notation is repeated with lowercase letters for the second set; numeric re-uses numbers. When `somap` or `ww` notations are used, the `-c` argument enables colorizing the outputs to mostly match the notation. (Brown and orange colors are unavailable on most terminals so the corresponding letters are arbitrarily assigned different colors.)

For Pentominoes, there are two notations:

|Golomb<br/>`-n gol`|Conway<br/>`-n con`|
|----|----|
|F|R|
|I|O|
|L|Q|
|N|S|
|P|P|
|T|T|
|U|U|
|V|V|
|W|W|
|X|X|
|Y|Y|
|Z|Z|

## Input

The model input file looks like this:
```
Model name

*.... / *.... / *.... 
*.... / *.... / *.... 
***.. / ***.. / ***..
..*.. / ..*.. / ..*..
..*** / ..*** / ..***

Model name 2

*** / *** / ***
*** / *** / ***
*** / *** / ***

...

```
Layers are shown top to bottom, terminated by slashes; "\*" denotes a cube, "." is a cubical void. Other characters are ignored.

## Output

(Uncolorized) Text format output looks like this:

```
Castle I

*...* / ***** / 
..... / ***** / 
..... / ***** / 
..... / ***** / 
*.... / ****. / 


Solution № 1
R...L / RGGGL / 
..... / RRGLL / 
..... / WWYYO / 
..... / BWYOO / 
B.... / BBYO. / 

Solution № 2
R...L / RGGGL / 
..... / RRGLL / 
..... / WWYYY / 
..... / BWYOO / 
B.... / BBOO. / 

...
```

First is shown the model. Layers are shown top to bottom, terminated by slashes; "\*" denotes a cube, "." is a cubical void.
At end of analysis all solutions are printed, unless the `-q` option is used (probably because you want to know if solutions exist or how many there are but not what they are).

Every 5 seconds and at end of analysis a status update line is shown on the terminal. 

You can terminate running with `CTRL-C` and partial results will be shown. The `-s` option will stop analysis and print partial results after the first solution is found.

