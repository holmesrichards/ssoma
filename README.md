# ssoma.py

A Python script to solve Soma Cube puzzles.

Based on a Pentominoes solver by "MiniMax" ([https://codereview.stackexchange.com/questions/233300/solving-pentomino-puzzles-by-using-knuths-algorithm-x
](https://codereview.stackexchange.com/questions/233300/solving-pentomino-puzzles-by-using-knuths-algorithm-x)).

Very hacky (my parts, at least) but it works. Can do 2-set puzzles though they take a lot longer. Shows only solutions that are not the same under rotation or reflection (with pieces 5 and 6 interchanged).

On my computer it finds all 240 cube solutions in under 5 seconds. Then it spends another 35 seconds looking for other solutions.

Edit the script to specify a new figure to solve.

Solutions are shown as layers from top to bottom, with pieces denoted by the color code used in Berlecamp, Conway, and Guy's *Winning Ways*:

* 1 = W = White
* 2 = Y = Yellow
* 3 = G = Green
* 4 = O = Orange
* 5 = L = bLue
* 6 = R = Red
* 7 = B = Black

You can change the labels to the standard numbers 1–7 easily enough (but I have a multi color cube using the above scheme and it makes it easier to note or check solutions that way. For 2-set figures lowercase letters are used for the second set.)


