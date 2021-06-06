from datetime import datetime
import logging
class Trainer:
    log=None
    def __init__(self):
        self.log=logging.getLogger()

    def train(self,func, n:int, inputs: list):
        if n<len(inputs):
            self.log.error("The number of inputs is insufficient")
            raise Exception("Insufficient input to trainer")
        start=datetime.now()
        for i in range(0,n):
            func(inputs[i])
        end=datetime.now()
        self.log.info("Training Complete. Training took: "+str((start-end).seconds)+" seconds.")

