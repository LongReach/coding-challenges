from typing import List, Tuple, Optional

class ToVisitArray:
    """
    Helper class. It implements a FIFO array that holds coordinates in need of being visited. Under the hood, this
    array is circular for efficiency, with a memory allocation only needing to happen once. Another efficiency
    improvement is to avoid adding cells to to-visit list if already there.
    """

    def __init__(self, grid_h, grid_w, fill_element: Tuple[int, int]):
        self.array = [fill_element] * (grid_w * grid_h)
        self.start_idx = 0
        self.end_idx = 0
        self.to_visit_grid = []
        for y in range(grid_h):
            self.to_visit_grid.append([False] * grid_w)

    def size(self) -> int:
        """
        Returns number of cells that need visiting.
        """
        if self.end_idx < self.start_idx:
            return len(self.array) - self.start_idx + self.end_idx
        return self.end_idx - self.start_idx

    def get_next(self) -> Optional[Tuple[int, int]]:
        """
        Returns the next cell to be visited, if any, removing it from to-visit list.
        :return: (x, y) or None
        """
        if self.start_idx == self.end_idx:
            return None
        result = self.array[self.start_idx]
        x, y = result
        self.to_visit_grid[y][x] = False
        self.start_idx += 1
        if self.start_idx >= len(self.array):
            self.start_idx = 0
        return result

    def add(self, element: Tuple[int, int]):
        """
        Adds a cell to the to-visit list, if not already on it.
        """
        x, y = element
        if self.to_visit_grid[y][x]:
            # No need to add, already there
            return
        self.array[self.end_idx] = element
        self.end_idx += 1
        if self.end_idx >= len(self.array):
            self.end_idx = 0
        self.to_visit_grid[y][x] = True

    def get_items(self):
        """Returns all cells on to-visit list, as list"""
        out_elements = []
        idx = self.start_idx
        while idx != self.end_idx:
            out_elements.append(self.array[idx])
            idx += 1
            if idx >= len(self.array):
                idx = 0
        return out_elements

class Solution:
    """
    Problem: https://leetcode.com/problems/maximum-number-of-points-from-grid-queries/
    Difficulty: hard
    Solution successful: yes

    Basic idea:
    Each square has a lowest query that can reach it. We start with the upper-left square,
    find its query, then explore its neighbors. Each neighbor receives the lowest possible
    query value that has been set for one of its own neighbors, unless it has a higher
    "height" than that lowest query. In that case, it receives the lowest query value that works
    for its own height. Then, its neighbors are explored and assigned query values.

    Sometimes, a square that already has a query value assigned to it will be revisited and
    given a new value, a lower one. Then its neighbors will be revisited, to see if they're
    candidates for having their query values lowered. Think of a flood-fill in progress.

    More intuitive but slower solution:
    Assign query values to lowest-height squares first, by breadth-first "flooding". Then
    get the ones that fit the next query up. And so on.

    Note the use of a logarithmic "phone book" search to find the best query for a given
    height value.
    """

    debug = False
    print_pad = 1
    show_indices = False

    OUT_OF_REACH_QUERY = 999999

    def maxPoints(self, grid: List[List[int]], queries: List[int]) -> List[int]:

        # Want to map back to original unsorted list
        queries_sorted: List[Tuple[int, int]] = [(q, i) for i, q in enumerate(queries)]
        queries_sorted.sort(key=lambda x: x[0])

        if self.debug:
            self.base_query_grid = []
            for y, row in enumerate(grid):
                query_row = []
                for x, h in enumerate(row):
                    q_val = self.get_query_above(h, queries_sorted)
                    query_row.append(q_val)
                self.base_query_grid.append(query_row)

            self.query_to_index_map = {}
            for idx, q in enumerate(queries_sorted):
                if self.query_to_index_map.get(q[0], 0) == 0:
                    self.query_to_index_map[q[0]] = idx
            self.query_to_index_map[self.OUT_OF_REACH_QUERY] = -1

        # Which query can reach this square? -1 for none set yet
        marked_for = [[-1] * len(row) for row in grid]
        to_visit = ToVisitArray(len(grid), len(grid[0]), (-1, -1))
        to_visit.add((0, 0))

        def get_neighbors(_x: int, _y: int) -> List[Tuple[int, int]]:
            """
            Return list of neighbors (each given as x,y coordinate) that are marked with a query
            value.
            """
            coords = [(_x, _y-1), (_x-1, y), (_x+1, y), (_x, _y+1)]
            results = []
            for cx, cy in coords:
                if cx < 0 or cy < 0 or cx >= len(grid[0]) or cy >= len(grid):
                    continue
                if -1 < marked_for[cy][cx]:
                    results.append((cx, cy))
            return results

        def get_neighbors_needing_visit(_x: int, _y: int) -> List[Tuple[int, int]]:
            """
            Return list of neighbors that a) haven't been visited yet or b) might need a new
            query value.
            """
            q_val = marked_for[_y][_x]
            coords = [(_x, _y-1), (_x-1, y), (_x+1, y), (_x, _y+1)]
            results = []
            for cx, cy in coords:
                if cx < 0 or cy < 0 or cx >= len(grid[0]) or cy >= len(grid):
                    continue
                if marked_for[cy][cx] == -1 or marked_for[cy][cx] > q_val:
                    # Want either:
                    # -- an unvisited neighbor
                    # -- one whose query category is higher than that of cell (_x, _y)
                    results.append((cx, cy))
            return results

        def show_info():
            if not self.debug:
                return
            self.print(f"\nQueries sorted: {queries_sorted}")
            self.print("\nGrid")
            self.print_map(grid)
            self.print("\nMarkings")
            self.print_marked_for(marked_for, to_visit)
            to_visit_items = to_visit.get_items()
            self.print(f"\nTo visit: {to_visit_items}")

        i = 0
        while to_visit.size() > 0:
            visit_coord = to_visit.get_next()
            x, y = visit_coord[0], visit_coord[1]
            h = grid[y][x]
            q_val = marked_for[y][x]
            did_marking = False
            find_own_query = False
            neighbors = get_neighbors(x, y)
            if len(neighbors) > 0:
                # Among all neighbors with a known best query that fits this height, find the one with
                # the lowest. If it's too low for the height of this square, then calculate this
                # square's query.
                find_own_query = True
                best_query = self.OUT_OF_REACH_QUERY
                for nx, ny in neighbors:
                    nq = marked_for[ny][nx]
                    if nq < best_query:
                        best_query = nq
                if best_query > h:
                    marked_for[y][x] = best_query
                    #dumb_idx = self.query_to_index_map[best_query]
                    #self.print(f"**** ({x}, {y}) marked from neighbor to {best_query}, idx = {dumb_idx}")
                    did_marking = True
                    find_own_query = False

            if find_own_query or marked_for[y][x] == -1:
                # No best query from neighbors, figure one out based on square's own height.
                q_val = self.get_query_above(h, queries_sorted)
                marked_for[y][x] = q_val
                #self.print(f"**** ({x}, {y}) marked fresh to {q_val}")
                did_marking = True

            if did_marking:
                neighbors = get_neighbors_needing_visit(x, y)
                for n in neighbors:
                    to_visit.add(n)

            i += 1

            show_info()

        results = [-1] * len(queries_sorted)

        show_info()

        score_map = {}
        for y, row in enumerate(marked_for):
            for x, q_val in enumerate(row):
                score_map[q_val] = score_map.get(q_val, 0) + 1
        if self.debug:
            self.print(f"**** score map is: {score_map}")
            self.print(f"**** query to idx is: {self.query_to_index_map}")

        last_val = -1
        summed_scores = 0
        sorted_results = []
        for q_val, orig_idx in queries_sorted:
            if q_val == last_val:
                results[orig_idx] = score_map[q_val]
                continue
            score_map[q_val] = score_map.get(q_val, 0) + summed_scores
            summed_scores = score_map[q_val]
            last_val = q_val
            results[orig_idx] = score_map[q_val]
            sorted_results.append(score_map[q_val])

        self.print(f"Sorted results: {sorted_results}")
        self.print(f"Final results: {results}")
        return results

    def get_query_above(self, val: int, queries_sorted: List[Tuple[int, int]], start_idx: int = 0, end_idx: int = -1):
        if end_idx == -1:
            end_idx = len(queries_sorted)
        if queries_sorted[start_idx][0] > val:
            return queries_sorted[start_idx][0]
        if queries_sorted[end_idx - 1][0] <= val:
            return self.OUT_OF_REACH_QUERY
        # 0-1, mid is -1; 0-2, mid is 0; 0-3, mid is 0
        mid_idx = (start_idx + end_idx) // 2 - 1
        if queries_sorted[mid_idx][0] > val:
            return self.get_query_above(val, queries_sorted, start_idx, mid_idx + 1)
        else:
            return self.get_query_above(val, queries_sorted, mid_idx + 1, end_idx)

    def print_map(self, grid):
        if not self.debug:
            return
        out_str = "       "
        for x, val in enumerate(grid[0]):
            out_str += f"{x:{self.print_pad}}  "
        print(out_str)
        print()
        for y, row in enumerate(grid):
            out_str = f"{y:{4}}:  "
            for x, val in enumerate(row):
                if self.show_indices:
                    h = self.base_query_grid[y][x]
                    idx = self.query_to_index_map[h]
                    out_str += f"{idx:{self.print_pad}}  "
                else:
                    out_str += f"{val:{self.print_pad}}  "
            print(out_str)

    def print_marked_for(self, marked_for, to_visit: ToVisitArray):
        if not self.debug:
            return
        out_str = "      "
        for x, val in enumerate(marked_for[0]):
            out_str += f"{x:{self.print_pad}}  "
        print(out_str)
        print()

        to_visit_grid = to_visit.to_visit_grid

        spaces_str = "".join([" "] * self.print_pad)
        for y, row in enumerate(marked_for):
            out_str = f"{y:{4}}: "
            for x, val in enumerate(row):
                plus_str = "+" if to_visit_grid[y][x] else " "
                if val == -1:
                    out_str += f"{spaces_str}{plus_str} "
                else:
                    if self.show_indices:
                        idx = self.query_to_index_map[val]
                        out_str += f"{idx:{self.print_pad}}{plus_str} "
                    else:
                        out_str += f"{val:{self.print_pad}}{plus_str} "
            print(out_str)

    def print(self, s: str = ""):
        if self.debug:
            print(s)

Solution.debug = True
#grid = [[1,2,3],[2,5,7],[3,5,1]]
#queries = [5,6,2]
grid = [[420766,806051,922751],[181527,815280,904568],[952102,4037,140319],[324081,17907,799523],[176688,90257,83661],[932477,621193,623068],[135839,554701,511427],[227575,450848,178065],[785644,204668,835141],[313774,167359,501496],[641317,620688,74989],[324499,122376,270369],[2121,887154,848859],[456704,7763,662087],[286827,145349,468865],[277137,858176,725551],[106131,93684,576512],[372563,944355,497187],[884187,600892,268120],[576578,515031,807686]]
queries = [352655,586228,169685,541073,584647,413832,576537,616413]
#grid = [[249472,735471,144880,992181,760916,920551,898524,37043,422852,194509,714395,325171],[295872,922051,900801,634980,644237,912433,857189,98466,725226,984534,370121,399006],[618420,573065,587011,298153,694872,12760,880413,593508,474772,291113,852444,77998],[67650,426517,146447,190319,379151,184754,479219,106819,138473,865661,799297,228827],[390392,789371,772048,730506,7144,862164,650590,21524,879440,396198,408897,851020],[932044,662093,436861,246956,128943,167432,267483,148325,458128,418348,900594,831373],[742255,795191,598857,441846,243888,777685,313717,560586,257220,488025,846817,554722],[252507,621902,87704,599753,651175,305330,620166,631193,385405,183376,432598,706692],[984416,996917,586571,324595,784565,300514,101313,685863,703194,729430,732044,349877],[155629,290992,539879,173659,989930,373725,701670,992137,893024,455455,454886,559081],[252809,641084,632837,764260,68790,732601,349257,208701,613650,429049,983008,76324],[918085,126894,909148,194638,915416,225708,184408,462852,40392,964501,436864,785076],[875475,442333,111818,494972,486734,901577,46210,326422,603800,176902,315208,225178],[171174,458473,744971,872087,680060,95371,806370,322605,349331,736473,306720,556064],[207705,587869,129465,543368,840821,977451,399877,486877,327390,8865,605705,481076]]
#queries = [690474,796832,913701,939418,46696,266869,150594,948153,718874]
#grid = [[914034,453318,890358,66464,241824,627609,751672,3912,103879,964103,172337,537700,809750,275447,91344,685368,16087,990389,51724],[350247,478851,13956,913855,293160,942030,770604,324424,154269,835737,211748,987927,688311,997190,487291,192031,413002,435462,279037],[552593,823760,17368,568756,381899,930515,845801,432960,82668,841376,502318,1909,821953,908124,627205,257411,589411,975764,889588],[433381,868134,490460,91910,444695,863882,817711,634045,503807,832083,161667,332238,985188,626271,436465,547822,496397,76856,343221],[998983,638696,424820,737770,266084,421332,628369,840131,537735,655740,136120,399678,912817,281988,715782,928750,450941,176733,695928],[728755,172254,47126,663092,987180,56539,218891,621936,148209,565803,370194,52199,990490,506329,538206,567695,496913,273669,492475],[493042,126959,198821,263231,381322,556191,615496,95912,302544,849586,230339,319564,869485,834730,187691,898921,738916,671293,627115],[84418,398842,197682,766763,965351,403719,111730,171727,629212,390838,702378,925433,715539,715192,716329,618440,910391,45543,934154],[85864,895798,613952,964678,476819,51177,951630,326303,10242,704918,327628,639624,583231,36668,164793,196632,362138,627905,60738]]
#queries = [262126,926187,453990,484163,969204,390494,280282,926270,697383,471169,264992,424922,979974,165804,138645,491024,250399]
Solution.print_pad = 6
Solution.show_indices = True
Solution().maxPoints(grid, queries)