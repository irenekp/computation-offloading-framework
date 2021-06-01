from diceLibrary.settings import ProfilerEnum, RunTime, BatteryStats, CPUStats, NetworkStats
from datetime import datetime
import speedtest
import psutil

class Profiler:
    _energyEnabled: bool
    _networkEnabled: bool
    _runtimeEnabled: bool
    _cpuEnabled: bool
    runTime: RunTime
    batteryStats: BatteryStats
    networkStats: NetworkStats
    cpu: CPUStats

    def __init__(self, settings):
        self._energyEnabled=False
        self._networkEnabled=False
        self._runtimeEnabled=False
        self._cpuEnabled=False
        if not len(settings):
            #DICEY
            pass
        else:
            for setting in settings:
                if setting==ProfilerEnum.ENERGY:
                    self._energyEnabled=True
                    self.batteryStats=BatteryStats()
                elif setting==ProfilerEnum.NETWORK:
                    self._networkEnabled=True
                    self.networkStats=NetworkStats()
                elif setting==ProfilerEnum.RUNTIME:
                    self._runtimeEnabled=True
                    self.runTime=RunTime()
                elif setting==ProfilerEnum.CPU:
                    self._cpuEnabled= True
                    self.cpu=CPUStats()
                else:
                    #DICEY
                    pass

    def getBatteryTime(self, start=True):
        if not hasattr(psutil, "sensors_battery"):
            #DICEY - Platform not supported
            pass
        else:
            batt = psutil.sensors_battery()
            if batt is None:
                #DICEY - no battery found
                pass
            else:
                if start:
                    self.batteryStats.startBatteryCharge=batt.percent
                else:
                    self.batteryStats.endBatteryCharge=batt.percent
                if batt.power_plugged:
                    #DICEY - disabling energy
                    self._energyEnabled=False
                else:
                    if start:
                        self.batteryStats.startBatteryTime=batt.secsleft
                    else:
                        self.batteryStats.endBatteryTime=batt.secsleft

    def profileNetwork(self):
        threads = 1
        s = speedtest.Speedtest()
        s.download(threads=threads)
        s.upload(threads=threads)
        res = s.results.dict()
        self.networkStats.upload=res['upload']
        self.networkStats.download=res['download']
        self.networkStats.ping=res['ping']
        self.networkStats.latency=res['server']['latency']

    def startProfile(self):
        if self._runtimeEnabled:
            self.runTime.startTime=datetime.now()
        if self._energyEnabled:
            self.getBatteryTime(start=True)
        if self._networkEnabled:
            self.profileNetwork()
        if self._cpuEnabled:
            self.cpu.startStats=psutil.cpu_times()

    def closeProfile(self):
        if self._runtimeEnabled:
            self.runTime.endTime=datetime.now()
            time_diff = (self.runTime.endTime - self.runTime.startTime)
            self.runTime.runtime = time_diff.total_seconds()
        if self._energyEnabled:
            self.getBatteryTime(start=False)
            self.batteryStats.consumedBatteryTime=self.batteryStats.endBatteryTime-self.batteryStats.startBatteryTime-self.runTime.runtime
        if self._networkEnabled:
            pass
        if self._cpuEnabled:
            self.cpu.endStats=psutil.cpu_times()
            self.cpu.calculateDifference()
    def printProfiles(self):
        print(self.runTime)
        print(self.batteryStats)
        print(self.networkStats)
        print(self.cpu)


    