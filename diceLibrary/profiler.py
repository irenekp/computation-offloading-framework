from diceLibrary.settings import ProfilerConfig, RunTime, BatteryStats, CPUStats, NetworkStats
from datetime import datetime
import speedtest
import psutil
import copy

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
    _networkStatsStore=dict()

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
                    self._energyEnabled = False
                else:
                    if start:
                        self.batteryStats.startBatteryTime=batt.secsleft
                        self.log.info('Battery Start Time Left:'+str(batt.secsleft))
                    else:
                        self.batteryStats.endBatteryTime=batt.secsleft
                        self.log.info('Battery End Time Left:'+str(batt.secsleft))

    def profileNetwork(self):
        if self._networkStatsStore.get('storedData',None)!=None:
            time=self._networkStatsStore['storedData']['time']
            diff=(datetime.now()-time).total_seconds()
            if diff<600:
                self.networkStats=copy.deepcopy(self._networkStatsStore['storedData']['data'])
                return
        try:
            threads = 1
            print(dir(speedtest))
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
            self._networkStatsStore['storedData']={'time':datetime.now(),'data':copy.deepcopy(self.networkStats)}
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
            self.batteryStats.consumedBatteryTime=self.batteryStats.startBatteryTime-self.batteryStats.endBatteryTime
            self.log.info('Battery Time Consumed: '+str(self.batteryStats.consumedBatteryTime))
        if self._cpuEnabled:
            self.cpu.endStats=psutil.cpu_times()
            self.cpu.calculateDifference()
            self.log.info('Cpu Stats At End:'+str(self.cpu.endStats))
        if self._networkEnabled:
            pass

    def getProfilerSummary(self):
        runT,batteryS,batteryT,latency,ping,upload,download,user,sys,idle=None, None, None, None, None,None, None, None, None,None
        if self._runtimeEnabled:
            runT=self.runTime.runtime
        if self._energyEnabled:
            batteryS=self.batteryStats.startBatteryTime
            batteryT=self.batteryStats.consumedBatteryTime
        if self._networkEnabled:
            ping=self.networkStats.ping
            upload=self.networkStats.upload
            download=self.networkStats.download
            latency=self.networkStats.latency
        if self._cpuEnabled:
            user=self.cpu.user
            sys=self.cpu.system
            idle=self.cpu.idle
        return runT,batteryS,batteryT,latency,ping,upload,download,user,sys,idle

    def getTrainingSummary(self):
        batteryS,upload,download=None, None, None
        if self._energyEnabled:
            batteryS = self.batteryStats.startBatteryTime
        if self._networkEnabled:
            upload = self.networkStats.upload
            download = self.networkStats.download
        return batteryS, upload, download

    def getUpdatedProfile(self):
        updatedConfig = []
        if self._runtimeEnabled:
            updatedConfig.append(ProfilerConfig.RUNTIME)
        if self._cpuEnabled:
            updatedConfig.append(ProfilerConfig.CPU)
        if self._networkEnabled:
            updatedConfig.append(ProfilerConfig.NETWORK)
        if self._energyEnabled:
            updatedConfig.append(ProfilerConfig.ENERGY)
        return updatedConfig