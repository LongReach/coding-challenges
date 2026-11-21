from typing import Dict, Tuple, List
import random

"""
Problem: https://leetcode.com/problems/random-pick-with-blacklist/description/
Difficulty: hard
Solved: yes

See ./thinking.txt for how my solution works.
"""


def seeded_ints_lcg(seed: int, n: int):
    """Psuedo-random number generator that's reasonably fast and even with distributions"""
    MASK = (1 << 64) - 1
    s = seed & MASK
    while True:
        s = (s * 6364136223846793005 + 1442695040888963407) & MASK
        yield ((s >> 32) * n) >> 32

class Solution:

    debug = False

    def __init__(self, n: int, blacklist: list[int]):
        """
        :param n: number of entries in full list, including blacklisted ones
        :param blacklist: list of blacklisted numbers
        """
        blacklist.sort()
        self.reduced_range = n - len(blacklist)

        self.print(f"Blacklist is: {blacklist}")

        # Build up range list. Each entry represents a sequence of consecutive non-blacklisted numbers.
        self.range_list: List[Tuple[int, int, int]] = []
        full_list_idx = 0
        actual_list_idx = 0
        for bl_item in blacklist:
            if bl_item == full_list_idx:
                # Can't create a range entry yet
                full_list_idx += 1
            else:
                # We need to create a new range entry
                range_entry = (actual_list_idx, full_list_idx, bl_item - full_list_idx)
                self.range_list.append(range_entry)
                self.print(f"Just placed range entry before {bl_item}: {range_entry}")
                actual_list_idx += bl_item - full_list_idx
                full_list_idx = bl_item + 1
        if full_list_idx < n:
            range_entry = (actual_list_idx, full_list_idx, n - full_list_idx)
            self.range_list.append(range_entry)
            self.print(f"Just placed range entry before {n}: {range_entry}")

        seed = random.randrange(0, 1000000)
        self.gen = seeded_ints_lcg(seed, self.reduced_range)

        self.run_test()

    def print(self, my_string: str):
        if self.debug:
            print(my_string)

    def pick(self) -> int:
        actual_idx = next(self.gen)
        choice = self.apply_range_list(actual_idx)

        self.print(f"Returning {choice}")
        return choice

    def apply_range_list(self, actual_list_idx: int, start_idx: int = 0, end_idx = -1) -> int:
        """
        Given an index into notional actual_list, return o non-blacklisted number that that maps to,
        or -1. This function recursively calls itself for ab O(log(n)) dictionary search.

        :param actual_list_idx: index into actual_list
        :param start_idx: start index for dictionary search in range_list
        :param end_idx: end index for dictionary search in range_list
        :return: a non-blacklisted number or -1
        """
        if end_idx == -1:
            end_idx = len(self.range_list)

        mid_idx = int((start_idx + end_idx) / 2)

        # If the bottom entry in the sequence of range entries is no good, return failure
        # (Desired item is to its left)
        if self.range_list[start_idx][0] > actual_list_idx:
            return -1
        if end_idx - start_idx <= 1:
            # It's definitely this entry
            dist = actual_list_idx - self.range_list[start_idx][0]
            return self.range_list[start_idx][1] + dist

        # Try dictionary search
        result = self.apply_range_list(actual_list_idx, mid_idx, end_idx)
        if result != -1:
            return result
        result = self.apply_range_list(actual_list_idx, start_idx, mid_idx)
        if result != -1:
            return result

        return -1

    def run_test(self):
        """Verifies that the dictionary search works"""
        if not self.debug:
            return
        for x in range(self.reduced_range):
            full_x = self.apply_range_list(x)
            self.print(f"Full list entry for {x} is {full_x}")

# Your Solution object will be instantiated and called as such:
# obj = Solution(n, blacklist)
# param_1 = obj.pick()

Solution.debug = True
solution = Solution(7, [2, 3, 5])
#solution = Solution(2, [])
for i in range(10):
    solution.pick()