import json

mode = wiz.request.query("mode", True)
config = wiz.config('dizest')
path = config.get(mode)
storage = wiz.model("storage").use(path)

def workspaces(wiz):
    wps = []
    data = storage.ls()
    for i in range(len(data)):
        wp = storage.read.json(f"{data[i]}/package.dz", None)
        if 'stage' in wp:
            del wp['stage']
        wp['id'] = data[i]
        wps.append(wp)
    wiz.response.status(200, wps)
