import os
from diceLibrary.diceConfig import DiceConfig
from diceLibrary.settings import ProfilerConfig, DecisionEngineConfig, LoggerConfig, AnalyticsConfig, InputType
from diceLibrary.dice import Dice
from itertools import permutations
from diceLibrary.dice import offloadable
from diceLibrary.dispatcher import Dispatcher
import string
import numpy as np
import pandas as pd
import networkx as nx
import nltk
import string
import random
from nltk.corpus import stopwords
import re
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import timeit
import ml_func

from diceLibrary.trainer import Trainer

x = DiceConfig()
x.setProfilerConfig([ProfilerConfig.ENERGY, ProfilerConfig.RUNTIME, ProfilerConfig.CPU, ProfilerConfig.NETWORK])
x.setDecisionEngineConfig([DecisionEngineConfig.CASCADE])
x.setAnalyticsConfig([AnalyticsConfig.CURRENTRUN])
x.setLoggerConfig([LoggerConfig.DOWNLOAD])
dice = Dice(x)

serverLinkQueens="http://ec2-3-143-255-59.us-east-2.compute.amazonaws.com:8080/getNQueens"
queensMetadata={'n':InputType.VALUE}
dispatcher1=Dispatcher(serverLinkQueens, metaData=queensMetadata)
@offloadable(dice=dice, dispatcher=dispatcher1)
def nQueens(n):
    n = int(n)
    cols = range(n)
    for vec in permutations(cols):
        if n == len(set(vec[i] + i for i in cols)) \
                == len(set(vec[i] - i for i in cols)):
            print(vec)

serverLinkTOH="http://ec2-3-143-255-59.us-east-2.compute.amazonaws.com:8080/getTOH"
TOHmetaData={'n':InputType.VALUE, 'source':InputType.VALUE, 'auxiliary': InputType.VALUE, 'destination':InputType.VALUE}
dispatcher2=Dispatcher(serverLinkTOH, metaData=TOHmetaData)
@offloadable(dice=dice, dispatcher=dispatcher2)
def TOH(n, source, auxiliary, destination):
    if n == 1:
        print("Move disk 1 from source", source, "to destination", destination)
        return
    TOH(n - 1, source, auxiliary, destination)
    print("Move disk", n, "from source", source, "to destination", destination)
    TOH(n - 1, auxiliary, destination, source)

serverLinkBbl="http://ec2-3-143-255-59.us-east-2.compute.amazonaws.com:8080/getSort"
sortMetaData={'n':InputType.VALUE}
dispatcher3=Dispatcher(serverLinkBbl, metaData=sortMetaData)
@offloadable(dice=dice, dispatcher=dispatcher3)
def bubbleSort(n):
    sortList = list(range(n, 0, -1))
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            print(j)
            if sortList[j] > sortList[j + 1]:
                sortList[j], sortList[j + 1] = sortList[j + 1], sortList[j]
    print("Finished sorting")
    return "Finished sorting!"

    
serverLinkCompress="http://ec2-3-143-255-59.us-east-2.compute.amazonaws.com:8080/compressVideo"
compressMetaData = {'trial':InputType.FILE, 'compressedVideo':InputType.FILE}
dispatcher4=Dispatcher(urlEndpoint=serverLinkCompress, metaData=compressMetaData, inputFilePath="Trails/trial3.mp4", outputFilePath="Trails/compressedVideo.mp4")
@offloadable(dice=dice, dispatcher=dispatcher4)
def compress(inputFile, outputFile):
    os.system("ffmpeg -y -i " + inputFile + " -c:v libx264 -crf 25 -preset veryslow -pix_fmt yuv420p " + outputFile)
    return "FINISHED COMPRESSION"

serverLinkML="http://ec2-3-143-255-59.us-east-2.compute.amazonaws.com:8080/summarize"
mlMetaData = {'nyt':InputType.FILE}
dispatcher5=Dispatcher(urlEndpoint=serverLinkML, metaData=mlMetaData, inputFilePath="Trails/nyt.txt", outputFilePath="Trails/sum.txt")
@offloadable(dice=dice, dispatcher=dispatcher5)
def summarize(filename, outfile):
  ml_func.summarizerMain(filename, outfile)

if __name__ == "__main__":

    '''
    dice.train(bubbleSort, [(100,),(500,),(1000,),(100,),(500,),(1000,),(2000,),(5000,),(10000,),(7500,)])
    dice.train(nQueens, [(7,),(5,),(4,),(8,),(10,),(9,),(2,),(3,),(11,),(10,),(7,),(12,)])
    
    nQueens(10)
    nQueens(11)
    nQueens(4)
    nQueens(6)
    nQueens(9)
    nQueens(12)
    
    bubbleSort(10000)
    bubbleSort(5500)
    bubbleSort(14500)
    bubbleSort(100)
    bubbleSort(20)
    bubbleSort(10)
    '''

    #dice.train(compress, [("Trails/trial4.mp4", "Trails/compressedVideo.mp4", )])
    #compress("Trails/trial3.mp4", "Trails/outputVid.mp4")

    #dice.train(summarize, [("Trails/nyt.txt", "Trails/sum.txt")])
    print('end')
