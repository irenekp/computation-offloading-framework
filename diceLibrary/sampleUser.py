from diceLibrary.diceConfig import DiceConfig
from diceLibrary.settings import ProfilerConfig, DecisionEngineConfig, LoggerConfig, AnalyticsConfig, InputType
from diceLibrary.dice import Dice
from itertools import permutations
from diceLibrary.dice import offloadable
from diceLibrary.dispatcher import Dispatcher


x = DiceConfig()
x.setProfilerConfig([ProfilerConfig.ENERGY, ProfilerConfig.RUNTIME, ProfilerConfig.CPU, ProfilerConfig.NETWORK])
x.setDecisionEngineConfig([DecisionEngineConfig.CASCADE])
#x.setAnalyticsConfig([AnalyticsConfig.CURRENTRUN, AnalyticsConfig.SUMMARYANALYTICS])
x.setLoggerConfig([LoggerConfig.DOWNLOAD])
dice = Dice(x)
serverLink="http://ec2-18-219-235-10.us-east-2.compute.amazonaws.com:8080/getNQueens"
metaData={'n':InputType.VALUE}
dispatcher1=Dispatcher(serverLink, metaData=metaData)
@offloadable(dice=dice, dispatcher=dispatcher1)
def myFunc(n):
    n = int(n)
    cols = range(n)
    for vec in permutations(cols):
        if n == len(set(vec[i] + i for i in cols)) \
                == len(set(vec[i] - i for i in cols)):
            print(vec)


if __name__ == "__main__":
    dice.train(myFunc, [(6, ),(7,),(8,),(9,),(10,),(11,)])
    myFunc(11)
