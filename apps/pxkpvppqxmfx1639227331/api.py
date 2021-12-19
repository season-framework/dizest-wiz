fs_stage = wiz.model("storage").use("dizest/stage")

def dataset(wiz):
    namespace = wiz.request.query("namespace", True)
    datahub = wiz.model("datahub").load(namespace)
    dataset = datahub.dataset()
    info = dataset.info()
    wiz.response.status(200, info)

def data(wiz):
    print(dataset.stage['builder'].code())
    wiz.response.status(200)

def status(wiz):
    datahub = wiz.model("datahub").load("sample")
    dhprocess = datahub.process()

    if dhprocess.is_running():
        wiz.response.status(400)

    @dhprocess
    def process():
        dataset = datahub.dataset()
        dataset.clear()
        datadir = dataset.storage().use("data")
        cached = dataset.storage().use("cached")
        cached.delete()
        cached.makedirs()
        datadir.copy("c1.jpeg", cached.abspath("c1.jpeg"))
        data = dataset.stage.build()
        for index in range(len(data)):
            for stage in dataset.stage:
                stage(index)

        datadir.copy("cell.jpeg", cached.abspath("cell.jpeg"))
        data = dataset.stage.build()
        for index in range(len(data)):
            for stage in dataset.stage:
                stage(index)

        dataset.stage.save()
        return "test2"
    
    process()
    wiz.response.status(200)