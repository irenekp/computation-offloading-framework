from diceLibrary.settings import LoggerConfig
import logging
import sys

class Logger:
    logger=None
    def __init__(self, settings):
        if not settings or not len(settings):
            return
        self.logger=logging.getLogger()
        filemode='w'
        if LoggerConfig.PERSISTLOG in settings and LoggerConfig.DOWNLOAD in settings:
            filemode='a'
        if LoggerConfig.DOWNLOAD in settings:
            logging.basicConfig(
                level="INFO",
                format="%(asctime)s-[%(name)s]-[%(levelname)s]-%(message)s",
                datefmt='%d-%b-%y %H:%M:%S',
                handlers=[
                    logging.FileHandler("dice.log", mode=filemode),
                    logging.StreamHandler(sys.stdout)
                ])
        else:
            logging.basicConfig(
                level="INFO",
                format="%(asctime)s-[%(name)s]-[%(levelname)s]-%(message)s",
                datefmt='%d-%b-%y %H:%M:%S',
                handlers=[
                    logging.StreamHandler(sys.stdout)
                ])
            if LoggerConfig.PERSISTLOG in settings:
                self.logger.error('Persist log option ignored as download logs option was not enabled')
        logging.captureWarnings(capture=True)

    def info(self, msg):
        if self.logger:
            self.logger.info(msg)

    def warning(self, msg):
        if self.logger:
            self.logger.info(msg)

    def error(self, msg):
        if self.logger:
            self.logger.error(msg)

if __name__=="__main__":
    x=Logger([LoggerConfig.PERSISTLOG])
    x.info(1)
    x.error('error')
    x.warning('warning')