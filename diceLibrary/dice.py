from diceLibrary.profiler import Profiler
from diceLibrary.Logger import Logger
class Dice:
    profiler=None
    log=None
    def __init__(self, config):
        self.log=Logger(config.getLoggerConfig())
        self.profiler=Profiler(config.getProfilerConfig(), self.log)

    @staticmethod
    def offloadable(*args, **kwargs):
        def intermediateOffloadable(func):
            def runOffloadable(*args2, **kwargs2):
                dice=kwargs.get('dice',None)
                if dice:
                    dice.log.info('Beginning profiling process')
                    dice.profiler.startProfile()
                    func(*args2, **kwargs2)
                    dice.profiler.closeProfile()
                else:
                    dice.log.error('Dice Instance Not Passed')
                    raise Exception('Dice Instance Not Passed')
            return runOffloadable
        return intermediateOffloadable


if __name__=='__main__':
    pass