import sqlite3
import pandas as pd
import logging
from datetime import datetime

class cascadeDatabase:
    dbName='dice.db'
    tableName='cascadeAnalytics'
    trainTableName='cascadeTrain'
    log=None
    def __init__(self,dbName='dice.db'):
        self.dbName=dbName
        self.log=logging.getLogger()
        self.createTableIfNotExists()

    def toList(self, s: str):
        return s.split(',')

    def fromList(self, ls:list):
        ls=[str(x) for x in ls]
        return ','.join(ls)

    def createTableIfNotExists(self):
        conn = sqlite3.connect(self.dbName)
        conn.execute('''
        create table if not exists {} (
        runId varchar(255) NOT NULL,
        functionName varchar(255) NOT NULL,
        inputTypes varchar(255),
        inputValues varchar(255),
        offloadStatus BIT NOT NULL,
        dataSize FLOAT,
        runTime FLOAT,
        batteryStartTime FLOAT,
        batteryTime FLOAT,
        latency FLOAT,
        upload FLOAT,
        download FLOAT,
        ping FLOAT,
        userCPU FLOAT,
        systemCPU FLOAT,
        idleCPU FLOAT,
        training BOOL,
        PRIMARY KEY (runId)
        )
        '''.format(self.tableName))
        self.log.info("Created Table: "+self.tableName)
        conn.execute('''
        create table if not exists {} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        functionName varchar(255) NOT NULL,
        inputTypes varchar(255),
        inputValues varchar(255),
        offload BIT NOT NULL,
        dataSize FLOAT,
        batteryStartTime FLOAT,
        upload FLOAT,
        download FLOAT
        )
        '''.format(self.trainTableName))
        conn.close()

    def formatMetaData(self, values, metaData):
        ipVal=list()
        ipTypes=list()
        for key in values.keys():
            ipVal.append(values[key])
            ipTypes.append(metaData.get(key,None).value)
        return self.fromList(ipVal), self.fromList(ipTypes)

    def addCascadeEntry(self, func,values,metaData,offloaded,dataSize,runT,batteryS,batteryT,latency,ping,upload,download,user,sys,idle, training):
        id=datetime.now().strftime('%m/%d/%YT%H:%M:%S.%f')
        conn = sqlite3.connect(self.dbName)
        if offloaded:
            offloaded=1
        else:
            offloaded=0
        ipValues,ipTypes=self.formatMetaData(values,metaData)
        conn.execute('''
        INSERT INTO {} VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        '''.format(self.tableName),(id,func,ipTypes,ipValues,offloaded,dataSize,runT,batteryS,batteryT,latency,ping,upload,download,user,sys,idle, training))
        self.log.info('Profiled data input into table')
        conn.commit()
        conn.close()
        return id

    def addTrainingEntry(self, func, ipTypes, ipValues, offload, dataSize, batteryStartTime, upload, download):
        conn = sqlite3.connect(self.dbName)
        conn.execute('''
        INSERT INTO {} (functionName,inputTypes, inputValues, offload, dataSize, batteryStartTime, upload, download) VALUES (?,?,?,?,?,?,?,?)'''.format(self.trainTableName),\
                     (func, ipTypes, ipValues, offload, dataSize, batteryStartTime, upload, download))
        conn.commit()
        conn.close()

    def getCascadeData(self, train=False):
        conn = sqlite3.connect(self.dbName)
        tableName=self.trainTableName if train else self.tableName
        df = pd.read_sql_query("SELECT * FROM "+tableName, conn)
        return df


if __name__ == '__main__':
    dB=cascadeDatabase()
    data=dB.getCascadeData()
    data=dB.getCascadeData(train=True)
    print('end')