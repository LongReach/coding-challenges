from typing import List, Any, Optional, Tuple

class CircularArray:

    """
    A circular array class. It functions as a FIFO queue, but the underlying list only has to be allocated once.
    """

    def __init__(self, size, fill_element: Any):
        self.array = [fill_element] * size
        self.start_idx = 0
        self.end_idx = 0

    def size(self) -> int:
        """Returns current size of queue"""
        if self.end_idx < self.start_idx:
            return len(self.array) - self.start_idx + self.end_idx
        return self.end_idx - self.start_idx

    def get_next(self) -> Optional[Any]:
        """Returns next item in queue, removing it from queue, or None if queue empty"""
        if self.start_idx == self.end_idx:
            return None
        result = self.array[self.start_idx]
        self.start_idx += 1
        if self.start_idx >= len(self.array):
            self.start_idx = 0
        return result

    def add(self, element: Any):
        """Adds item to end of queue"""
        self.array[self.end_idx] = element
        self.end_idx += 1
        if self.end_idx >= len(self.array):
            self.end_idx = 0

    def get_items(self):
        """Returns list of all items on queue"""
        out_elements = []
        idx = self.start_idx
        while idx != self.end_idx:
            out_elements.append(self.array[idx])
            idx += 1
            if idx >= len(self.array):
                idx = 0
        return out_elements

    def get_debug_info(self):
        return f"{self.start_idx}, {self.end_idx}"

class Solution:

    """
    Problem: https://leetcode.com/problems/escape-the-spreading-fire/description/
    Difficulty: hard
    Solved: yes

    Insight:

    Mark a map with how many turns it takes the fire to reach each square. Then, do the same thing
    with the person. However, at each square, we note the time "cushion" between the person's arrival
    and the time when the fire arrives. The cushion reflects the MAXIMUM wait time that would allow
    the person to safely reach a particular square, starting from the beginning.
    """

    debug = False
    print_pad = 3
    GIANT_NUMBER = 1000000000

    def maximumMinutes(self, grid: List[List[int]]) -> int:
        
        w = len(grid[0])
        h = len(grid)

        def get_visitable_neighbors(x: int, y: int):
            coords = [(x, y-1), (x-1, y), (x+1, y), (x, y+1)]
            results = []
            for cx, cy in coords:
                if cx < 0 or cy < 0 or cx >= w or cy >= h:
                    continue
                if grid[cy][cx] == 0:
                    results.append((cx, cy))
            return results

        # (x, y, turn)
        to_visit_fire = CircularArray(w * h + 10, (-1, -1, -1))
        fire_map: List[List[int]] = []
        for y in range(len(grid)):
            fire_map.append([-1] * len(grid[y]))
            for x in range(len(grid[y])):
                if grid[y][x] == 1:
                    to_visit_fire.add((x, y, 0))

        while to_visit_fire.size() > 0:
            # Let the fire move to to-visit points that can be entered
            point = to_visit_fire.get_next()
            x, y, turn = point
            if fire_map[y][x] == -1:
                # Mark turn
                fire_map[y][x] = turn
                neighbors = get_visitable_neighbors(x, y)
                for n in neighbors:
                    to_visit_fire.add((n[0], n[1], turn+1))

        self.print_map(grid)
        self.print()
        self.print_move_map(fire_map)

        # (x, y, turn, cushion)
        to_visit_person = CircularArray(w * h + 10, (-1, -1, -1, -1))
        # (turn, cushion)
        person_map: List[List[Tuple[int, int]]] = []
        for i in range(h):
            person_map.append([(-1, -1)] * w)
        to_visit_person.add((0, 0, 0, self.GIANT_NUMBER))

        def needs_marking(_x, _y, _cushion) -> bool:
            _turn, _existing_cushion = person_map[_y][_x]
            if _turn == -1 and _existing_cushion == -1:
                return True
            if _existing_cushion < _cushion:
                return True
            return False

        while to_visit_person.size() > 0:
            # Let the person move to to-visit points that can be entered
            point = to_visit_person.get_next()
            x, y, turn, cushion = point
            if needs_marking(x, y, cushion):
                # Update cushion value?
                if fire_map[y][x] == -1:
                    new_cushion = self.GIANT_NUMBER
                else:
                    if x == (w-1) and y == (h-1):
                        # It's okay if the fire reaches the person right after person gets into
                        # safe house.
                        new_cushion = fire_map[y][x] - turn
                    else:
                        new_cushion = fire_map[y][x] - turn - 1

                if new_cushion < 0:
                    new_cushion = -1
                if new_cushion < cushion:
                    cushion = new_cushion

                # Mark turn
                person_map[y][x] = (turn, cushion)
                if cushion >= 0:
                    neighbors = get_visitable_neighbors(x, y)
                    for n in neighbors:
                        to_visit_person.add((n[0], n[1], turn+1, cushion))

        self.print()
        self.print_move_map(person_map, is_fire=False, show_cushion=False)
        self.print()
        self.print_move_map(person_map, is_fire=False, show_cushion=True)

        self.print(f"Returning: {person_map[h-1][w-1][1]}")
        return person_map[h-1][w-1][1]

    def print_map(self, grid):
        out_str = " " * self.print_pad + " "
        for x in range(len(grid[0])):
            out_str += f"{x:{self.print_pad}}"
        self.print(out_str)
        self.print()
        for y, row in enumerate(grid):
            out_str = f"{y:{self.print_pad}} "
            for x, val in enumerate(row):
                block_str = "#" if val == 2 else ("^" if val == 1 else " ")
                out_str += f"{block_str}" * self.print_pad
            self.print(out_str)

    def print_move_map(self, move_map, is_fire = True, show_cushion = False):
        out_str = " " * self.print_pad + " "
        for x in range(len(move_map[0])):
            out_str += f"{x:{self.print_pad}}"
        self.print(out_str)
        self.print()
        for y, row in enumerate(move_map):
            out_str = f"{y:{self.print_pad}} "
            for x, val in enumerate(row):
                if is_fire:
                    show_str = ("-" * self.print_pad) if val == -1 else f"{val:{self.print_pad}}"
                else:
                    if show_cushion:
                        if val[1] == self.GIANT_NUMBER:
                            show_str = "." * self.print_pad
                        else:
                            show_str = ("-" * self.print_pad) if val[1] == -1 else f"{val[1]:{self.print_pad}}"
                    else:
                        show_str = ("-" * self.print_pad) if val[0] == -1 else f"{val[0]:{self.print_pad}}"
                out_str += show_str
            self.print(out_str)

    def print(self, s = ""):
        if self.debug:
            print(s)

Solution.debug = True
Solution.print_pad = 3
#grid = [[0,2,0,0,0,0,0],[0,0,0,2,2,1,0],[0,2,0,0,1,2,0],[0,0,2,2,2,0,2],[0,0,0,0,0,0,0]]
#grid = [[0,0,0,0],[0,1,2,0],[0,2,0,0]]
#grid = [[0,0,0],[2,2,0],[1,2,0]]
grid = [[0,2,0,0,1],[0,2,0,2,2],[0,2,0,0,0],[0,0,2,2,0],[0,0,0,0,0]]
#grid = [[0,0],[0,0]]
#grid = [[0,0,0,0,0],[0,2,0,2,0],[0,2,0,2,0],[0,2,1,2,0],[0,2,2,2,0],[0,0,0,0,0]]
Solution().maximumMinutes(grid)