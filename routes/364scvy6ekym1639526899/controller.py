action = wiz.request.segment.action
if action == 'log':
    room = wiz.request.query("room", True)
    msg = wiz.request.query("data", None)
    if msg is not None:
        wiz.socketio.emit("log", msg + "\n", to=room, namespace="/wiz/api/dizest.editor", broadcast=True)
    wiz.response.status(200)

wiz.response.render("/dizest/list", "dizest.list", mode='workspace')
wiz.response.render("/dizest/editor/<namespace>", "dizest.editor", mode='workspace')
wiz.response.render("/dizest/preview/<mode>/<namespace>/<stage_id>", "dizest.preview")

wiz.response.redirect("/dizest/list")