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
    CASCADE =1
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