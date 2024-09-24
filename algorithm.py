# I decided to use merge sort for sorting since it has a time complexity
# of O(n * Log n) even as the data set increases, this means that it will
# not become less efficient - this complexity is the best, average and worst case.
class MergeSort:
    unsortedList1 = []
    unsortedList2 = []
    sortedList = []

    def __init__(self, unsortedList):
        self.unsortedList = unsortedList

    def sort(self):
        # split the unsorted list into two halves
        self.__divide()

        # sort the sublists
        sublistOneSorted, sublistTwoSorted = self.__conquer()

        # merge the two sublists together to output the final
        # sorted list
        sortedList = self.__merge(sublistOneSorted, sublistTwoSorted)

        print(sortedList)

    # split the unsorted list into two sublists
    def __divide(self):
        # checking to see if number of items in list is
        # divisible by 2, if so then it has an even number
        # of elements
        if (len(self.unsortedList) / 2) % 2 == 0:
            halfwayEndIndex = int(len(self.unsortedList) / 2)

        else:
            halfwayEndIndex = int((len(self.unsortedList) / 2) + 0.5)

        self.unsortedList1 = self.unsortedList[0:halfwayEndIndex]
        self.unsortedList2 = self.unsortedList[halfwayEndIndex:]

    def __conquer(self):
        sublistOneSorted = self.__sortSublist(1)

        sublistTwoSorted = self.__sortSublist(2)

        return sublistOneSorted, sublistTwoSorted

    # sorts the sublist and returns it to conquer method
    def __sortSublist(self, listNumber):
        # this is the list that is going to be returned at the
        # end
        finalList = []

        # making a copy of the list depending on which sublist
        # needs to be sorted
        if listNumber == 1:
            copyList = self.unsortedList1.copy()
        else:
            copyList = self.unsortedList2.copy()

        # if the copied list is not empty, this process will loop
        while copyList:

            # making the assumption that the first item is the shortest
            # time
            shortestTime = copyList[0]

            # going through the elements in the copied list to analyse which
            # is the shortest time
            for time in copyList:
                comparison = self.__comparingTimes(time, shortestTime)
                # updating the shortest time since the next element has a
                # shorter time
                if comparison == "time2":
                    shortestTime = time

            # adding the shortest time to the final list
            finalList.append(shortestTime)

            # removing the shortest time, so it is not duplicated inside
            # the final list
            copyList.remove(shortestTime)

        return finalList

    # merges the two sub-lists
    def __merge(self, sublistOne, sublistTwo):
        # this is the final list that is going to be returned
        finalList = []

        # when at least one of the sublists have one element
        # this block will process
        while sublistOne or sublistTwo:

            # there is a possibility that one of the sub-lists can become
            # empty before the other one, in this case, the sublist that
            # still has times should all be added to the end of the
            # finalList
            if sublistOne and not sublistTwo:
                for item in sublistOne:
                    finalList.append(item)
                    sublistOne.remove(item)
                break
            elif not sublistOne and sublistTwo:
                for item in sublistTwo:
                    finalList.append(item)
                    sublistTwo.remove(item)
                break

            output = self.__comparingTimes(sublistOne[0], sublistTwo[0])

            # if the two times are the same add them both to the finalList
            # and remove both of them from their respective sub-lists
            if output == "draw":
                finalList.append(sublistOne[0])
                finalList.append(sublistTwo[0])
                sublistOne.pop(0)
                sublistTwo.pop(0)
            # if the first sub-list has a greater time, add the second time
            # to the finalList and remove it from the second sub-list
            elif output == "time1":
                finalList.append(sublistTwo[0])
                sublistTwo.pop(0)
            # if the second sub-list has a greater time, add the first time
            # to the finalList and remove it from the first sub-list
            else:
                finalList.append(sublistOne[0])
                sublistOne.pop(0)

        return finalList

    # returns draw if the two times are equal
    # returns time1 if it is greater than time2
    # returns time2 if it is greater than time1
    def __comparingTimes(self, time1, time2):
        timeOneHour = int(time1[0:2])
        timeOneMinutes = int(time1[3:])

        timeTwoHour = int(time2[0:2])
        timeTwoMinutes = int(time2[3:])

        # Compare hour to see if there is an immediate difference
        if timeOneHour > timeTwoHour:
            return "time1"
        elif timeTwoHour > timeOneHour:
            return "time2"
        elif timeOneHour == timeTwoHour:
            # Compare minutes to see deduce which one is greater
            if timeTwoMinutes > timeOneMinutes:
                return "time2"
            elif timeOneMinutes > timeTwoMinutes:
                return "time1"
            else:
                return "draw"


# this is a test function to make sure that the algorithm works as
# expected
def test():
    unsortedEven = ["13:14", "03:15", "12:30", "14:05"]
    mergeSortEven = MergeSort(unsortedEven)
    mergeSortEven.sort()

    unsortedOdd= ["18:09", "10:47", "12:13", "14:48", "07:37"]
    mergeSortOdd = MergeSort(unsortedOdd)
    mergeSortOdd.sort()

    unsortedOne = ["12:02"]
    mergeSortOne = MergeSort(unsortedOne)
    mergeSortOne.sort()

    unsortedTwo = ["12:02", "04:12"]
    mergeSortTwo = MergeSort(unsortedTwo)
    mergeSortTwo.sort()