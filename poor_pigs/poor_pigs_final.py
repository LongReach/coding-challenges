import math
from typing import List, Any, Dict, Tuple

"""
Problem: https://leetcode.com/problems/poor-pigs/
Difficulty: hard
Solution successful: yes

See ./thinking.txt for my reasoning on this problem.
"""

class Solution:

    debug = False

    def __init__(self):
        pass

    def print(self, my_string: str):
        if self.debug:
            print(my_string)

    def poorPigs(self, buckets: int, minutesToDie: int, minutesToTest: int) -> int:
        num_turns = int(minutesToTest / minutesToDie)
        pigs = 0
        while (num_turns+1) ** pigs < buckets:
            pigs += 1
        self.print(f"Pigs needed for {buckets} buckets, {num_turns} turns: {pigs}")
        return pigs



Solution.debug = True
#Solution().poorPigs(4, 15, 15)
#Solution().poorPigs(4, 15, 30)
#Solution().poorPigs(1000, 15, 60)
Solution().poorPigs(125, 1, 4)