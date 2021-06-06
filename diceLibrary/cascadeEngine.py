'''
Cascade Decision Engine - Core
*Not exposed to user*

Called at dice.py to decide whether @offloadable decorated methods will be executed remotely.

Two separate decision methods are being used.
1) If the user offloads a method with 'File' as input arg: we consider file size, runtime and energy in our decision-making.
2) If the user offloads a method with just 'JSON' as input arg: we consider only runtime and energy in our decision-making.
'''

import constants
import diceLibrary.cascadeDatabase as db
import sqlite3
import pandas as pd

class cascadeEngine:

    _userPriority: int

    def getClosestAsset(self, priority):
        if priority == constants.PRIORITY_RUNTIME:
            pass