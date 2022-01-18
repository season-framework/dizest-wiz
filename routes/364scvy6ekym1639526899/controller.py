action = wiz.request.segment.action
if action == 'log':
    room = wiz.request.query("room", True)
    msg = wiz.request.query("data", None)
    if msg is not None:
        wiz.socketio.emit("log", msg + "\n", to=room, namespace="/wiz/api/dizest.editor", broadcast=True)
    wiz.response.status(200)

if action == 'export':
    segment = wiz.match("/dizest/export/<mode>/<workspace_id>")
    mode = segment.mode
    workspace_id = segment.workspace_id
    
    dizest = wiz.model("dizest").load(workspace_id, mode=mode)
    wp = dizest.workspace()
    packagepath = wp.storage.abspath("package.dz")
    wiz.response.download(packagepath, as_attachment=True, filename=f"{workspace_id}.dz")

if action == 'logout':
    wiz.session.clear()
    wiz.response.redirect("/")

wiz.response.render("/dizest/install", "dizest.install")
wiz.response.render("/dizest/login", "dizest.login")
wiz.response.render("/dizest/list", "dizest.list", mode='workspace')
wiz.response.render("/dizest/viewer/<namespace>", "dizest.viewer", mode='workspace')
wiz.response.render("/dizest/editor/<namespace>", "dizest.editor", mode='workspace')
wiz.response.render("/dizest/preview/<mode>/<namespace>/<stage_id>", "dizest.preview")

wiz.response.redirect("/dizest/list")