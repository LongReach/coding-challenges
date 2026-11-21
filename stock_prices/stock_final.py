from typing import List, Tuple, Optional
from copy import copy

class Solution:

    """
    Problem:
    https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/
    Difficulty: hard
    Solved: yes

    Insight:

    On each day, we either open a position, do nothing, or close a position.

    Dynamic programming. Start at end, work backwards. For each day record:
    - Best profit if we enter position now, with total of zero positions left before end (impossible)
    - Best profit if we enter position now, with total of one position left before end
    - Best profit if we enter position now, with total of two positions left before end
    - Best profit if we don't enter position here, with total of zero positions left before end (always zero)
    - Best profit if we don't enter position here, with total of one position left before end
    - Best profit if we don't enter position here, with total of two positions left before end

    When entering a position at i, we look to T[i+1][p][1], moving the entry point back by one.
    Then we look to T[i+1][p-1][0], as though we are entering and immediately exiting
    Then we look to T[i+1][p-1][0], as though we are entering and exiting at i+1
    When not entering a position now, we look to T[i+1][p][1]
    Then to T[i+1][p][0]

    (T is short for profit_table, p is positions lefts)
    """

    GIANT_NUMBER = 1000000000
    debug = False

    def maxProfit(self, prices: List[int]) -> int:

        num_entries = len((prices))
        profit_table = [[[-self.GIANT_NUMBER, -self.GIANT_NUMBER] for i in range(3)] for j in range(num_entries)]
        profit_table[num_entries-1][1][1] = 0
        profit_table[num_entries-1][0][0] = 0

        for i in range(num_entries-2, -1, -1):
            for starts_here in range(2):
                for total_trades in range(3):
                    if starts_here == 0:
                        # Table entry for not entering a position here
                        profit = max(profit_table[i+1][total_trades][1], profit_table[i+1][total_trades][0])
                    elif total_trades > 0:
                        # Table entry for entering a position here
                        profit = max(profit_table[i+1][total_trades][1] + prices[i+1] - prices[i], profit_table[i+1][total_trades-1][0], profit_table[i+1][total_trades-1][0] + prices[i+1] - prices[i])
                    else:
                        # Not possible to enter a position under with no trades left
                        profit = -self.GIANT_NUMBER
                    profit_table[i][total_trades][starts_here] = profit

        if self.debug:
            self.print(f"Prices are: {', '.join([str(p) for p in prices])}")
            for total_trades in range(3):
                for starts_here in range(2):
                    print_list = [profit_table[i][total_trades][starts_here] for i in range(num_entries)]
                    print_list = [str(item) if item >= 0 else "_" for item in print_list]
                    print_list = ", ".join(print_list)
                    self.print(f"Total trades {total_trades}, enter here {starts_here}: {print_list}")

        return max(profit_table[0][2][0], profit_table[0][2][1], profit_table[0][1][0], profit_table[0][1][1])

    def print(self, s: str = ""):
        if self.debug:
            print(s)

"""
Prices are: 2, 1, 2, 0, 1
Total trades 0, enter here 0: 0, 0, 0, 0, 0
Total trades 0, enter here 1: _, _, _, _, _
Total trades 1, enter here 0: 1, 1, 1, 0, _
Total trades 1, enter here 1: 0, 1, 0, 1, 0
Total trades 2, enter here 0: 1, 0, _, _, _
Total trades 2, enter here 1: 1, 1, 0, _, _

Should be:
Total trades 2, enter here 1: 1, 2, 0, _, _

Look at T[2][1][0]
"""

Solution.debug = True
#prices = [3,3,5,0,0,3,1,4]
#prices = [1,2,3,4,5]
#prices = [7, 6, 4, 3, 1]
#prices = [6,1,3,2,4,7]
prices=[2,1,2,0,1]
Solution().maxProfit(prices)