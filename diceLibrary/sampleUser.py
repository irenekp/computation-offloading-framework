from diceLibrary.diceConfig import DiceConfig
from diceLibrary.settings import ProfilerConfig, DecisionEngineConfig, LoggerConfig, AnalyticsConfig, InputType
from diceLibrary.dice import Dice
from itertools import permutations
from diceLibrary.dice import offloadable
from diceLibrary.dispatcher import Dispatcher


x = DiceConfig()
x.setProfilerConfig([ProfilerConfig.ENERGY, ProfilerConfig.RUNTIME, ProfilerConfig.CPU])
x.setDecisionEngineConfig([DecisionEngineConfig.CASCADE])
#x.setAnalyticsConfig([AnalyticsConfig.CURRENTRUN, AnalyticsConfig.SUMMARYANALYTICS])
x.setLoggerConfig([LoggerConfig.DOWNLOAD])
dice = Dice(x)
serverLink="http://ec2-18-219-235-10.us-east-2.compute.amazonaws.com:8080/getNQueens"
metaData={'input':InputType.VALUE,'input2':InputType.FILE}
inputFilePath='abc/ced'
outputFilePath='abc/ced'
metaData={'input':InputType.VALUE,'input2':InputType.FILE}
dispatcher1=Dispatcher(serverLink, inputFilePath=inputFilePath,outputFilePath=outputFilePath,metaData=metaData)
@offloadable(dice=dice, dispatcher=dispatcher1)
def myFunc(input, input2):
    '''
    for i in range(0,10):
        n = int(input)
        cols = range(n)
        for vec in permutations(cols):
            if n == len(set(vec[i] + i for i in cols)) \
                    == len(set(vec[i] - i for i in cols)):
                print(vec)
    '''
    print('func ',input, input2)


if __name__ == "__main__":
    dice.train(myFunc, [(1,1),(2,2),(3,3)])
    myFunc(4,5)
