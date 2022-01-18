def login(wiz):
    password = wiz.request.query("password", True)
    config = wiz.model("dizest").config()
    config_password = config.get("password")

    if password == config_password:
        wiz.session.set(active=True)
        wiz.response.status(200)

    wiz.response.status(400)