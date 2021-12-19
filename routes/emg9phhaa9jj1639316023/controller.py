msg = wiz.request.query("data")
if msg is not None:
    wiz.socketio.emit("log", msg + "\n", namespace="/wiz", broadcast=True)
wiz.response.status(200)