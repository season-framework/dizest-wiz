import os
import sys
import requests
import time

syspath = "/opt/workspace/seasondh-v3/src"
sys.path.insert(0, syspath)
__package__ = "dizest"

import dizest

class Model:
    dizest = dizest

    def __init__(self, namespace):
        self.namespace = namespace

    def process(self, **kwargs):
        namespace = self.namespace
        return dizest.process(namespace, **kwargs)

    def dataset(self):
        namespace = self.namespace
        config = wiz.config('dizest')
        basepath = os.path.join(config.get("path", os.path.join(season.core.PATH.PROJECT, "dizest")), namespace)
        dataset = dizest.dataset(basepath, logger=Model.logger)
        return dataset
    
    @staticmethod
    def logger(*args):
        tag = "[dizest]"
        log_color = 94
        args = list(args)
        for i in range(len(args)): 
            args[i] = str(args[i])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)
        requests.post("http://220.82.71.14:3000/datahub/log", {"data": logdata})
        # print(logdata)

    @classmethod
    def load(cls, namespace):
        return cls(namespace)

    # @staticmethod
    # def process(*args, **kwargs):
    #     return dizest.process(*args, **kwargs)

    # @staticmethod
    # def dataset(namespace):
    #     config = wiz.config('dizest')
    #     basepath = os.path.join(config.get("path", os.path.join(season.core.PATH.PROJECT, "dizest")), namespace)
    #     dataset = dizest.dataset(basepath, logger=Model.logger)
    #     return dataset
