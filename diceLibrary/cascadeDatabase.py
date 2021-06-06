import sqlite3
import pandas as pd
import logging
from datetime import datetime

class cascadeDatabase:
    dbName='dice.db'
    tableName='cascadeAnalytics'
    trainTableName='cascadeTrain'
    _trainMode=False
    log=None
    def __init__(self,dbName='dice.db'):
        self.dbName=dbName
        self.log=logging.getLogger()
        self.createTableIfNotExists()

    def createTableIfNotExists(self):
        conn = sqlite3.connect(self.dbName)
        for tbName in [self.tableName,self.trainTableName]:
            conn.execute('''
            create table if not exists {} (
            runId varchar(255) NOT NULL,
            functionName varchar(255) NOT NULL,
            offloadStatus BIT NOT NULL,
            dataSize FLOAT,
            runTime FLOAT,
            batteryTime FLOAT,
            latency FLOAT,
            upload FLOAT,
            download FLOAT,
            ping FLOAT,
            userCPU FLOAT,
            systemCPU FLOAT,
            idleCPU FLOAT,
            PRIMARY KEY (runId)
            )
            '''.format(tbName))
            self.log.info("Created Table: "+tbName)
        conn.close()

    def addCascadeEntry(self, func,offloaded,dataSize,runT,batteryT,latency,ping,upload,download,user,sys,idle):
        id=datetime.now().strftime('%m/%d/%YT%H:%M:%S.%f')
        tableName=self.trainTableName if self._trainMode else self.tableName
        conn = sqlite3.connect(self.dbName)
        if offloaded:
            offloaded=1
        else:
            offloaded=0
        conn.execute('''
        INSERT INTO {} VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        '''.format(tableName),(id,func,offloaded,dataSize,runT,batteryT,latency,ping,upload,download,user,sys,idle))
        self.log.info('Profiled data input into table')
        conn.commit()
        conn.close()
        return id

    def getCascadeData(self):
        conn = sqlite3.connect(self.dbName)
        tableName=self.trainTableName if self._trainMode else self.tableName
        df = pd.read_sql_query("SELECT * FROM "+tableName, conn)
        return df

    def setTrainMode(self, trainMode=True):
        self._trainMode=trainMode
        self.log.info('Training mode set')

if __name__ == '__main__':
    dB=cascadeDatabase()
    dB.setTrainMode(True)
    data=dB.getCascadeData()
    data=dB.getCascadeData()
    print('end')