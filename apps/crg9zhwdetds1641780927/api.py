import season
import time
import builtins
import urllib
import requests
import traceback

mode = wiz.request.segment.get(0)
namespace = wiz.request.segment.get(1)
stage_id = wiz.request.segment.get(2)
fnname = wiz.request.segment.get(3)

logger = wiz.model("dizest").logger

dizest = wiz.model("dizest").load(namespace, mode=mode)
workspace = dizest.workspace()
stage = workspace.stage[stage_id]

env = dict()
env['print'] = logger

workspace.process = dizest.process
workspace.stage.current = stage

env['dizest'] = workspace
env['wiz'] = wiz

code = stage.get("api")
exec(code, env)

def dizest_api(wiz):
    if fnname not in env:
        wiz.response.status(404)

    try:
        env[fnname]()
    except season.core.CLASS.RESPONSE.STATUS as e:
        raise e
    except Exception as e:
        stderr = traceback.format_exc()
        logger(f"Dizest API Error: {type(e)} \n{stderr}", color=91)
        raise e
