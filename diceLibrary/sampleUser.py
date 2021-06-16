import os
from diceLibrary.diceConfig import DiceConfig
from diceLibrary.settings import ProfilerConfig, DecisionEngineConfig, LoggerConfig, AnalyticsConfig, InputType
from diceLibrary.dice import Dice
from itertools import permutations
from diceLibrary.dice import offloadable
from diceLibrary.dispatcher import Dispatcher
from diceLibrary.trainer import Trainer

x = DiceConfig()
x.setProfilerConfig([ProfilerConfig.ENERGY, ProfilerConfig.RUNTIME, ProfilerConfig.CPU, ProfilerConfig.NETWORK])
x.setDecisionEngineConfig([DecisionEngineConfig.CASCADE])
#x.setAnalyticsConfig([AnalyticsConfig.CURRENTRUN, AnalyticsConfig.SUMMARYANALYTICS])
x.setLoggerConfig([LoggerConfig.DOWNLOAD])
dice = Dice(x)

serverLinkQueens="http://ec2-18-223-29-55.us-east-2.compute.amazonaws.com:8080/getNQueens"
metaData={'n':InputType.VALUE}
dispatcher1=Dispatcher(serverLinkQueens, metaData=metaData)
@offloadable(dice=dice, dispatcher=dispatcher1)
def nQueens(n):
    n = int(n)
    cols = range(n)
    for vec in permutations(cols):
        if n == len(set(vec[i] + i for i in cols)) \
                == len(set(vec[i] - i for i in cols)):
            print(vec)

serverLinkTOH="http://ec2-18-223-29-55.us-east-2.compute.amazonaws.com:8080/getTOH"
metaData={'n':InputType.VALUE, 'source':InputType.VALUE, 'auxiliary': InputType.VALUE, 'destination':InputType.VALUE}
dispatcher2=Dispatcher(serverLinkTOH, metaData=metaData)
@offloadable(dice=dice, dispatcher=dispatcher2)
def TOH(n, source, auxiliary, destination):
    if n == 1:
        print("Move disk 1 from source", source, "to destination", destination)
        return
    TOH(n - 1, source, auxiliary, destination)
    print("Move disk", n, "from source", source, "to destination", destination)
    TOH(n - 1, auxiliary, destination, source)

serverLinkBbl="http://ec2-18-223-29-55.us-east-2.compute.amazonaws.com:8080/getSort"
metaData={'n':InputType.VALUE}
dispatcher3=Dispatcher(serverLinkBbl, metaData=metaData)
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

def bub(n):
    sortList = list(range(n, 0, -1))
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            print(j)
            if sortList[j] > sortList[j + 1]:
                sortList[j], sortList[j + 1] = sortList[j + 1], sortList[j]
    return "Finished sorting!"
    
serverLinkCompress="http://ec2-18-223-29-55.us-east-2.compute.amazonaws.com:8080/compressVideo"
compressMetaData = {'trial':InputType.FILE, 'compressedVideo':InputType.FILE}
dispatcher4=Dispatcher(urlEndpoint=serverLinkCompress, metaData=metaData, inputFilePath="Trails/uploadedVideo.mp4", outputFilePath="Trails/compressedVideo.mp4")
@offloadable(dice=dice, dispatcher=dispatcher4)
def compress(inputFile, outputFile):
    os.system("ffmpeg -y -i " + inputFile + " -c:v libx264 -crf 25 -preset veryslow -pix_fmt yuv420p " + outputFile)
    return("FINISHED COMPRESSION")
    return "FINISHED COMPRESSION"


if __name__ == "__main__":
    #dice.train(nQueens, [(3,),(4,),(6,),(7,),(8,),(9,),(10,),(11,),(3,),(4,),(6,),(7,),(8,),(9,),(10,),(11,),(3,),(4,),(6,),(7,),(8,),(9,),(10,),(11,)])

    '''
    print("nQueens 10")
    nQueens(10)
    print("nQueens 5")
    nQueens(5)
    print("nQueens 8")
    nQueens(8)
    print("nQueens 9")
    nQueens(9)
    '''


    #dice.train(TOH, [(5,'A', 'B', 'C',),(10,'A', 'B', 'C',),(15,'A', 'B', 'C',),(5,'A', 'B', 'C',),(10,'A', 'B', 'C',),(8,'A', 'B', 'C',)])
    '''   
    print("TOH for 10")
    TOH(10, 'A', 'B', 'C')
    print("TOH for 15")
    TOH(15, 'A', 'B', 'C')
    print("TOH for 25")
    TOH(25, 'A', 'B', 'C')
    '''
    print("bubblesort 100")
    bubbleSort(100)
    print("Bubblesort 2250")
    bubbleSort(2250)
    print("bubblesort 5000")
    print("bubbleSort 10000")
    bubbleSort(10000)
    print("bubbleSort 500")
    bubbleSort(500)
    #dice.train(bubbleSort, [(100,),(500,),(1000,),(100,),(500,),(1000,),(2000,),(100,),(500,),(1000,),(100,),(500,),(1000,),(2000,),(2500,),(750,),(1000,),(3000,),(100,),(500,),(1000,),(2000,),(100,),(500,),(1000,),(2500,),(750,)])


    #dice.train(compress, [("Trails/trial.mp4", "Trails/compressedVideo.mp4", )])
    #compress("Trails/trial.mp4", "Trails/outputVid.mp4")
    print('end')
