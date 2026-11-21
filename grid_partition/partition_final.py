from typing import List, Any, Tuple, Dict

class Solution:

    """
    https://leetcode.com/problems/equal-sum-grid-partition-ii/description/
    Difficulty: hard
    Solution successful: yes

    Solution:

    For each row, add its cells together and then add that value to the sum of all previous rows. Store
    the total for the row.

    For the problem of removing a single cell, we prepare the ground by putting every unique integer found in
    the grid into a dictionary. Each entry contains:
    - lowest x position at which that integer is found
    - highest x position at which that integer is found
    - lowest y position at which that integer is found
    - highest y position at which that integer is found

    Next, go through the rows one by one and compare the total sums of the two sides created, if the split
    were to happen after that row. If the difference is zero, we've solved the problem and no cell needs to
    be removed. If the difference is non-zero, check the integer dictionary to find out if there's a cell
    that can be removed. In some cases, we can't actually do so, if it prevents connectivity between the
    remaining cells.

    Same idea with columns.
    """

    debug = False

    def canPartitionGrid(self, grid: List[List[int]]) -> bool:

        self.print("Grid:")
        for row in grid:
            self.print(row)

        grid_w = len(grid[0])
        grid_h = len(grid)

        # Maps an integer in the grid to (furthest left, furthest right, furthest up, furthest down)
        integer_lookup: Dict[int, Tuple[int, int, int, int]] = {}

        col_sums: List[int] = [0] * len(grid[0])

        self.print("Sums by row:")
        sum_by_row: List[int] = []
        total_sum = 0
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                integer_tup = integer_lookup.get(cell)
                if integer_tup is None:
                    integer_tup = (x, x, y, y)
                    integer_lookup[cell] = integer_tup
                if x < integer_tup[0]:
                    integer_tup = (x, integer_tup[1], integer_tup[2], integer_tup[3])
                    integer_lookup[cell] = integer_tup
                elif x > integer_tup[1]:
                    integer_tup = (integer_tup[0], x, integer_tup[2], integer_tup[3])
                    integer_lookup[cell] = integer_tup
                if y < integer_tup[2]:
                    integer_tup = (integer_tup[0], integer_tup[1], y, integer_tup[3])
                    integer_lookup[cell] = integer_tup
                elif y > integer_tup[3]:
                    integer_tup = (integer_tup[0], integer_tup[1], integer_tup[2], y)
                    integer_lookup[cell] = integer_tup
                col_sums[x] = col_sums[x] + cell
            total_sum += sum(row)
            sum_by_row.append(total_sum)
            self.print(f"{total_sum}")

        self.print("\nSums by column:")
        sum_by_col: List[int] = []
        total_sum = 0
        for col_sum in col_sums:
            total_sum += col_sum
            sum_by_col.append(total_sum)
            self.print(f"{total_sum}")

        self.print(f"Integer map: {integer_lookup}")

        if grid_h > 1:
            self.print("Looking for horizontal splits")
            # Look to split horizontally
            total_sum = sum_by_row[-1]
            for y, sum_1 in enumerate(sum_by_row):
                sum_2 = total_sum - sum_1
                diff = sum_2 - sum_1
                success = False
                if diff == 0:
                    self.print(f"Can split without subtraction after row {y}")
                    success = True
                elif diff < 0:
                    integer_tup = integer_lookup.get(-diff)
                    if integer_tup and integer_tup[2] <= y:
                        # Removable integer is in top part
                        self.print(f"Can split with top part subtraction, maybe, before row {y}")
                        if grid_w == 1:
                            # Top part is only one cell wide
                            if grid[0][0] == -diff or grid[y][0] == -diff:
                                success = True
                        elif y == 0:
                            # Top part is only one cell deep
                            # The cell can't be in the middle
                            if grid[y][0] == -diff or grid[y][-1] == -diff:
                                success = True
                        else:
                            success = True
                else:
                    integer_tup = integer_lookup.get(diff)
                    if integer_tup and integer_tup[3] > y:
                        # Removable integer is in bottom part
                        self.print(f"Can split with bottom part subtraction, maybe, after row {y}")
                        if grid_w == 1:
                            # Bottom part is only one cell wide
                            if grid[y+1][0] == diff or grid[-1][0] == diff:
                                success = True
                        elif y + 1 == grid_h - 1:
                            # Bottom part is only one cell deep
                            # The cell can't be in the middle
                            if grid[y+1][0] == diff or grid[y+1][-1] == diff:
                                success = True
                        else:
                            success = True
                if success:
                    self.print("Success!")
                    return True

        if grid_w > 1:
            self.print("Looking for vertical splits")
            # Look to split vertically
            total_sum = sum_by_col[-1]
            for x, sum_1 in enumerate(sum_by_col):
                sum_2 = total_sum - sum_1
                diff = sum_2 - sum_1
                success = False
                if diff == 0:
                    self.print(f"Can split without subtraction after column {x}")
                    success = True
                elif diff < 0:
                    integer_tup = integer_lookup.get(-diff)
                    if integer_tup and integer_tup[0] <= x:
                        # Removable integer in left part
                        self.print(f"Can split with top part subtraction, maybe, before column {x}")
                        if grid_h == 1:
                            # Left part is 1 cell high
                            if grid[0][0] == -diff or grid[0][x] == -diff:
                                success = True
                        elif x == 0:
                            # Left part is one cell deep
                            # The cell can't be in the middle
                            if grid[0][x] == -diff or grid[-1][x] == -diff:
                                success = True
                        else:
                            success = True
                else:
                    integer_tup = integer_lookup.get(diff)
                    if integer_tup and integer_tup[1] > x:
                        self.print(f"Can split with bottom part subtraction, maybe, after column {x}")
                        if grid_h == 1:
                            # Right part is one cell high
                            if grid[0][x+1] == diff or grid[0][-1] == diff:
                                success = True
                        elif x + 1 == grid_w - 1:
                            # Right part is one cell deep
                            # The cell can't be in the middle
                            if grid[0][x+1] == diff or grid[-1][x+1] == diff:
                                success = True
                        else:
                            success = True
                if success:
                    self.print("Success!")
                    return True

        return False

    def print(self, val):
        if self.debug:
            print(val)

Solution.debug = True
#Solution().canPartitionGrid([[1,4],[2,3]])
#Solution().canPartitionGrid([[1,2,4],[2,3,5]])
#Solution().canPartitionGrid([[2,2,2],[2,3,1],[1,1,1],[2,2,2]])
Solution().canPartitionGrid([[10,5,4,5]])