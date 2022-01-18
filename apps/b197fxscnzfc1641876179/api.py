import json

mode = wiz.request.query("mode", True)
config = wiz.model('dizest').config()
path = config.get('workspace')
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
