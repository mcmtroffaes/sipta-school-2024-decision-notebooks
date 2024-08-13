import csv
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from math import prod
from statistics import mean

import pytest

TOL = 1e-6

csv_file = """5,67,3,5,3,1
4,43,1,1,?,1
5,58,4,5,3,1
4,28,1,1,3,0
5,74,1,5,?,1
4,65,1,?,3,0
4,70,?,?,3,0
5,42,1,?,3,0
5,57,1,5,3,1
5,60,?,5,1,1
5,76,1,4,3,1
3,42,2,1,3,1
4,64,1,?,3,0
4,36,3,1,2,0
4,60,2,1,2,0
4,54,1,1,3,0
3,52,3,4,3,0
4,59,2,1,3,1
4,54,1,1,3,1
4,40,1,?,?,0
?,66,?,?,1,1
5,56,4,3,1,1
4,43,1,?,?,0
5,42,4,4,3,1
4,59,2,4,3,1
5,75,4,5,3,1
2,66,1,1,?,0
5,63,3,?,3,0
5,45,4,5,3,1
5,55,4,4,3,0
4,46,1,5,2,0
5,54,4,4,3,1
5,57,4,4,3,1
4,39,1,1,2,0
4,81,1,1,3,0
4,77,3,?,?,0
4,60,2,1,3,0
5,67,3,4,2,1
4,48,4,5,?,1
4,55,3,4,2,0
4,59,2,1,?,0
4,78,1,1,1,0
4,50,1,1,3,0
4,61,2,1,?,0
5,62,3,5,2,1
5,44,2,4,?,1
5,64,4,5,3,1
4,23,1,1,?,0
2,42,?,?,4,0
5,67,4,5,3,1
4,74,2,1,2,0
5,80,3,5,3,1
4,23,1,1,?,0
4,63,2,1,?,0
4,53,?,5,3,1
4,43,3,4,?,0
4,49,2,1,1,0
5,51,2,4,?,0
4,45,2,1,?,0
5,59,2,?,?,1
5,52,4,3,3,1
5,60,4,3,3,1
4,57,2,5,3,0
3,57,2,1,?,0
5,74,4,4,3,1
4,25,2,1,?,0
4,49,1,1,3,0
5,72,4,3,?,1
4,45,2,1,3,0
4,64,2,1,3,0
4,73,2,1,2,0
5,68,4,3,3,1
5,52,4,5,3,0
5,66,4,4,3,1
5,70,?,4,?,1
4,25,1,1,3,0
5,74,1,1,2,1
4,64,1,1,3,0
5,60,4,3,2,1
5,67,2,4,1,0
4,67,4,5,3,0
5,44,4,4,2,1
3,68,1,1,3,1
4,57,?,4,1,0
5,51,4,?,?,1
4,33,1,?,?,0
5,58,4,4,3,1
5,36,1,?,?,0
4,63,1,1,?,0
5,62,1,5,3,1
4,73,3,4,3,1
4,80,4,4,3,1
4,67,1,1,?,0
5,59,2,1,3,1
5,60,1,?,3,0
5,54,4,4,3,1
4,40,1,1,?,0
4,47,2,1,?,0
5,62,4,4,3,0
4,33,2,1,3,0
5,59,2,?,?,0
4,65,2,?,?,0
4,58,4,4,?,0
4,29,2,?,?,0
4,58,1,1,?,0
4,54,1,1,?,0
4,44,1,1,?,1
3,34,2,1,?,0
4,57,1,1,3,0
5,33,4,4,?,1
4,45,4,4,3,0
5,71,4,4,3,1
5,59,4,4,2,0
4,56,2,1,?,0
4,40,3,4,?,0
4,56,1,1,3,0
4,45,2,1,?,0
4,57,2,1,2,0
5,55,3,4,3,1
5,84,4,5,3,0
5,51,4,4,3,1
4,43,1,1,?,0
4,24,2,1,2,0
4,66,1,1,3,0
5,33,4,4,3,0
4,59,4,3,2,0
4,76,2,3,?,0
4,40,1,1,?,0
4,52,?,4,?,0
5,40,4,5,3,1
5,67,4,4,3,1
5,75,4,3,3,1
5,86,4,4,3,0
4,60,2,?,?,0
5,66,4,4,3,1
5,46,4,5,3,1
4,59,4,4,3,1
5,65,4,4,3,1
4,53,1,1,3,0
5,67,3,5,3,1
5,80,4,5,3,1
4,55,2,1,3,0
4,48,1,1,?,0
4,47,1,1,2,0
4,50,2,1,?,0
5,62,4,5,3,1
5,63,4,4,3,1
4,63,4,?,3,1
4,71,4,4,3,1
4,41,1,1,3,0
5,57,4,4,4,1
5,71,4,4,4,1
4,66,1,1,3,0
4,47,2,4,2,0
3,34,4,4,3,0
4,59,3,4,3,0
5,55,2,?,?,1
4,51,?,?,3,0
4,62,2,1,?,0
4,58,4,?,3,1
5,67,4,4,3,1
4,41,2,1,3,0
4,23,3,1,3,0
4,53,?,4,3,0
4,42,2,1,3,0
5,87,4,5,3,1
4,68,1,1,3,1
4,64,1,1,3,0
5,54,3,5,3,1
5,86,4,5,3,1
4,21,2,1,3,0
4,39,1,1,?,0
4,53,4,4,3,0
4,44,4,4,3,0
4,54,1,1,3,0
5,63,4,5,3,1
4,62,2,1,?,0
4,45,2,1,2,0
5,71,4,5,3,0
5,49,4,4,3,1
4,49,4,4,3,0
5,66,4,4,4,0
4,19,1,1,3,0
4,35,1,1,2,0
4,71,3,3,?,1
5,74,4,5,3,1
5,37,4,4,3,1
4,67,1,?,3,0
5,81,3,4,3,1
5,59,4,4,3,1
4,34,1,1,3,0
5,79,4,3,3,1
5,60,3,1,3,0
4,41,1,1,3,1
4,50,1,1,3,0
5,85,4,4,3,1
4,46,1,1,3,0
5,66,4,4,3,1
4,73,3,1,2,0
4,55,1,1,3,0
4,49,2,1,3,0
3,49,4,4,3,0
4,51,4,5,3,1
2,48,4,4,3,0
4,58,4,5,3,0
5,72,4,5,3,1
4,46,2,3,3,0
4,43,4,3,3,1
?,52,4,4,3,0
4,66,2,1,?,0
4,46,1,1,1,0
4,69,3,1,3,0
2,59,1,1,?,1
5,43,2,1,3,1
5,76,4,5,3,1
4,46,1,1,3,0
4,59,2,4,3,0
4,57,1,1,3,0
5,43,4,5,?,0
3,45,2,1,3,0
3,43,2,1,3,0
4,45,2,1,3,0
5,57,4,5,3,1
5,79,4,4,3,1
5,54,2,1,3,1
4,40,3,4,3,0
5,63,4,4,3,1
2,55,1,?,1,0
4,52,2,1,3,0
4,38,1,1,3,0
3,72,4,3,3,0
5,80,4,3,3,1
5,76,4,3,3,1
4,62,3,1,3,0
5,64,4,5,3,1
5,42,4,5,3,0
3,60,?,3,1,0
4,64,4,5,3,0
4,63,4,4,3,1
4,24,2,1,2,0
5,72,4,4,3,1
4,63,2,1,3,0
4,46,1,1,3,0
3,33,1,1,3,0
5,76,4,4,3,1
4,36,2,3,3,0
4,40,2,1,3,0
5,58,1,5,3,1
4,43,2,1,3,0
3,42,1,1,3,0
4,32,1,1,3,0
5,57,4,4,2,1
4,37,1,1,3,0
4,70,4,4,3,1
5,56,4,2,3,1
3,76,?,3,2,0
5,73,4,4,3,1
5,77,4,5,3,1
5,67,4,4,1,1
5,71,4,3,3,1
5,65,4,4,3,1
4,43,1,1,3,0
4,40,2,1,?,0
4,49,2,1,3,0
5,76,4,2,3,1
4,55,4,4,3,0
5,72,4,5,3,1
3,53,4,3,3,0
5,75,4,4,3,1
5,61,4,5,3,1
5,67,4,4,3,1
5,55,4,2,3,1
5,66,4,4,3,1
2,76,1,1,2,0
4,57,4,4,3,1
5,71,3,1,3,0
5,70,4,5,3,1
4,35,4,2,?,0
5,79,1,?,3,1
4,63,2,1,3,0
5,40,1,4,3,1
4,41,1,1,3,0
4,47,2,1,2,0
4,68,1,1,3,1
4,64,4,3,3,1
4,65,4,4,?,1
4,73,4,3,3,0
4,39,4,3,3,0
5,55,4,5,4,1
5,53,3,4,4,0
5,66,4,4,3,1
4,43,3,1,2,0
5,44,4,5,3,1
4,77,4,4,3,1
4,62,2,4,3,0
5,80,4,4,3,1
4,33,4,4,3,0
4,50,4,5,3,1
4,71,1,?,3,0
5,46,4,4,3,1
5,49,4,5,3,1
4,53,1,1,3,0
3,46,2,1,2,0
4,57,1,1,3,0
4,54,3,1,3,0
4,54,1,?,?,0
2,49,2,1,2,0
4,47,3,1,3,0
4,40,1,1,3,0
4,45,1,1,3,0
4,50,4,5,3,1
5,54,4,4,3,1
4,67,4,1,3,1
4,77,4,4,3,1
4,66,4,3,3,0
4,71,2,?,3,1
4,36,2,3,3,0
4,69,4,4,3,0
4,48,1,1,3,0
4,64,4,4,3,1
4,71,4,2,3,1
5,60,4,3,3,1
4,24,1,1,3,0
5,34,4,5,2,1
4,79,1,1,2,0
4,45,1,1,3,0
4,37,2,1,2,0
4,42,1,1,2,0
4,72,4,4,3,1
5,60,4,5,3,1
5,85,3,5,3,1
4,51,1,1,3,0
5,54,4,5,3,1
5,55,4,3,3,1
4,64,4,4,3,0
5,67,4,5,3,1
5,75,4,3,3,1
5,87,4,4,3,1
4,46,4,4,3,1
4,59,2,1,?,0
55,46,4,3,3,1
5,61,1,1,3,1
4,44,1,4,3,0
4,32,1,1,3,0
4,62,1,1,3,0
5,59,4,5,3,1
4,61,4,1,3,0
5,78,4,4,3,1
5,42,4,5,3,0
4,45,1,2,3,0
5,34,2,1,3,1
5,39,4,3,?,1
4,27,3,1,3,0
4,43,1,1,3,0
5,83,4,4,3,1
4,36,2,1,3,0
4,37,2,1,3,0
4,56,3,1,3,1
5,55,4,4,3,1
5,46,3,?,3,0
4,88,4,4,3,1
5,71,4,4,3,1
4,41,2,1,3,0
5,49,4,4,3,1
3,51,1,1,4,0
4,39,1,3,3,0
4,46,2,1,3,0
5,52,4,4,3,1
5,58,4,4,3,1
4,67,4,5,3,1
5,80,4,4,3,1
3,46,1,?,?,0
3,43,1,?,?,0
4,45,1,1,3,0
5,68,4,4,3,1
4,54,4,4,?,1
4,44,2,3,3,0
5,74,4,3,3,1
5,55,4,5,3,0
4,49,4,4,3,1
4,49,1,1,3,0
5,50,4,3,3,1
5,52,3,5,3,1
4,45,1,1,3,0
4,66,1,1,3,0
4,68,4,4,3,1
4,72,2,1,3,0
5,64,?,?,3,0
2,49,?,3,3,0
3,44,?,4,3,0
5,74,4,4,3,1
5,58,4,4,3,1
4,77,2,3,3,0
4,49,3,1,3,0
4,34,?,?,4,0
5,60,4,3,3,1
5,69,4,3,3,1
4,53,2,1,3,0
3,46,3,4,3,0
5,74,4,4,3,1
4,58,1,1,3,0
5,68,4,4,3,1
5,46,4,3,3,0
5,61,2,4,3,1
5,70,4,3,3,1
5,37,4,4,3,1
3,65,4,5,3,1
4,67,4,4,3,0
5,69,3,4,3,0
5,76,4,4,3,1
4,65,4,3,3,0
5,72,4,2,3,1
4,62,4,2,3,0
5,42,4,4,3,1
5,66,4,3,3,1
5,48,4,4,3,1
4,35,1,1,3,0
5,60,4,4,3,1
5,67,4,2,3,1
5,78,4,4,3,1
4,66,1,1,3,1
4,26,1,1,?,0
4,48,1,1,3,0
4,31,1,1,3,0
5,43,4,3,3,1
5,72,2,4,3,0
5,66,1,1,3,1
4,56,4,4,3,0
5,58,4,5,3,1
5,33,2,4,3,1
4,37,1,1,3,0
5,36,4,3,3,1
4,39,2,3,3,0
4,39,4,4,3,1
5,83,4,4,3,1
4,68,4,5,3,1
5,63,3,4,3,1
5,78,4,4,3,1
4,38,2,3,3,0
5,46,4,3,3,1
5,60,4,4,3,1
5,56,2,3,3,1
4,33,1,1,3,0
4,?,4,5,3,1
4,69,1,5,3,1
5,66,1,4,3,1
4,72,1,3,3,0
4,29,1,1,3,0
5,54,4,5,3,1
5,80,4,4,3,1
5,68,4,3,3,1
4,35,2,1,3,0
4,57,3,?,3,0
5,?,4,4,3,1
4,50,1,1,3,0
4,32,4,3,3,0
0,69,4,5,3,1
4,71,4,5,3,1
5,87,4,5,3,1
3,40,2,?,3,0
4,31,1,1,?,0
4,64,1,1,3,0
5,55,4,5,3,1
4,18,1,1,3,0
3,50,2,1,?,0
4,53,1,1,3,0
5,84,4,5,3,1
5,80,4,3,3,1
4,32,1,1,3,0
5,77,3,4,3,1
4,38,1,1,3,0
5,54,4,5,3,1
4,63,1,1,3,0
4,61,1,1,3,0
4,52,1,1,3,0
4,36,1,1,3,0
4,41,?,?,3,0
4,59,1,1,3,0
5,51,4,4,2,1
4,36,1,1,3,0
5,40,4,3,3,1
4,49,1,1,3,0
4,37,2,3,3,0
4,46,1,1,3,0
4,63,1,1,3,0
4,28,2,1,3,0
4,47,2,1,3,0
4,42,2,1,3,1
5,44,4,5,3,1
4,49,4,4,3,0
5,47,4,5,3,1
5,52,4,5,3,1
4,53,1,1,3,1
5,83,3,3,3,1
4,50,4,4,?,1
5,63,4,4,3,1
4,82,?,5,3,1
4,54,1,1,3,0
4,50,4,4,3,0
5,80,4,5,3,1
5,45,2,4,3,0
5,59,4,4,?,1
4,28,2,1,3,0
4,31,1,1,3,0
4,41,2,1,3,0
4,21,3,1,3,0
5,44,3,4,3,1
5,49,4,4,3,1
5,71,4,5,3,1
5,75,4,5,3,1
4,38,2,1,3,0
4,60,1,3,3,0
5,87,4,5,3,1
4,70,4,4,3,1
5,55,4,5,3,1
3,21,1,1,3,0
4,50,1,1,3,0
5,76,4,5,3,1
4,23,1,1,3,0
3,68,?,?,3,0
4,62,4,?,3,1
5,65,1,?,3,1
5,73,4,5,3,1
4,38,2,3,3,0
2,57,1,1,3,0
5,65,4,5,3,1
5,67,2,4,3,1
5,61,2,4,3,1
5,56,4,4,3,0
5,71,2,4,3,1
4,49,2,2,3,0
4,55,?,?,3,0
4,44,2,1,3,0
0,58,4,4,3,0
4,27,2,1,3,0
5,73,4,5,3,1
4,34,2,1,3,0
5,63,?,4,3,1
4,50,2,1,3,1
4,62,2,1,3,0
3,21,3,1,3,0
4,49,2,?,3,0
4,36,3,1,3,0
4,45,2,1,3,1
5,67,4,5,3,1
4,21,1,1,3,0
4,57,2,1,3,0
5,66,4,5,3,1
4,71,4,4,3,1
5,69,3,4,3,1
6,80,4,5,3,1
3,27,2,1,3,0
4,38,2,1,3,0
4,23,2,1,3,0
5,70,?,5,3,1
4,46,4,3,3,0
4,61,2,3,3,0
5,65,4,5,3,1
4,60,4,3,3,0
5,83,4,5,3,1
5,40,4,4,3,1
2,59,?,4,3,0
4,53,3,4,3,0
4,76,4,4,3,0
5,79,1,4,3,1
5,38,2,4,3,1
4,61,3,4,3,0
4,56,2,1,3,0
4,44,2,1,3,0
4,64,3,4,?,1
4,66,3,3,3,0
4,50,3,3,3,0
4,46,1,1,3,0
4,39,1,1,3,0
4,60,3,?,?,0
5,55,4,5,3,1
4,40,2,1,3,0
4,26,1,1,3,0
5,84,3,2,3,1
4,41,2,2,3,0
4,63,1,1,3,0
2,65,?,1,2,0
4,49,1,1,3,0
4,56,2,2,3,1
5,65,4,4,3,0
4,54,1,1,3,0
4,36,1,1,3,0
5,49,4,4,3,0
4,59,4,4,3,1
5,75,4,4,3,1
5,59,4,2,3,0
5,59,4,4,3,1
4,28,4,4,3,1
5,53,4,5,3,0
5,57,4,4,3,0
5,77,4,3,4,0
5,85,4,3,3,1
4,59,4,4,3,0
5,59,1,5,3,1
4,65,3,3,3,1
4,54,2,1,3,0
5,46,4,5,3,1
4,63,4,4,3,1
4,53,1,1,3,1
4,56,1,1,3,0
5,66,4,4,3,1
5,66,4,5,3,1
4,55,1,1,3,0
4,44,1,1,3,0
5,86,3,4,3,1
5,47,4,5,3,1
5,59,4,5,3,1
5,66,4,5,3,0
5,61,4,3,3,1
3,46,?,5,?,1
4,69,1,1,3,0
5,93,1,5,3,1
4,39,1,3,3,0
5,44,4,5,3,1
4,45,2,2,3,0
4,51,3,4,3,0
4,56,2,4,3,0
4,66,4,4,3,0
5,61,4,5,3,1
4,64,3,3,3,1
5,57,2,4,3,0
5,79,4,4,3,1
4,57,2,1,?,0
4,44,4,1,1,0
4,31,2,1,3,0
4,63,4,4,3,0
4,64,1,1,3,0
5,47,4,5,3,0
5,68,4,5,3,1
4,30,1,1,3,0
5,43,4,5,3,1
4,56,1,1,3,0
4,46,2,1,3,0
4,67,2,1,3,0
5,52,4,5,3,1
4,67,4,4,3,1
4,47,2,1,3,0
5,58,4,5,3,1
4,28,2,1,3,0
4,43,1,1,3,0
4,57,2,4,3,0
5,68,4,5,3,1
4,64,2,4,3,0
4,64,2,4,3,0
5,62,4,4,3,1
4,38,4,1,3,0
5,68,4,4,3,1
4,41,2,1,3,0
4,35,2,1,3,1
4,68,2,1,3,0
5,55,4,4,3,1
5,67,4,4,3,1
4,51,4,3,3,0
2,40,1,1,3,0
5,73,4,4,3,1
4,58,?,4,3,1
4,51,?,4,3,0
3,50,?,?,3,1
5,59,4,3,3,1
6,60,3,5,3,1
4,27,2,1,?,0
5,54,4,3,3,0
4,56,1,1,3,0
5,53,4,5,3,1
4,54,2,4,3,0
5,79,1,4,3,1
5,67,4,3,3,1
5,64,3,3,3,1
4,70,1,2,3,1
5,55,4,3,3,1
5,65,3,3,3,1
5,45,4,2,3,1
4,57,4,4,?,1
5,49,1,1,3,1
4,24,2,1,3,0
4,52,1,1,3,0
4,50,2,1,3,0
4,35,1,1,3,0
5,?,3,3,3,1
5,64,4,3,3,1
5,40,4,1,1,1
5,66,4,4,3,1
4,64,4,4,3,1
5,52,4,3,3,1
5,43,1,4,3,1
4,56,4,4,3,0
4,72,3,?,3,0
6,51,4,4,3,1
4,79,4,4,3,1
4,22,2,1,3,0
4,73,2,1,3,0
4,53,3,4,3,0
4,59,2,1,3,1
4,46,4,4,2,0
5,66,4,4,3,1
4,50,4,3,3,1
4,58,1,1,3,1
4,55,1,1,3,0
4,62,2,4,3,1
4,60,1,1,3,0
5,57,4,3,3,1
4,57,1,1,3,0
6,41,2,1,3,0
4,71,2,1,3,1
4,32,2,1,3,0
4,57,2,1,3,0
4,19,1,1,3,0
4,62,2,4,3,1
5,67,4,5,3,1
4,50,4,5,3,0
4,65,2,3,2,0
4,40,2,4,2,0
6,71,4,4,3,1
6,68,4,3,3,1
4,68,1,1,3,0
4,29,1,1,3,0
4,53,2,1,3,0
5,66,4,4,3,1
4,60,3,?,4,0
5,76,4,4,3,1
4,58,2,1,2,0
5,96,3,4,3,1
5,70,4,4,3,1
4,34,2,1,3,0
4,59,2,1,3,0
4,45,3,1,3,1
5,65,4,4,3,1
4,59,1,1,3,0
4,21,2,1,3,0
3,43,2,1,3,0
4,53,1,1,3,0
4,65,2,1,3,0
4,64,2,4,3,1
4,53,4,4,3,0
4,51,1,1,3,0
4,59,2,4,3,0
4,56,2,1,3,0
4,60,2,1,3,0
4,22,1,1,3,0
4,25,2,1,3,0
6,76,3,?,3,0
5,69,4,4,3,1
4,58,2,1,3,0
5,62,4,3,3,1
4,56,4,4,3,0
4,64,1,1,3,0
4,32,2,1,3,0
5,48,?,4,?,1
5,59,4,4,2,1
4,52,1,1,3,0
4,63,4,4,3,0
5,67,4,4,3,1
5,61,4,4,3,1
5,59,4,5,3,1
5,52,4,3,3,1
4,35,4,4,3,0
5,77,3,3,3,1
5,71,4,3,3,1
5,63,4,3,3,1
4,38,2,1,2,0
5,72,4,3,3,1
4,76,4,3,3,1
4,53,3,3,3,0
4,67,4,5,3,0
5,69,2,4,3,1
4,54,1,1,3,0
2,35,2,1,2,0
5,68,4,3,3,1
4,68,4,4,3,0
4,67,2,4,3,1
3,39,1,1,3,0
4,44,2,1,3,0
4,33,1,1,3,0
4,60,?,4,3,0
4,58,1,1,3,0
4,31,1,1,3,0
3,23,1,1,3,0
5,56,4,5,3,1
4,69,2,1,3,1
6,63,1,1,3,0
4,65,1,1,3,1
4,44,2,1,2,0
4,62,3,3,3,1
4,67,4,4,3,1
4,56,2,1,3,0
4,52,3,4,3,0
4,43,1,1,3,1
4,41,4,3,2,1
4,42,3,4,2,0
3,46,1,1,3,0
5,55,4,4,3,1
5,58,4,4,2,1
5,87,4,4,3,1
4,66,2,1,3,0
0,72,4,3,3,1
5,60,4,3,3,1
5,83,4,4,2,1
4,31,2,1,3,0
4,53,2,1,3,0
4,64,2,3,3,0
5,31,4,4,2,1
5,62,4,4,2,1
4,56,2,1,3,0
5,58,4,4,3,1
4,67,1,4,3,0
5,75,4,5,3,1
5,65,3,4,3,1
5,74,3,2,3,1
4,59,2,1,3,0
4,57,4,4,4,1
4,76,3,2,3,0
4,63,1,4,3,0
4,44,1,1,3,0
4,42,3,1,2,0
4,35,3,?,2,0
5,65,4,3,3,1
4,70,2,1,3,0
4,48,1,1,3,0
4,74,1,1,1,1
6,40,?,3,4,1
4,63,1,1,3,0
5,60,4,4,3,1
5,86,4,3,3,1
4,27,1,1,3,0
4,71,4,5,2,1
5,85,4,4,3,1
4,51,3,3,3,0
6,72,4,3,3,1
5,52,4,4,3,1
4,66,2,1,3,0
5,71,4,5,3,1
4,42,2,1,3,0
4,64,4,4,2,1
4,41,2,2,3,0
4,50,2,1,3,0
4,30,1,1,3,0
4,67,1,1,3,0
5,62,4,4,3,1
4,46,2,1,2,0
4,35,1,1,3,0
4,53,1,1,2,0
4,59,2,1,3,0
4,19,3,1,3,0
5,86,2,1,3,1
4,72,2,1,3,0
4,37,2,1,2,0
4,46,3,1,3,1
4,45,1,1,3,0
4,48,4,5,3,0
4,58,4,4,3,1
4,42,1,1,3,0
4,56,2,4,3,1
4,47,2,1,3,0
4,49,4,4,3,1
5,76,2,5,3,1
5,62,4,5,3,1
5,64,4,4,3,1
5,53,4,3,3,1
4,70,4,2,2,1
5,55,4,4,3,1
4,34,4,4,3,0
5,76,4,4,3,1
4,39,1,1,3,0
2,23,1,1,3,0
4,19,1,1,3,0
5,65,4,5,3,1
4,57,2,1,3,0
5,41,4,4,3,1
4,36,4,5,3,1
4,62,3,3,3,0
4,69,2,1,3,0
4,41,3,1,3,0
3,51,2,4,3,0
5,50,3,2,3,1
4,47,4,4,3,0
4,54,4,5,3,1
5,52,4,4,3,1
4,30,1,1,3,0
3,48,4,4,3,1
5,?,4,4,3,1
4,65,2,4,3,1
4,50,1,1,3,0
5,65,4,5,3,1
5,66,4,3,3,1
6,41,3,3,2,1
5,72,3,2,3,1
4,42,1,1,1,1
4,80,4,4,3,1
0,45,2,4,3,0
4,41,1,1,3,0
4,72,3,3,3,1
4,60,4,5,3,0
5,67,4,3,3,1
4,55,2,1,3,0
4,61,3,4,3,1
4,55,3,4,3,1
4,52,4,4,3,1
4,42,1,1,3,0
5,63,4,4,3,1
4,62,4,5,3,1
4,46,1,1,3,0
4,65,2,1,3,0
4,57,3,3,3,1
4,66,4,5,3,1
4,45,1,1,3,0
4,77,4,5,3,1
4,35,1,1,3,0
4,50,4,5,3,1
4,57,4,4,3,0
4,74,3,1,3,1
4,59,4,5,3,0
4,51,1,1,3,0
4,42,3,4,3,1
4,35,2,4,3,0
4,42,1,1,3,0
4,43,2,1,3,0
4,62,4,4,3,1
4,27,2,1,3,0
5,?,4,3,3,1
4,57,4,4,3,1
4,59,2,1,3,0
5,40,3,2,3,1
4,20,1,1,3,0
5,74,4,3,3,1
4,22,1,1,3,0
4,57,4,3,3,0
4,57,4,3,3,1
4,55,2,1,2,0
4,62,2,1,3,0
4,54,1,1,3,0
4,71,1,1,3,1
4,65,3,3,3,0
4,68,4,4,3,0
4,64,1,1,3,0
4,54,2,4,3,0
4,48,4,4,3,1
4,58,4,3,3,0
5,58,3,4,3,1
4,70,1,1,1,0
5,70,1,4,3,1
4,59,2,1,3,0
4,57,2,4,3,0
4,53,4,5,3,0
4,54,4,4,3,1
4,53,2,1,3,0
0,71,4,4,3,1
5,67,4,5,3,1
4,68,4,4,3,1
4,56,2,4,3,0
4,35,2,1,3,0
4,52,4,4,3,1
4,47,2,1,3,0
4,56,4,5,3,1
4,64,4,5,3,0
5,66,4,5,3,1
4,62,3,3,3,0"""

COL_BIRADS = 0
COL_AGE = 1
COL_SHAPE = 2
COL_MARGIN = 3
COL_DENSITY = 4
COL_SEVERITY = 5


# possible values for each column in the data
cancer_values: Sequence[Sequence[int]] = [
    range(1, 7),  # BI-RADS
    [0, 45, 55, 75],  # age
    range(1, 5),  # shape
    range(1, 6),  # margin
    range(1, 5),  # density
    range(2),  # severity
]


def process_row(vals: Sequence[str]) -> Sequence[int] | None:
    # omit rows that have missing data
    if "?" in vals:
        return None
    birads, age, shape, margin, density, severity = map(int, vals)
    # discretize age
    if age >= 75:
        age = 75
    elif age >= 55:
        age = 55
    elif age >= 45:
        age = 45
    else:
        age = 0
    # fix typos in birads column
    if birads == 0:
        birads = 1
    elif birads == 55:
        birads = 5
    return birads, age, shape, margin, density, severity


cancer_data = [
    row2
    for row in csv.reader(csv_file.split("\n"))
    if (row2 := process_row(row)) is not None
]


@dataclass
class Model:
    values: Sequence[Sequence[int]]  # possible values
    c_column: int  # class column index
    a_columns: Sequence[int]  # attribute column indices
    n: int  # N, total number of observations
    nc: Mapping[int, int]  # n(c) as nc[c]
    nac: Mapping[int, Mapping[tuple[int, int], int]]  # n(a_i,c) as nac[i][a_i,c]
    s: float  # s constant used by the credal classifier; ignored by bayes classifier


def train_model(
    values: Sequence[Sequence[int]],
    data: Sequence[Sequence[int]],
    c_column: int,
    a_columns: Sequence[int],
    s: float = 2.0,
) -> Model:
    assert all(all(val in vals for val, vals in zip(row, values)) for row in data)
    nc = Counter(row[c_column] for row in data)
    nac = {
        a_column: Counter((row[a_column], row[c_column]) for row in data)
        for a_column in a_columns
    }
    return Model(
        values=values,
        c_column=c_column,
        a_columns=a_columns,
        n=len(data),
        nc=nc,
        nac=nac,
        s=s,
    )


cancer_model = train_model(
    values=cancer_values,
    data=cancer_data,
    c_column=COL_SEVERITY,
    a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
)


def test_cancer_model() -> None:
    assert cancer_model.nc[0] == 427
    assert cancer_model.nc[1] == 403
    assert cancer_model.nac[COL_BIRADS][5, 1] == 286
    assert cancer_model.nac[COL_AGE][75, 0] == 10


def naive_bayes_prob(model: Model, test_row: Sequence[int], c: int) -> float:
    pc = model.nc[c] / model.n  # p(c)=n(c)/N
    if model.nc[c] == 0:
        return 0.0  # prevent division by zero... class not in data so probability 0
    else:
        pacs = [  # p(a|c)=n(a_i,c)/n(c)
            model.nac[a_column][test_row[a_column], c] / model.nc[c]
            for a_column in model.a_columns
        ]
        return pc * prod(pacs)


def naive_bayes_outcome(
    model: Model, test_row: Sequence[int]
) -> Sequence[float | None]:
    c_values = model.values[model.c_column]
    probs = {c: naive_bayes_prob(model, test_row, c) for c in c_values}
    max_prob = max(probs.values())
    c_test = test_row[model.c_column]
    return [1 if probs[c_test] + TOL >= max_prob else 0]


def mean_outcome(outcomes: Sequence[Sequence[float | None]]) -> Sequence[float | None]:
    def _mean(xs: Sequence[float | None]) -> float | None:
        xs2 = [x for x in xs if x is not None]
        return mean(xs2) if xs2 else None

    return list(map(_mean, zip(*outcomes)))


def test_mean_outcome() -> None:
    assert mean_outcome(
        [naive_bayes_outcome(cancer_model, row) for row in cancer_data]
    ) == [pytest.approx(0.8385, abs=0.0001)]


def kfcv_outcomes(
    # test(model, test_row) -> sequence of accuracy measures
    test: Callable[[Model, Sequence[int]], Sequence[float | None]],
    folds: int,
    values: Sequence[Sequence[int]],
    data: Sequence[Sequence[int]],
    c_column: int,
    a_columns: Sequence[int],
    s: float = 2.0,
) -> Sequence[Sequence[float | None]]:
    outcomes = []
    for fold in range(folds):
        test_data = data[fold::folds]
        test_indices = range(fold, len(data), folds)
        train_data = [row for i, row in enumerate(data) if i not in test_indices]
        model = train_model(values, train_data, c_column, a_columns, s)
        outcomes += [test(model, row) for row in test_data]
    return outcomes


def test_kfcv_outcomes() -> None:
    assert mean_outcome(
        kfcv_outcomes(
            test=naive_bayes_outcome,
            folds=10,
            values=cancer_values,
            data=cancer_data,
            c_column=COL_SEVERITY,
            a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
        )
    ) == [pytest.approx(0.8337, abs=0.0001)]


def naive_credal_prob(
    model: Model, test_row: Sequence[int], c: int
) -> tuple[float, float]:
    def interval(a: float, b: float) -> tuple[float, float]:
        return a / (b + model.s), (a + model.s) / (b + model.s)

    pc = interval(model.nc[c], model.n)
    pacs = [
        interval(model.nac[a_column][test_row[a_column], c], model.nc[c])
        for a_column in model.a_columns
    ]
    return pc[0] * prod(pac[0] for pac in pacs), pc[1] * prod(pac[1] for pac in pacs)


def naive_credal_outcome(
    model: Model, test_row: Sequence[int]
) -> Sequence[float | None]:
    c_values = model.values[model.c_column]
    probs = {c: naive_credal_prob(model, test_row, c) for c in c_values}
    max_lowprob = max(low for low, upp in probs.values())
    set_size = sum(1 if probs[c][1] + TOL >= max_lowprob else 0 for c in c_values)
    c_test = test_row[model.c_column]
    correct = probs[c_test][1] + TOL >= max_lowprob
    return [
        1 if correct else 0,  # accuracy
        (1 if correct else 0) if set_size == 1 else None,  # single accuracy
        (1 if correct else 0) if set_size != 1 else None,  # set accuracy
        set_size if set_size != 1 else None,  # indeterminate set size
        1 if set_size == 1 else 0,  # determinacy
    ]


def test_naive_credal_outcome() -> None:
    assert mean_outcome(
        kfcv_outcomes(
            test=naive_credal_outcome,
            folds=10,
            values=cancer_values,
            data=cancer_data,
            c_column=COL_SEVERITY,
            a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
        )
    ) == pytest.approx(
        [0.8409638554216867, 0.8384332925336597, 1, 2, 0.9843373493975903]
    )


def is_maximal(
    dominates: Callable[[int, int], bool],  # compares two classes
    cs: Sequence[int],  # sequence classes
) -> Sequence[bool]:
    def is_not_dominated(c1: int) -> bool:
        return all(not dominates(c2, c1) for c2 in cs)

    return [is_not_dominated(c1) for c1 in cs]


def naive_credal_outcome_2(
    model: Model, test_row: Sequence[int]
) -> Sequence[float | None]:

    def dominates(c1: int, c2: int) -> bool:
        return all(
            (
                ((model.nc[c2] + model.s * t) / (model.nc[c1] + model.s * (1 - t)))
                ** (len(model.a_columns) - 1)
            )
            * prod(
                model.nac[a_column][test_row[a_column], c1]
                / (model.nac[a_column][test_row[a_column], c2] + model.s * t)
                for a_column in model.a_columns
            )
            > 1 + TOL
            for t in [0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]
        )

    c_values = model.values[model.c_column]
    is_max_cs = is_maximal(dominates, c_values)
    set_size = sum(is_max_cs)
    c_test = test_row[model.c_column]
    correct = is_max_cs[c_values.index(c_test)]
    return [
        1 if correct else 0,  # accuracy
        (1 if correct else 0) if set_size == 1 else None,  # single accuracy
        (1 if correct else 0) if set_size != 1 else None,  # set accuracy
        set_size if set_size != 1 else None,  # indeterminate set size
        1 if set_size == 1 else 0,  # determinacy
    ]


def test_naive_credal_outcome_2() -> None:
    assert mean_outcome(
        kfcv_outcomes(
            test=naive_credal_outcome_2,
            folds=10,
            values=cancer_values,
            data=cancer_data,
            c_column=COL_SEVERITY,
            a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
        )
    ) == pytest.approx(
        # same as with naive_credal_outcome! this is due to large dataset
        [0.8409638554216867, 0.8384332925336597, 1, 2, 0.9843373493975903]
    )


def test_naive_credal_outcome_3() -> None:
    assert mean_outcome(
        kfcv_outcomes(
            test=naive_credal_outcome,
            folds=10,
            values=cancer_values,
            data=cancer_data[:50],
            c_column=COL_SEVERITY,
            a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
        )
    ) == pytest.approx([0.88, 0.8536585365853658, 1, 2, 0.82])
    assert mean_outcome(
        kfcv_outcomes(
            test=naive_credal_outcome_2,
            folds=10,
            values=cancer_values,
            data=cancer_data[:50],
            c_column=COL_SEVERITY,
            a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
        )
    ) == pytest.approx([0.86, 0.8409090909090909, 1, 2, 0.88])


def test_naive_credal_outcome_4() -> None:
    assert mean_outcome(
        kfcv_outcomes(
            test=naive_credal_outcome,
            folds=10,
            values=cancer_values,
            data=cancer_data[:100],
            c_column=COL_BIRADS,
            a_columns=[COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
        )
    ) == pytest.approx(
        [0.86, 0.8333333333333334, 0.8714285714285714, 4.642857142857143, 0.3]
    )
    assert mean_outcome(
        kfcv_outcomes(
            test=naive_credal_outcome,
            folds=10,
            values=cancer_values,
            data=cancer_data[:200],
            c_column=COL_BIRADS,
            a_columns=[COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
        )
    ) == pytest.approx(
        [0.815, 0.7704918032786885, 0.8846153846153846, 3.858974358974359, 0.61]
    )
    assert mean_outcome(
        kfcv_outcomes(
            test=naive_credal_outcome_2,
            folds=10,
            values=cancer_values,
            data=cancer_data[:400],
            c_column=COL_BIRADS,
            a_columns=[COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
        )
    ) == pytest.approx(
        [0.785, 0.7717041800643086, 0.8314606741573034, 3.1235955056179776, 0.7775]
    )


def test_zero_counts() -> None:
    model = train_model(
        values=[range(2), range(1)],
        data=[[0, 0]],
        c_column=0,
        a_columns=[1],
    )
    assert naive_bayes_outcome(model, [1, 0]) == [0]
    assert naive_credal_outcome(model, [1, 0]) == [1, None, 1, 2, 0]
    assert naive_credal_outcome_2(model, [1, 0]) == [1, None, 1, 2, 0]
