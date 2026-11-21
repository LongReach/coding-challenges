from typing import List, Any, Dict, Tuple
from bisect import bisect_left

class Solution:

    """
    https://leetcode.com/problems/maximum-walls-destroyed-by-robots/
    Difficulty: hard
    Solved: yes

    Insights:

    Whichever direction robot shoots in, it destroys all walls within range, unless bullet stopped by robot.
    Dynamic programming seems like a good solution. Since a robot can't shoot through another robot, then
    as we scan from left to right, that allows a most optimal solution thus far to be recalculated at each
    robot. Read about the design of the score table in comments further down.
    """

    debug = False

    def __init__(self):
        # Maps x position to (0 = wall / 1 = robot / 2 = both, index, shot range or -1)
        self.objects_map: Dict[int, Tuple[int, int, int]] = {}
        self.sorted_xs: List[int] = []
        self.sorted_robot_xs: List[int] = []
        self.sorted_wall_xs: List[int] = []

    def maxWalls(self, robots: List[int], distance: List[int], walls: List[int]) -> int:
        robots_and_dist = list(zip(robots, distance))
        print(f"Robots and shot distance: {robots_and_dist}")

        max_x = 0 # right-most x coordinate at which a robot or wall exists
        # Fill in objects map with robots
        for idx, x in enumerate(robots):
            self.objects_map[x] = (1, idx, distance[idx])
            max_x = max(x, max_x)

        # Fill in objects map with walls (can coexist with robots)
        for idx, x in enumerate(walls):
            current_entry = self.objects_map.get(x)
            if current_entry and current_entry[0] == 1:
                code = 2
                dist = current_entry[2]
            else:
                code = 0
                dist = -1
            self.objects_map[x] = (code, idx, dist)
            max_x = max(x, max_x)

        # Sort by x coordinate
        self.objects_map = dict(sorted(self.objects_map.items()))
        self.sorted_xs = list(self.objects_map.keys())

        self.sorted_robot_xs = [x for x in self.sorted_xs if self.objects_map[x][0] in [1, 2]]
        self.sorted_wall_xs = [x for x in self.sorted_xs if self.objects_map[x][0] in [0, 2]]

        if self.debug:
            obj_strs = [" "] * (max_x + 1)
            dist_strs = [" "] * (max_x + 1)
            for x, tup in self.objects_map.items():
                obj_type, idx, dist = tup
                obj_strs[x] = "#" if obj_type == 0 else ("@" if obj_type == 1 else "!")
                dist_strs[x] = str(dist) if dist >= 0 else " "
            self.print("Map:")
            self.print("-" * (max_x + 1))
            self.print("".join(obj_strs))
            self.print("".join(dist_strs))

            self.print(f"Coordinates: {self.sorted_xs}")
            self.print(f"Robots sorted: {self.sorted_robot_xs}")
            self.print(f"Walls sorted: {self.sorted_wall_xs}")

        # Maps robot x to list of walls to left of robot
        walls_to_left: Dict[int, List[int]] = {}

        # Go through robots left to right, tracking walls to the left of each
        wall_idx = 0
        robot_idx = 0
        while robot_idx < len(self.sorted_robot_xs):
            robot_x = self.sorted_robot_xs[robot_idx]
            # Shot distance
            dist = self.objects_map[robot_x][2]
            walls = []
            # Build list of walls to left of robot
            while wall_idx < len(self.sorted_wall_xs) and self.sorted_wall_xs[wall_idx] <= robot_x:
                if self.sorted_wall_xs[wall_idx] >= robot_x - dist:
                    walls.append(self.sorted_wall_xs[wall_idx])
                wall_idx += 1
            walls_to_left[robot_x] = walls
            self.print(f"Walls to left of robot at {robot_x}: {walls}")
            robot_idx += 1

        # Maps robot x to list of walls to right of robot
        walls_to_right: Dict[int, List[int]] = {}

        # Go through robots right to left, tracking walls to the right of each
        wall_idx = len(self.sorted_wall_xs) - 1
        robot_idx = len(self.sorted_robot_xs) - 1
        while robot_idx >= 0:
            robot_x = self.sorted_robot_xs[robot_idx]
            dist = self.objects_map[robot_x][2]
            walls = []
            while wall_idx >= 0 and robot_x <= self.sorted_wall_xs[wall_idx]:
                if self.sorted_wall_xs[wall_idx] <= robot_x + dist:
                    walls.append(self.sorted_wall_xs[wall_idx])
                wall_idx -= 1
            walls_to_right[robot_x] = walls
            self.print(f"Walls to right of robot at {robot_x}: {walls}")
            robot_idx -= 1

        # Go through robots left to right, build score table
        # Score table structure:
        #    index 0: robot x
        #    index 1: 0 for shot to left, 1 for shot to right
        #    value: (highest score that can be achieved if robot here shoots left/right, list of reachable walls to left/right by x coordinate)

        # The scores are cumulative, taking into account the highest possible score that can be achieved by robots to left of given one.
        # It's a dynamic programming solution.

        # Meaning
        score_table = [[(0, []) for i in range(2)] for x in self.sorted_robot_xs]
        score_table[0][0] = (len(walls_to_left[self.sorted_robot_xs[0]]), walls_to_left[self.sorted_robot_xs[0]])
        score_table[0][1] = (len(walls_to_right[self.sorted_robot_xs[0]]), walls_to_right[self.sorted_robot_xs[0]])
        for idx in range(1, len(score_table)):
            robot_x = self.sorted_robot_xs[idx]

            # Establish best score if robot shoots left

            # Previous also shoots left
            score_l_l = score_table[idx-1][0][0]
            left_list_1 = walls_to_left[robot_x]

            # Previous shoots right
            walls_to_subtract = set(score_table[idx-1][1][1])
            left_list_2 = [x for x in walls_to_left[robot_x] if x not in walls_to_subtract]
            score_l_r = score_table[idx-1][1][0]

            if score_l_l + len(left_list_1) > score_l_r + len(left_list_2):
                score_table[idx][0] = (score_l_l + len(left_list_1), left_list_1)
            else:
                score_table[idx][0] = (score_l_r + len(left_list_2), left_list_2)

            # Establish best score if robot shoots right

            # Previous shoots left
            score_r_l = score_table[idx - 1][0][0]
            right_list_1 = walls_to_right[robot_x]

            # Previous shoots right
            score_r_r = score_table[idx - 1][1][0]
            right_list_2 = walls_to_right[robot_x]

            if score_r_l + len(right_list_1) > score_r_r + len(right_list_2):
                score_table[idx][1] = (score_r_l + len(right_list_1), right_list_1)
            else:
                score_table[idx][1] = (score_r_r + len(right_list_2), right_list_2)

        if self.debug:
            print("Score table:")
            print("-" * len(self.sorted_robot_xs))
            for dir in range(2):
                show_list = [score_table[idx][dir][0] for idx in range(len(self.sorted_robot_xs))]
                show_list = [str(elem) for elem in show_list]
                print(" ".join(show_list))

        return max(score_table[-1][0][0], score_table[-1][1][0])

    def print(self, text: Any):
        if self.debug:
            print(text)


Solution.debug = True
#Solution().maxWalls(robots = [10,2], distance = [5,1], walls = [5,2,7])
Solution().maxWalls(robots = [1,2], distance = [100,1], walls = [10])
#Solution().maxWalls(robots = [4], distance = [3], walls = [1,10])