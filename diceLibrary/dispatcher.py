'''
DISPATCHER is responsible for all client-server connectivity.
This includes sending and receiving files and data.

Mandatory User Arguments:-
url_endpoint : string - API URL endpoint for server, where POST request will be sent.

Optional/Customizable User Arguments:-
input_filepath : string - filepath to the file sent along with server as part of POST request parameters
output_filepath: string - filepath to write to if request is expecting a file in response to POST request
input_value: string - if not file, the arguments to be passed for the POST request
input_value_type: class/string - data-type of input_value

Other Class Members:-
function_type : int
(each combination of the customizable arguments has a separate function.
this value determines which function will be called for the particular method to be offloaded.)
constants for function_type values in constants.py
'''

import requests
import logging
import constants
import json

class Dispatcher:
    _urlEndpoint: str
    _inputFilePath: str
    _outputFilePath: str
    _inputArgs: json
    _inputArgType: str
    _isInputFile: bool
    _isOutputFile: bool
    _function_type: int
    log = None

    def __init__(self, _urlEndpoint = None, _inputFilePath = None, _outputFilePath = None, _inputArgs = None, _inputArgType = None):
        self.log = logging.getLogger()


        #init arguments
        self._urlEndpoint = _urlEndpoint if _urlEndpoint is not None else None
        self._inputFilePath = _inputFilePath if _inputFilePath is not None else None
        self._outputFilePath = _outputFilePath if _outputFilePath is not None else None
        self._inputArgs = _inputArgs if _inputArgs is not None else None
        self._inputArgType = _inputArgType if _inputArgType is not None else None

        #URL Endpoint is a required attr
        if _urlEndpoint is None:
            self.log.error("URL Endpoint not specified")
            raise Exception("URL Endpoint not specified")

        #checking which functionType to assign
        self._isInputFile= True if self._inputFilePath is not None else False
        self._isOutputFile = True if self._outputFilePath is not None else False

        if not self._isInputFile and not self._isOutputFile:
            self._function_type = constants.INPUT_VAL_OUTPUT_VAL

        elif self._isInputFile and self._isOutputFile:
            self._function_type = constants.INPUT_FILE_OUTPUT_FILE

        elif not self._isInputFile and self._isOutputFile:
            self._function_type = constants.INPUT_VAL_OUTPUT_FILE

        elif self._isInputFile and not self._isOutputFile:
            self._function_type = constants.INPUT_FILE_OUTPUT_VAL


    def offload_File_File(self):
       # Logger.info(msg="Dispatcher set to offload with inputFile, outputFile config")
        api_url = self._urlEndpoint
        files = {'file': open(self._inputFilePath, 'rb')}
        response = requests.post(url = api_url, files = files)
        response.raise_for_status()
        file = open(self._outputFilePath, 'w')
        file.write(response.text)
        file.close()
        return response.text

    def offload_Val_Val(self):
        #Logger.info(msg="Dispatcher set to offload with input arguments, output arguments config")
        api_url = self._urlEndpoint
        data = self._inputArgs
        response = requests.post(url = api_url, json = data)
        return response.text

    def offload_Val_File(self):
        #Logger.info(msg="Dispatcher set to offload with input arguments, output file config")
        api_url = self._urlEndpoint
        data = self._inputArgs
        response = requests.post(url = api_url, json = data)
        response.raise_for_status()
        file = open(self._outputFilePath, 'w')
        file.write(response.text)
        file.close()
        return response.text

    def offload_File_Val(self):
       # Logger.info(msg="Dispatcher set to offload with inputFile, output arguments config")
        api_url = self._urlEndpoint
        files = {'file': open(self._inputFilePath, 'rb')}
        response = requests.post(url = api_url, files = files)
        return response.text