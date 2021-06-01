from diceLibrary.settings import ProfilerConfig, RunTime, BatteryStats, CPUStats, NetworkStats
from datetime import datetime
import speedtest
import psutil

class Profiler:
    _profilerEnabled: bool
    _energyEnabled: bool
    _networkEnabled: bool
    _runtimeEnabled: bool
    _cpuEnabled: bool
    runTime: RunTime
    batteryStats: BatteryStats
    networkStats: NetworkStats
    cpu: CPUStats
    log=None

    def __init__(self, settings, log):
        self._energyEnabled=False
        self._networkEnabled=False
        self._runtimeEnabled=False
        self._cpuEnabled=False
        self.log=log
        self._profilerEnabled=False
        if not len(settings):
            self.log.warning('No Profiles, Profiler Disabled')
        else:
            self._profilerEnabled=True
            for setting in settings:
                if setting==ProfilerConfig.ENERGY:
                    self._energyEnabled=True
                    self.batteryStats=BatteryStats()
                    self.log.info('Battery Statistics Enabled')
                elif setting==ProfilerConfig.NETWORK:
                    self._networkEnabled=True
                    self.networkStats=NetworkStats()
                    self.log.info('Network Statistics Enabled')
                elif setting==ProfilerConfig.RUNTIME:
                    self._runtimeEnabled=True
                    self.runTime=RunTime()
                    self.log.info('Runtime Statistics Enabled')
                elif setting==ProfilerConfig.CPU:
                    self._cpuEnabled= True
                    self.cpu=CPUStats()
                    self.log.info('CPU Statistics Enabled')
                else:
                    self.log.warning('Invalid profiler setting provided - ignored')
                    pass

    def getBatteryTime(self, start=True):
        if not hasattr(psutil, "sensors_battery"):
            self.log.error('Device does not support battery monitoring - disabled')
            self._energyEnabled=False
        else:
            batt = psutil.sensors_battery()
            if batt is None:
                self.log.error('Battery not found, monitoring disabled')
                self._energyEnabled=False
            else:
                if start:
                    self.batteryStats.startBatteryCharge=batt.percent
                    self.log.info('Battery Start Percentage:'+str(batt.percent))
                else:
                    self.batteryStats.endBatteryCharge=batt.percent
                    self.log.info('Battery End Percentage:'+str(batt.percent))
                if batt.power_plugged:
                    self.log.error('Battery charging, monitoring disabled')
                    self._energyEnabled=False
                else:
                    if start:
                        self.batteryStats.startBatteryTime=batt.secsleft
                        self.log.info('Battery Start Time Left:'+str(batt.secsleft))
                    else:
                        self.batteryStats.endBatteryTime=batt.secsleft
                        self.log.info('Battery End Time Left:'+str(batt.secsleft))

    def profileNetwork(self):
        try:
            threads = 1
            s = speedtest.Speedtest()
            s.download(threads=threads)
            s.upload(threads=threads)
            res = s.results.dict()
            self.networkStats.upload=res['upload']
            self.networkStats.download=res['download']
            self.networkStats.ping=res['ping']
            self.networkStats.latency=res['server']['latency']
            self.log.info('Network Stats: upload: '+str(res['upload'])\
                          +' download: '+str(res['download'])+' ping: '+str(res['ping'])+' latency: '+str(res['server']['latency']))
        except:
            self.log.error('Error in capturing network statistics - disabled')
            self._networkEnabled=False

    def startProfile(self):
        if self._networkEnabled:
            self.profileNetwork()
        if self._cpuEnabled:
            self.cpu.startStats=psutil.cpu_times()
            self.log.info('Cpu Stats At Start:'+str(self.cpu.startStats))
        if self._energyEnabled:
            self.getBatteryTime(start=True)
        if self._runtimeEnabled:
            self.runTime.startTime=datetime.now()
            self.log.info('Start Time:'+str(self.runTime.startTime))




    def closeProfile(self):
        if self._runtimeEnabled:
            self.runTime.endTime=datetime.now()
            time_diff = (self.runTime.endTime - self.runTime.startTime)
            self.runTime.runtime = time_diff.total_seconds()
            self.log.info('End of Runtime:'+str(self.runTime.endTime)+' Total Runtime: '+str(self.runTime.runtime))
        if self._energyEnabled:
            self.getBatteryTime(start=False)
            self.batteryStats.consumedBatteryTime=self.batteryStats.endBatteryTime-self.batteryStats.startBatteryTime
            self.log.info('Battery Time Consumed: '+str(self.batteryStats.consumedBatteryTime))
        if self._cpuEnabled:
            self.cpu.endStats=psutil.cpu_times()
            self.cpu.calculateDifference()
            self.log.info('Cpu Stats At End:'+str(self.cpu.endStats))
            self.log.info('Runtime Cpu Summary: user:'+str(self.cpu.user)+' system: '+str(self.cpu.system)+' idle: '+str(self.cpu.idle) \
                          +' interrupt: '+str(self.cpu.interrupt)+' dpc: '+str(self.cpu.dpc))
        if self._networkEnabled:
            pass


    