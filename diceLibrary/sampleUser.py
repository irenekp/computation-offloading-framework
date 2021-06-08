from diceLibrary.diceConfig import DiceConfig
from diceLibrary.settings import ProfilerConfig, DecisionEngineConfig, LoggerConfig, AnalyticsConfig
from diceLibrary.dice import Dice
from itertools import permutations

x = DiceConfig()
x.setProfilerConfig([ProfilerConfig.ENERGY, ProfilerConfig.NETWORK, ProfilerConfig.RUNTIME, ProfilerConfig.CPU])
x.setDecisionEngineConfig([DecisionEngineConfig.CASCADE])
x.setAnalyticsConfig([AnalyticsConfig.CURRENTRUN, AnalyticsConfig.SUMMARYANALYTICS])
x.setLoggerConfig([LoggerConfig.DOWNLOAD])
dice = Dice(x)

@Dice.offloadable(dice=dice)
def myFunc(input):
    for i in range(0,10):
        n = int(input)
        cols = range(n)
        for vec in permutations(cols):
            if n == len(set(vec[i] + i for i in cols)) \
                    == len(set(vec[i] - i for i in cols)):
                print(vec)

if __name__ == "__main__":
    myFunc(5)
    dice.analyze()
