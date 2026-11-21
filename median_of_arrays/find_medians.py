from typing import List, Optional
import statistics
from warnings import simplefilter


class Solution:

    """
    Problem: https://leetcode.com/problems/median-of-two-sorted-arrays/
    Difficulty: hard
    Solution successful: yes

    Solution insight (linear):

    Regardless of overlap, one list is to the left of the other. Start a pointer on the left side
    of left list and a pointer on right side of right list. The left pointer moves forward and
    the right pointer backwards until the right pointer no longer points to a bigger element than
    left one does.

    Solution insight (logarithmic):

    The goal is to find the master index for each element. Definition: what the index would be in the
    final combined list. For a given element in one list, we must find the first element that's the
    same or bigger in the other list. This can be done recursively, with a "phone book" search.
    Once we have that info, we can figure out the master index for a given element.
    """

    debug = True

    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        """
        Returns the median of two sorted arrays
        :param nums1: array 1
        :param nums2: array 2
        :return: value of median element from combined list
        """
        if not nums1:
            return self.get_median(nums2)
        if not nums2:
            return self.get_median(nums1)

        if self.debug:
            combined_list = nums1 + nums2
            combined_list.sort()
            self.print(f"Combining list {nums1} and {nums2} into {combined_list} of length {len(combined_list)}")
        else:
            combined_list = []

        combined_size = len(nums1) + len(nums2)
        if combined_size % 2 == 1:
            # The median element in combined list will have this master index
            desired_indices = [combined_size // 2]
        else:
            # The median element in combined list will have one of these two master indices
            desired_indices = [combined_size // 2 - 1, combined_size // 2]

        self.print(f"\nSearching list 1 for {desired_indices}")
        success_1, outputs_1 = self.search_list(nums1, nums2, desired_indices, 0, combined_list)

        self.print(f"\nSearching list 2 for {desired_indices}")
        success_2, outputs_2 = self.search_list(nums2, nums1, desired_indices, 1, combined_list)

        self.print(f"Indices in list 0 are {outputs_1}. Success: {success_1}. Element(s) is/are in {nums1}")
        self.print(f"Indices in list 1 are {outputs_2}. Success: {success_2}. Element(s) is/are in {nums2}")

        # The following logic accounts for the fact that a median value can be the average of two entries,
        # if the combined list is of an even length.
        total_value = 0
        count = 0
        for idx in outputs_1:
            total_value += nums1[idx]
            count += 1
        for idx in outputs_2:
            total_value += nums2[idx]
            count += 1

        return total_value / count

    def get_median(self, nums: List[int]) -> float:
        """Get value of median element in sorted list"""
        n = len(nums)
        if n % 2 == 1:
            # Element right in the middle
            return nums[int(n / 2)]
        else:
            # Elements straddling middle
            return (nums[int(n / 2) - 1] + nums[int(n / 2)]) / 2.0

    def search_list(self, list_a, list_b, desired_master_indices, which_list, combined_list) -> (bool, List[int]):
        """
        Efficiently search list_a to find an element whose master index matches one or more entries in
        desired_master_indices. list_b is used in the calculation of master index values.

        :param list_a: a sorted list of numbers
        :param list_b: another sorted list of numbers
        :param desired_master_indices: a list of one or two master indices. One item in this list will match the master index
            of an element from one of the two main number lists.
        :param which_list: 0 if list A is the first list of numbers, 1 if it's the second list
        :param combined_list: for debugging purposes only
        :return: (True if one or more master index matches were found, list of indices into list A (not master indices))
        """

        def move_pointer(_ptr: int, _range, _distance) -> (int, int):
            if _distance < 0:
                # Go to middle of adjusted range
                # 0 to 0: middle is -1; 0 to 1: middle is 0; 0 to 2: middle is 0
                _new_ptr = (_range[0] + _ptr - 1) // 2
                if _new_ptr < _range[0]:
                    _new_ptr = _range[0]
                _range = (_range[0], _ptr)
            else:
                # Go to middle of adjusted range
                # 0 to 0: middle is 0; 0 to 1: middle is 0; 0 to 2: middle is 1
                _new_ptr = (_ptr + _range[1]) // 2
                if _new_ptr >= _range[1]:
                    _new_ptr = _range[1] - 1
                _range = (_ptr + 1, _range[1])
            # 0 to 1: middle is -1; 0 to 2 middle is 1;
            #print(f"**** pointer from {_ptr} to {_new_ptr}, range to {_range}")
            return _new_ptr, _range

        ptr = 0 # index of selected item in list A
        range = (0, len(list_a))
        desired_master_indices_copy = []
        desired_master_indices_copy.extend(desired_master_indices)
        output_indices = []

        # This loop goes through list_a, in an efficient logarithmic manner, and tries to find a list A element
        # whose master index matches one of the desired master indices (if there's more than one)
        while desired_master_indices_copy:
            # Note:
            # For same valued-elements, if they come from list 2, they go AFTER same-valued elements from
            # list 1 in combined list.

            # Get pointer from other list. Want one as close to element from list A as possible
            # If True, list_a is list_2
            want_bigger_than = which_list == 1
            # other_ptr is index of item in list_b that's equal to or bigger than list_a[ptr]
            other_ptr = self.find_element_from_other_list(list_a[ptr], list_b, 0, len(list_b), want_bigger_than)
            # Calculate master index by factoring in all elements from list B that go left of selected element from
            # list A
            if other_ptr == -1:
                # List B is entirely to the left of element from list A
                master_idx = ptr + len(list_b)
            else:
                # Part of list B is entirely to the left of element from list A
                master_idx = ptr + other_ptr

            self.print(f"Master index for {list_a[ptr]} is {master_idx}, in list {which_list}. Ptr: {ptr}. Combined: {combined_list}")
            if master_idx in desired_master_indices_copy:
                self.print(f"Got it for list {which_list}!")
                output_indices.append(ptr)
                desired_master_indices_copy.remove(master_idx)
                continue

            if range[1] - range[0] <= 1:
                self.print("No more searching to do")
                break

            # Figure out which direction to try next
            distances = [desired_idx - master_idx for desired_idx in desired_master_indices_copy]
            best_distance = min(distances)

            # We want to shrink the search range
            direction_str = "left" if best_distance < 0 else "right"
            ptr, range = move_pointer(ptr, range, best_distance)
            inclusive_range = (range[0], range[1] - 1)
            self.print(
                f"Moved list {which_list} pointer {direction_str} to {ptr}. New range is {inclusive_range} (inclusive)")

        return len(output_indices) > 0, output_indices

    def find_element_from_other_list(self, val, nums: List[int], start_idx: int, end_idx: int, bigger_than: bool) -> int:
        """
        Given a list of numbers, find first entry whose value is equal to or larger than specified value, and
        return its index.

        This function calls itself recursively for logarithmic efficiency.

        :param val: the number to be searched for
        :param nums: list of numbers
        :param start_idx: index within nums at which to start search
        :param end_idx: index within nums at which to end search (non-inclusive)
        :param bigger_than: if True, the number found must be bigger than val
        :return: index of found entry, or -1 if not found
        """

        # end_idx is non-inclusive
        mid_idx = int((start_idx + end_idx) / 2)
        # self.print(f"**** searching for bigger than {val} in range from {start_idx} ({nums[start_idx]}) to {end_idx} (after {nums[end_idx-1]}), mid_idx is {mid_idx} ({nums[mid_idx]})")
        if start_idx == end_idx:
            return -1

        test_val = val + 1 if bigger_than else val

        if nums[start_idx] >= test_val:
            # Smallest item in the list is good enough
            return start_idx
        if nums[end_idx - 1] < test_val:
            # Biggest item in the list is smaller
            return -1
        if nums[mid_idx-1] >= test_val:
            # Desired item somewhere in first half of range
            return self.find_element_from_other_list(val, nums, start_idx, mid_idx, bigger_than)
        if nums[end_idx-1] >= test_val:
            # Desired item somewhere in second half of range
            return self.find_element_from_other_list(val, nums, mid_idx, end_idx, bigger_than)
        return -1

    def log_find(self, val, nums: List[int]):
        """Not used -- only served a purpose during development."""
        idx = self.find_element_from_other_list(val, nums, 0, len(nums))
        result = None if idx == -1 else nums[idx]
        self.print(f"log_find() got {result} as item bigger than {val} in {nums}")

    def simple_median(self, nums: List[int]) -> Optional[int]:
        """Not used -- only served a purpose during development."""
        if not nums:
            return None

        n = len(nums)
        if n % 1 == 1:
            # For 5 elements, that's 2, right in the middle
            median_idx = int(n / 2)
            median_val = nums[median_idx]
        else:
            # For 6 elements, we want to average elements 2 and 3
            right_idx = int(n / 2)
            left_idx = int(right_idx - 1)
            median_val = (nums[left_idx] + nums[right_idx]) / 2

        return median_val

    def brute_force(self, nums1: List[int], nums2: List[int]) -> float:
        """Not used -- only served a purpose during development."""
        combined_list = nums1 + nums2
        combined_list.sort()
        return statistics.median(combined_list)

    def print(self, s: str):
        if self.debug:
            print(s)


solver = Solution()
#solver.findMedianSortedArrays([1, 2, 4], [3, 7, 9])
#solver.findMedianSortedArrays([2, 2, 4, 4], [2, 2, 2, 4, 4])
#solver.findMedianSortedArrays([1, 2, 3, 4], [4, 5, 6, 7, 8])
#solver.findMedianSortedArrays([1, 2, 3, 7, 8, 9, 10], [4, 5, 6])
solver.findMedianSortedArrays([1, 2, 3, 7, 8,], [9, 11, 13])

#nums = [1, 2, 3, 4, 10, 11, 12, 13]
#nums = [1, 2, 2, 2, 4, 5, 6, 7, 7, 9, 9, 9, 9, 9, 10, 11, 12]
#solver.log_find(5, nums)