# -*- coding: utf-8 -*-

from pybonita import server

__all__ = ['BonitaProcess']

class BonitaProcess(BonitaObject):

    def __init__(self, uuid):
        super(self, BonitaObject).__init__(uuid)

    def instanciate(self, user="john"):

        url = "/bonita-server-rest/API/runtimeAPI/instantiateProcess/%s" % self.uuid

        server.sendRESTRequest(url, None, user)