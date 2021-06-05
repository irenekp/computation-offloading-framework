from diceLibrary.diceConfig import DiceConfig
from diceLibrary.settings import ProfilerConfig, DecisionEngineConfig, LoggerConfig
from diceLibrary.dice import Dice

x=DiceConfig()
x.setProfilerConfig([ProfilerConfig.ENERGY, ProfilerConfig.NETWORK, ProfilerConfig.RUNTIME, ProfilerConfig.CPU])
x.setDecisionEngineConfig([DecisionEngineConfig.CASCADE])
x.enableAnalytics(True)
x.setLoggerConfig([LoggerConfig.DOWNLOAD])
dice=Dice(x)

@Dice.offloadable(dice=dice)
def myFunc(input):
    print('my Func'+input)
myFunc('input')