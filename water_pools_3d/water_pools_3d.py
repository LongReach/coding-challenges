from typing import List

class Solution:

    """
    Problem: https://leetcode.com/problems/trapping-rain-water-ii/
    Difficulty: hard
    Solved: yes

    Idea:

    Start scanning typewriter style. At each coordinate, if space is hemmed in by water or solid blocks
    to the north and west, we place water. If both neighbors are wet but of different heights, then
    we raise water to the height of highest neighbor and mark it for drainage later. We all mark wet
    squares on the left or bottom of whole grid as needing drainage.

    Draining process:
    Drain each square down to height of lowest neighbor (if not possible, remove all water). Then,
    mark the neighboring wet squares as needing drainage. Keep iterating until there are no more
    squares needing drainage.
    """

    debug = False

    def trapRainWater(self, heightMap: List[List[int]]) -> int:
        water_map = []
        for y, row in enumerate(heightMap):
            water_map_row = [0] * len(row)
            water_map.append(water_map_row)

        if self.debug:
            self.print("Empty map:")
            self.print_map(heightMap, water_map)
            self.print("")

        # Squares in this list will need to be drained
        drain_points = []

        water_count = 0
        for y in range(1, len(heightMap)):
            for x in range(1, len(heightMap[y])):
                north_neighor_h = heightMap[y-1][x] + water_map[y-1][x]
                west_neighor_h = heightMap[y][x-1] + water_map[y][x-1]
                h = heightMap[y][x]
                if north_neighor_h <= h and west_neighor_h <= h:
                    # Both neighbors are below this one, no water needed
                    water_map[y][x] = 0
                else:
                    # One or both neighbors are above this one, so water needed.
                    # Rise to level of highest neighbor height (for now).
                    water_map[y][x] = (north_neighor_h if north_neighor_h > west_neighor_h else west_neighor_h) - h
                    if north_neighor_h != west_neighor_h:
                        # This point will need to be drained, due to discrepancy
                        drain_points.append((x, y))
                    water_count += water_map[y][x]
                    if y == len(heightMap) - 1 or x == len(heightMap[0]) - 1:
                        # This point will need to be drained, due to being on edge of map
                        drain_points.append((x, y))

        if self.debug:
            self.print(f"First add-water pass, water count to {water_count}:")
            self.print_map(heightMap, water_map)
            self.print()

        water_drained = self.drain_water(heightMap, water_map, drain_points)

        if self.debug:
            self.print(f"After drainage of {water_drained} units:")
            self.print_map(heightMap, water_map)
            self.print()

        water_count -= water_drained
        self.print(f"Final amount of water: {water_count}")
        return water_count

    def drain_water(self, height_map: List[List[int]], water_map: List[List[int]], drain_points: List) -> int:

        def get_water_height(_x: int, _y: int) -> (int, bool):
            if _x < 0 or _y < 0 or _y >= len(height_map) or _x >= len(height_map[0]):
                return 0, False
            #print(f"**** dumb {_x}, {_y}")
            return height_map[_y][_x] + water_map[_y][_x], water_map[_y][_x] > 0

        waiter_drained = 0
        while len(drain_points) > 0:
            point = drain_points.pop()
            x, y = point[0], point[1]
            wh0, wet0 = get_water_height(x,y) # This point
            wh1,wet1 = get_water_height(x-1, y) # West
            wh2, wet2 = get_water_height(x, y-1) # North
            wh3, wet3 = get_water_height(x+1, y) # East
            wh4, wet4 = get_water_height(x, y+1) # South

            # Drain current square
            old_wh0 = wh0
            target_wh = wh0
            neighbor_whs = [wh1, wh2, wh3, wh4]
            for n_wh in neighbor_whs:
                if n_wh < target_wh:
                    target_wh = n_wh
            wh0 = target_wh
            water_map[y][x] = wh0 - height_map[y][x] if wh0 > height_map[y][x] else 0
            if wh0 == old_wh0:
                # Height unchanged, so neighbors unaffected
                continue
            old_water_amount = old_wh0 - height_map[y][x]
            drain_amount = old_wh0 - wh0
            if drain_amount > old_water_amount:
                drain_amount = old_water_amount
            self.print(f"Drained square {x}, {y} from {old_wh0} to {wh0} by {drain_amount}")
            waiter_drained += drain_amount

            # Now mark neighbors that need drainage
            neighbor_coords = [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]
            neighbor_wet_vals = [wet1, wet2, wet3, wet4]
            for i, n_wh in enumerate(neighbor_whs):
                if n_wh > wh0 and neighbor_wet_vals[i]:
                    # This neighbor needs to be drained
                    drain_points.append((neighbor_coords[i][0], neighbor_coords[i][1]))

        return waiter_drained


    def print_map(self, height_map: List[List[int]], water_map: List[List[int]]):
        for y in range(len(height_map)):
            line_str = ""
            for x in range(len(height_map[y])):
                if water_map[y][x] > 0:
                    line_str += f" {water_map[y][x] + height_map[y][x]}  "
                else:
                    line_str += f"[{height_map[y][x]}] "
            print(line_str)

    def print(self, s: str = ""):
        if self.debug:
            print(s)

Solution.debug = True
heightMap = [[1, 4, 3, 1, 3, 2], [3, 2, 1, 3, 2, 4], [2, 3, 3, 2, 3, 1]]
#heightMap = [[3,3,3,3,3],[3,2,2,2,3],[3,2,1,2,3],[3,2,2,2,3],[3,3,3,3,3]]
#heightMap = [[9,9,9,9,9,9,8,9,9,9,9],[9,0,0,0,0,0,1,0,0,0,9],[9,0,0,0,0,0,0,0,0,0,9],[9,0,0,0,0,0,0,0,0,0,9],[9,9,9,9,9,9,9,9,9,9,9]]
Solution().trapRainWater(heightMap)