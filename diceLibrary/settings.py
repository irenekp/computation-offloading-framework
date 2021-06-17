from datetime import datetime
import enum
class ProfilerConfig(enum.Enum):
    ENERGY = 1
    NETWORK = 2
    RUNTIME = 3
    CPU = 4
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class DecisionEngineConfig(enum.Enum):
    CASCADE = 1
    LOGREG = 2
    DECTREE = 3
    SVM = 4
    RANDFRST = 5
    KNN = 6
    CASCALPHA = 7
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class LoggerConfig(enum.Enum):
    PERSISTLOG=1
    DOWNLOAD=2
    DISABLE=3
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class AnalyticsConfig(enum.Enum):
    CURRENTRUN=1
    SUMMARYANALYTICS=2
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class RunTime:
    startTime: datetime
    endTime: datetime
    runtime: float

class BatteryStats:
    startBatteryTime: int
    startBatteryCharge: float
    endBatteryTime: int
    endBatteryCharge: float
    consumedBatteryTime: float

class CPUStats:
    startStats=None
    endStats=None
    user: float
    system: float
    idle: float
    def calculateDifference(self):
        self.user=self.endStats.user-self.startStats.user
        self.system=self.endStats.system-self.startStats.system
        self.idle=self.endStats.idle-self.startStats.idle

class NetworkStats:
    latency: float
    ping: float
    upload: float
    download: float

class InputType(enum.Enum):
    VALUE =1
    FILE =2

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

#util function for old Cascade:
# Python3 program to find element
# closet to given target.

# Returns element closest to target in arr[]
def findClosest(arr, n, target):

    # Corner cases
    if (target <= arr[0]):
        return arr[0]
    if (target >= arr[n - 1]):
        return arr[n - 1]

    # Doing binary search
    i = 0; j = n; mid = 0
    while (i < j):
        mid = (i + j) // 2

        if (arr[mid] == target):
            return arr[mid]

        # If target is less than array
        # element, then search in left
        if (target < arr[mid]) :

            # If target is greater than previous
            # to mid, return closest of two
            if (mid > 0 and target > arr[mid - 1]):
                return getClosest(arr[mid - 1], arr[mid], target)

            # Repeat for left half
            j = mid

        # If target is greater than mid
        else :
            if (mid < n - 1 and target < arr[mid + 1]):
                return getClosest(arr[mid], arr[mid + 1], target)

            # update i
            i = mid + 1

    # Only single element left after search
    return arr[mid]


# Method to compare which one is the more close.
# We find the closest by taking the difference
# between the target and both values. It assumes
# that val2 is greater than val1 and target lies
# between these two.
def getClosest(val1, val2, target):

    if (target - val1 >= val2 - target):
        return val2
    else:
        return val1