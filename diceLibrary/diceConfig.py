from diceLibrary.settings import ProfilerConfig, DecisionEngineConfig, LoggerConfig
import logging
class DiceConfig:
    _profiler: list
    _decisionEngine: list
    _analytics: bool
    _logger: list
    _loggerEnabled: bool = False
    log=None
    def __init__(self):
        self.log=logging.getLogger()
    def setProfilerConfig(self,settings: list):
        if not settings or not len(settings):
            self.log.warning('No Profiles Chosen - Profiler Disabled')
        else:
            settingList=list()
            for setting in settings:
                if not ProfilerConfig.has_value(setting.value):
                    self.log.error('Erroneous profiler setting detected - ignored')
                else:
                    settingList.append(setting)
            self._profiler=settingList

    def getProfilerConfig(self):
        return self._profiler

    def setDecisionEngineConfig(self,settings: list):
        if not len(settings):
            self.log.warning('No Decision Engine Chosen - Decision Engine Disabled')
            pass
        else:
            settingList=list()
            for setting in settings:
                if not DecisionEngineConfig.has_value(setting.value):
                    self.log.error('Erroneous decision engine setting detected - ignored')
                else:
                    settingList.append(setting)
            self._decisionEngine=settingList

    def getDecisionEngineConfig(self):
        return self._decisionEngine

    def enableAnalytics(self,setting: bool):
        print('analytics'+str(setting))
        self._analytics=setting

    def getAnalyticSetting(self):
        return self._analytics

    def setLoggerConfig(self, settings: list):
        if not settings or not len(settings):
            self.log.warning('Logger Disabled')
        else:
            self._loggerEnabled=True
            settingList=list()
            for setting in settings:
                if not LoggerConfig.has_value(setting.value):
                    self.log.error('Erroneous logger setting detected - ignored')
                else:
                    settingList.append(setting)
            self._logger=settingList

    def getLoggerConfig(self):
        return self._logger

    def isLoggerEnabled(self):
        return self._loggerEnabled

if __name__=='__main__':
    pass