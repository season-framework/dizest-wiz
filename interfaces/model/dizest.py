import os
import sys
import time
import urllib
import requests
import pathlib

host = urllib.parse.urlparse(wiz.flask.request.base_url)
host = f"{host.scheme}://{host.netloc}/dizest/log"

syspath = "/opt/workspace/dizest/src"
sys.path.insert(0, syspath)
__package__ = "dizest"
import dizest

class Config:
    def __init__(self):
        HOMEDIR = pathlib.Path.home()
        DIZESTHOME = os.path.join(HOMEDIR, ".dizest")
        self.fs = fs = wiz.model("storage").use(DIZESTHOME)
        config = fs.read.json("dizest.config.json", dict())
        self.data = config
    
    def get(self, key=None, default=None):
        if key is None:
            return self.data
        if key in self.data:
            return self.data[key]
        return default

    def set(self, **config):
        data = self.data
        for key in config:
            data[key] = config[key]
        self.fs.write.json("dizest.config.json", data)

class Model:
    def __init__(self, namespace, mode):
        self.mode = mode
        self.namespace = namespace
        wiz.room = mode + "/" + namespace
        wiz.pid = os.getpid()

    def process(self, ns=""):
        namespace = os.path.join(self.namespace, ns)
        return dizest.process(namespace, logger=self.logger)

    def workspace(self):
        namespace = self.namespace
        config = wiz.config('dizest')
        default = os.path.join(season.core.PATH.PROJECT, "dizest", self.mode)
        basepath = config.get(self.mode, default)
        basepath = os.path.join(basepath, namespace)
        wp = dizest.workspace(basepath, logger=Model.logger)
        return wp

    def delete(self):
        namespace = self.namespace
        config = wiz.config('dizest')
        default = os.path.join(season.core.PATH.PROJECT, "dizest", self.mode)
        basepath = config.get(self.mode, default)
        basepath = os.path.join(basepath, namespace)
        fs = wiz.model("storage").use(basepath)
        fs.remove()

    @staticmethod
    def logger(*args, color=94):
        tag = "[dizest]"
        log_color = color
        args = list(args)
        for i in range(len(args)): 
            args[i] = str(args[i])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)

        if wiz.pid != os.getpid():
            res = requests.post(host, {"data": logdata, "room": wiz.room})
        else:
            res = wiz.socketio.emit("log", logdata + "\n", to=wiz.room, namespace="/wiz/api/dizest.editor", broadcast=True)

    @classmethod
    def load(cls, namespace, mode='workspace'):
        return cls(namespace, mode)

    @staticmethod
    def config():
        return Config()