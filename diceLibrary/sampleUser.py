from diceLibrary.diceConfig import DiceConfig
from diceLibrary.settings import ProfilerEnum, DecisionEngineEnum
from diceLibrary.dice import Dice

x=DiceConfig()
x.setProfiler([ProfilerEnum.ENERGY, ProfilerEnum.NETWORK, ProfilerEnum.RUNTIME, ProfilerEnum.CPU])
x.setDecisionEngine([DecisionEngineEnum.CASCADE])
x.enableAnalytics(True)
x.enableLogger(True)
dice=Dice(x)
@Dice.offloadable(dice=dice)
def myFunc(input):
    print('my Func'+input)
myFunc('input')