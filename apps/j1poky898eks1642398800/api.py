import datetime
import json

namespace = wiz.request.query("namespace", True)
mode = wiz.request.query("mode", True)
dizest = wiz.model("dizest").load(namespace, mode)

def workspace(wiz):
    wp = dizest.workspace()
    info = wp.get()
    wiz.response.status(200, info)

def update(wiz):
    data = wiz.request.query("data", True)
    data = json.loads(data)
    data['updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if 'stage' in data:
        del data['stage']

    workspace = dizest.workspace()
    workspace.update(**data)

    wiz.response.status(200)

def delete(wiz):
    dizest.delete()
    wiz.response.status(200)