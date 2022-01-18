import season
import datetime
import json
import os
import pathlib

class Controller(wiz.controller("base")):
    def __startup__(self, wiz):
        super().__startup__(wiz)

        config = wiz.model("dizest").config()
        if config.get("active", False) is False:
            wiz.response.redirect("/dizest/install")

        if wiz.session.has("active") == False:
            wiz.response.redirect("/dizest/login")