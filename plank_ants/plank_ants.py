from typing import List, Dict, Any

class Solution:

    """
    Problem: https://leetcode.com/problems/last-moment-before-all-ants-fall-out-of-a-plank/
    Difficulty: medium

    Solution:
    We just simulate the ants, as in a video game. Each tick is half a second, allowing them to
    meet in the middle between two markers.
    """

    def getLastMoment(self, n: int, left: List[int], right: List[int]) -> int:
        ants = []
        ant_idx = 0
        for x in right:
            ant_dict = {"x": x, "dir": 1.0, "alive": True, "index": ant_idx}
            ants.append(ant_dict)
            ant_idx += 1
        for x in left:
            ant_dict = {"x": x, "dir": -1.0, "alive": True, "index": ant_idx}
            ants.append(ant_dict)
            ant_idx += 1

        # Will hold index to any right-moving ant
        pos_array = [-1] * (n + 1)

        alive_count = len(ants)
        current_time = 0.0
        while alive_count:
            time_delta = 0.5
            alive_count = self.do_tick(pos_array, ants, time_delta)
            current_time += time_delta

        return int(current_time) - 1

    def do_tick(self, pos_array: List[int], ants: List[Dict[str, Any]], time_delta = 0.5) -> int:
        # Advance all ants, detaching from pos_array if needed
        for ant in ants:
            if not ant["alive"]:
                continue

            if ant["dir"] > 0:
                pos_idx = int(ant["x"])
                pos_array[pos_idx] = -1
            ant["x"] = ant["x"] + ant["dir"] * time_delta
            if ant["dir"] > 0:
                pos_idx = int(ant["x"])
                if 0 <= pos_idx < len(pos_array):
                    pos_array[pos_idx] = ant["index"]

        # Look for collisions or fallings
        alive_count = 0
        for ant in ants:
            if not ant["alive"]:
                continue
            alive_count += 1

            if ant["dir"] < 0:
                # This ant is going right
                other_idx = pos_array[int(ant["x"])]
                if other_idx >= 0:
                    other_ant = ants[other_idx]
                    if ant["x"] == other_ant["x"]:
                        # There's a collision, turn both around
                        ant["dir"] *= -1.0
                        other_ant["dir"] *= -1.0
                        # Now this ant is going left
                        pos_array[int(ant["x"])] = ant["index"]

            if ant["x"] <= -1.0 or ant["x"] >= float(len(pos_array)):
                # Ant has fallen
                ant["alive"] = False
                alive_count -= 1

        return alive_count

timestamp = Solution().getLastMoment(n = 4, left = [4,3], right = [0,1])
print(f"Last ant fell at: {timestamp}")