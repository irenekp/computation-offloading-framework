from diceLibrary.profiler import Profiler

class Dice:
    profiler=None
    def __init__(self, config):
        self.profiler=Profiler(config.getProfiler())
    @staticmethod
    def offloadable(*args, **kwargs):
        def intermediateOffloadable(func):
            def runOffloadable(*args2, **kwargs2):
                dice=kwargs['dice']
                dice.profiler.startProfile()
                func(*args2, **kwargs2)
                dice.profiler.closeProfile()
                dice.profiler.printProfiles()
            return runOffloadable
        return intermediateOffloadable


if __name__=='__main__':
    pass