def install(wiz):
    data = wiz.request.query()
    if 'host' not in data: data['host'] = '0.0.0.0'
    if 'port' not in data: data['port'] = '3000'
    if 'password' not in data: wiz.response.status(403)
    data['active'] = True
    
    config = wiz.model("dizest").config()
    config.set(**data)

    wiz.response.status(200)