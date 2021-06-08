from datetime import datetime
import logging
class Trainer:
    log=None
    decisionEngine=None
    def __init__(self, decisionEngine):
        self.log=logging.getLogger()
        self.decisionEngine=decisionEngine

    def cascadeTrainer(self):
        pass

    def train(self,func, inputs: list):
        self.decisionEngine.setTrainMode(True)
        if len(inputs)<1:
            self.log.error("The number of inputs is insufficient")
            raise Exception("Insufficient input to trainer")
        self.decisionEngine.setOffload(False)
        start=datetime.now()
        for i in inputs:
            func(*i)
        end=datetime.now()
        self.log.info("Local Training Complete. Training took: "+str((start-end).seconds)+" seconds.")
        self.decisionEngine.setOffload(True)
        start=datetime.now()
        for i in inputs:
            func(*i)
        end=datetime.now()
        self.decisionEngine.setTrainMode(False)
        self.log.info("Remote Training Complete. Training took: "+str((start-end).seconds)+" seconds.")
