from diceLibrary.settings import ProfilerConfig, DecisionEngineConfig, LoggerConfig, AnalyticsConfig
import logging
class DiceConfig:
    _profiler: list
    _decisionEngine: list
    _analytics: list
    _logger: list
    _analyticsEnabled: bool = False
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

    def setAnalyticsConfig(self,settings:list):
        if not settings or not len(settings):
            self.log.warning('Analytics Disabled')
        else:
            self._analyticsEnabled=True
            settingList=list()
            for setting in settings:
                if not AnalyticsConfig.has_value(setting.value):
                    self.log.error('Erroneous analytics setting detected - ignored')
                else:
                    settingList.append(setting)
            self._analytics=settingList

    def getAnalyticSetting(self):
        return self._analytics

    def isAnalyticsEnabled(self):
        return self._analyticsEnabled

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