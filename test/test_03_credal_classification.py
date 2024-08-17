import csv
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from math import prod
from statistics import mean
from typing import NamedTuple

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
cancer_domains: Sequence[Sequence[int]] = [
    range(1, 7),  # BI-RADS: 1-6
    [0, 45, 55, 75],  # age: 0+, 45+, 55+, 75+
    range(1, 5),  # shape: 1-4
    range(1, 6),  # margin: 1-5
    range(1, 5),  # density: 1-4
    range(2),  # severity: 0-1
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
    # fix typos in BI-RADS column
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
    domains: Sequence[Sequence[int]]  # possible values for each column
    c_column: int  # class column index
    a_columns: Sequence[int]  # attribute column indices
    n: int  # N, total number of observations
    nc: Mapping[int, int]  # n(c) as nc[c]
    nac: Mapping[int, Mapping[tuple[int, int], int]]  # n(a_i,c) as nac[i][a_i,c]
    s: float  # s constant used by the credal classifier; ignored by bayes classifier


def train_model(
    domains: Sequence[Sequence[int]],
    data: Sequence[Sequence[int]],
    c_column: int,
    a_columns: Sequence[int],
    s: float = 2.0,
) -> Model:
    assert all(all(val in vals for val, vals in zip(row, domains)) for row in data)
    nc = Counter(row[c_column] for row in data)
    nac = {
        a_column: Counter((row[a_column], row[c_column]) for row in data)
        for a_column in a_columns
    }
    return Model(
        domains=domains,
        c_column=c_column,
        a_columns=a_columns,
        n=len(data),
        nc=nc,
        nac=nac,
        s=s,
    )


cancer_model = train_model(
    domains=cancer_domains,
    data=cancer_data,
    c_column=COL_SEVERITY,
    a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
)


def test_cancer_model() -> None:
    assert cancer_model.nc[0] == 427
    assert cancer_model.nc[1] == 403
    assert cancer_model.nac[COL_BIRADS][5, 1] == 286
    assert cancer_model.nac[COL_AGE][75, 0] == 10


def naive_bayes_prob_1(model: Model, test_row: Sequence[int], c: int) -> float:
    n = model.n
    nc = model.nc[c]
    nacs = [model.nac[a_column][test_row[a_column], c] for a_column in model.a_columns]
    pc = nc / n
    pacs = [nac / nc for nac in nacs]
    return pc * prod(pacs)


def naive_bayes_prob_2(model: Model, test_row: Sequence[int], c: int) -> float:
    tc: float = 1 / len(model.domains[model.c_column])
    tacs: Sequence[float] = [
        tc / len(model.domains[a_column]) for a_column in model.a_columns
    ]
    n = model.n + model.s
    nc = model.nc[c] + model.s * tc
    nacs = [
        model.nac[a_column][test_row[a_column], c] + model.s * tac
        for a_column, tac in zip(model.a_columns, tacs)
    ]
    pc = nc / n
    pacs = [nac / nc for nac in nacs]
    return pc * prod(pacs)


def naive_bayes_predict(model: Model, test_row: Sequence[int]) -> Sequence[bool]:
    c_domain = model.domains[model.c_column]
    probs = [naive_bayes_prob_2(model, test_row, c) for c in c_domain]
    max_prob = max(probs)
    return [prob + TOL >= max_prob for prob in probs]


class Diagnostic(NamedTuple):
    accuracy: float | None
    single_accuracy: float | None
    set_accuracy: float | None
    indeterminate_set_size: float | None
    determinacy: float | None
    discounted_accuracy: float | None


def model_diagnostic(
    model: Model,
    test_row: Sequence[int],
    predict: Callable[[Model, Sequence[int]], Sequence[bool]],
) -> Diagnostic:
    outcome: Sequence[bool] = predict(model, test_row)  # predicted classes
    test_c: int = test_row[model.c_column]  # actual class
    correct: bool = outcome[model.domains[model.c_column].index(test_c)]
    set_size: int = sum(outcome)
    accuracy: int = 1 if correct else 0
    return Diagnostic(
        accuracy=accuracy,
        single_accuracy=accuracy if set_size == 1 else None,
        set_accuracy=accuracy if set_size != 1 else None,
        indeterminate_set_size=set_size if set_size != 1 else None,
        determinacy=1 if set_size == 1 else 0,
        discounted_accuracy=accuracy / set_size,
    )


def mean_diagnostic(diagnostics: Sequence[Diagnostic]) -> Diagnostic:
    def _mean(xs: Sequence[float | None]) -> float | None:
        xs2 = [x for x in xs if x is not None]
        return mean(xs2) if xs2 else None

    return Diagnostic(*map(_mean, zip(*diagnostics)))


def test_model_diagnostic() -> None:
    assert mean_diagnostic(
        [
            model_diagnostic(cancer_model, row, naive_bayes_predict)
            for row in cancer_data
        ]
    ) == pytest.approx(
        Diagnostic(
            accuracy=0.8385542168674699,
            single_accuracy=0.8383594692400482,
            set_accuracy=1,
            indeterminate_set_size=2,
            determinacy=0.9987951807228915,
            discounted_accuracy=0.8379518072289157,
        )
    )


def cross_validation_diagnostic(
    predict: Callable[[Model, Sequence[int]], Sequence[bool]],
    folds: int,
    domains: Sequence[Sequence[int]],
    data: Sequence[Sequence[int]],
    c_column: int,
    a_columns: Sequence[int],
    s: float = 2.0,
) -> Diagnostic:
    diagnostics: list[Diagnostic] = []
    for fold in range(folds):
        test_data = data[fold::folds]
        test_indices = range(fold, len(data), folds)
        train_data = [row for i, row in enumerate(data) if i not in test_indices]
        model = train_model(domains, train_data, c_column, a_columns, s)
        diagnostics += [model_diagnostic(model, row, predict) for row in test_data]
    return mean_diagnostic(diagnostics)


def test_cross_validation_diagnostic() -> None:
    assert cross_validation_diagnostic(
        predict=naive_bayes_predict,
        folds=10,
        domains=cancer_domains,
        data=cancer_data,
        c_column=COL_SEVERITY,
        a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
    ) == pytest.approx(
        Diagnostic(
            accuracy=0.8337349397590361,
            single_accuracy=0.8333333333333334,
            set_accuracy=1,
            indeterminate_set_size=2,
            determinacy=0.9975903614457832,
            discounted_accuracy=0.8325301204819278,
        )
    )


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


def naive_credal_predict(model: Model, test_row: Sequence[int]) -> Sequence[bool]:
    c_domain = model.domains[model.c_column]
    probs = [naive_credal_prob(model, test_row, c) for c in c_domain]
    max_lowprob = max(low for low, upp in probs)
    return [upp + TOL >= max_lowprob for low, upp in probs]


def test_naive_credal_predict() -> None:
    assert cross_validation_diagnostic(
        predict=naive_credal_predict,
        folds=10,
        domains=cancer_domains,
        data=cancer_data,
        c_column=COL_SEVERITY,
        a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
    ) == pytest.approx(
        Diagnostic(
            accuracy=0.8409638554216867,
            single_accuracy=0.8384332925336597,
            set_accuracy=1,
            indeterminate_set_size=2,
            determinacy=0.9843373493975903,
            discounted_accuracy=0.8331325301204819,
        )
    )


def is_maximal(
    dominates: Callable[[int, int], bool],  # compares two classes
    cs: Sequence[int],  # sequence classes
) -> Sequence[bool]:
    def is_not_dominated(c1: int) -> bool:
        return all(not dominates(c2, c1) for c2 in cs)

    return [is_not_dominated(c1) for c1 in cs]


def naive_credal_predict_2(model: Model, test_row: Sequence[int]) -> Sequence[bool]:

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

    c_domain = model.domains[model.c_column]
    return is_maximal(dominates, c_domain)


def test_naive_credal_predict_2() -> None:
    assert cross_validation_diagnostic(
        predict=naive_credal_predict_2,
        folds=10,
        domains=cancer_domains,
        data=cancer_data,
        c_column=COL_SEVERITY,
        a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
    ) == pytest.approx(
        # same as with naive_credal_predict! this is due to large dataset
        Diagnostic(
            accuracy=0.8409638554216867,
            single_accuracy=0.8384332925336597,
            set_accuracy=1,
            indeterminate_set_size=2,
            determinacy=0.9843373493975903,
            discounted_accuracy=0.8331325301204819,
        )
    )


def test_naive_credal_predict_3() -> None:
    assert cross_validation_diagnostic(
        predict=naive_credal_predict,
        folds=10,
        domains=cancer_domains,
        data=cancer_data[:50],
        c_column=COL_SEVERITY,
        a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
    ) == pytest.approx([0.88, 0.8536585365853658, 1, 2, 0.82, 0.79])
    assert cross_validation_diagnostic(
        predict=naive_credal_predict_2,
        folds=10,
        domains=cancer_domains,
        data=cancer_data[:50],
        c_column=COL_SEVERITY,
        a_columns=[COL_BIRADS, COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
    ) == pytest.approx([0.86, 0.8409090909090909, 1, 2, 0.88, 0.8])


def test_naive_credal_predict_4() -> None:
    assert cross_validation_diagnostic(
        predict=naive_credal_predict,
        folds=10,
        domains=cancer_domains,
        data=cancer_data[:100],
        c_column=COL_BIRADS,
        a_columns=[COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
    ) == pytest.approx(
        [0.86, 0.833333333333, 0.871428571428, 4.64285714285, 0.3, 0.3828333333333]
    )
    assert cross_validation_diagnostic(
        predict=naive_credal_predict,
        folds=10,
        domains=cancer_domains,
        data=cancer_data[:200],
        c_column=COL_BIRADS,
        a_columns=[COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
    ) == pytest.approx(
        [0.815, 0.770491803278, 0.884615384615, 3.85897435897, 0.61, 0.562916666666]
    )
    assert cross_validation_diagnostic(
        predict=naive_credal_predict_2,
        folds=10,
        domains=cancer_domains,
        data=cancer_data[:400],
        c_column=COL_BIRADS,
        a_columns=[COL_AGE, COL_SHAPE, COL_MARGIN, COL_DENSITY],
    ) == pytest.approx(
        [0.785, 0.771704180064, 0.831460674157, 3.123595505617, 0.7775, 0.664625]
    )


def test_zero_counts_0() -> None:
    model = train_model(
        domains=[range(2), range(2)], data=[], c_column=0, a_columns=[1]
    )
    with pytest.raises(ZeroDivisionError):
        naive_bayes_prob_1(model=model, test_row=[0, 0], c=0)
    assert naive_bayes_prob_2(model=model, test_row=[0, 0], c=0) == pytest.approx(0.25)
    assert naive_bayes_prob_2(model=model, test_row=[0, 0], c=1) == pytest.approx(0.25)
    assert naive_bayes_prob_2(model=model, test_row=[0, 1], c=0) == pytest.approx(0.25)
    assert naive_bayes_prob_2(model=model, test_row=[0, 1], c=1) == pytest.approx(0.25)


def test_zero_counts_1() -> None:
    model = train_model(
        domains=[range(2), range(2)],
        data=[[0, 0]],
        c_column=0,
        a_columns=[1],
    )
    assert naive_bayes_predict(model, [1, 0]) == [True, False]
    assert naive_credal_predict(model, [1, 0]) == [True, True]
    assert naive_credal_predict_2(model, [1, 0]) == [True, True]


@pytest.mark.parametrize(
    "test_row",
    [
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1],
    ],
)
def test_zero_counts_2(test_row: Sequence[int]) -> None:
    model = train_model(
        domains=[range(2), range(2)],
        data=[],
        c_column=0,
        a_columns=[1],
    )
    assert naive_bayes_predict(model, test_row) == [True, True]
    assert naive_credal_predict(model, test_row) == [True, True]
    assert naive_credal_predict_2(model, test_row) == [True, True]
