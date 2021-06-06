import sqlite3
import pandas as pd
from datetime import datetime

class cascadeDatabase:
    dbName='pythonsqlite.db'
    tableName='cascadeHistory'
    def __init__(self,dbName='pythonsqlite.db'):
        self.dbName=dbName
        self.createTableIfNotExists()

    def createTableIfNotExists(self):
        conn = sqlite3.connect(self.dbName)
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
        '''.format(self.tableName))
        print('table created')
        conn.close()

    def addCascadeEntry(self, func,offloaded,dataSize,runT,batteryT,latency,ping,upload,download,user,sys,idle):
        id=datetime.now().strftime('%m/%d/%YT%H:%M:%S')
        conn = sqlite3.connect(self.dbName)
        if offloaded:
            offloaded=1
        else:
            offloaded=0
        conn.execute('''
        INSERT INTO {} VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        '''.format(self.tableName),(id,func,offloaded,dataSize,runT,batteryT,latency,ping,upload,download,user,sys,idle))
        print('entry added to dB')
        conn.commit()
        conn.close()
        return id

    def getCascadeData(self):
        conn = sqlite3.connect(self.dbName)
        df = pd.read_sql_query("SELECT * FROM "+self.tableName, conn)
        return df

if __name__ == '__main__':
    dB=cascadeDatabase('pythonsqlite.db')
    #dB.createTableIfNotExists()
    #dB.addCascadeEntry('func1',False,28,29,34,45,46,56,34,6,7,8,9,10)
    dB.getCascadeData()
    print("end")
