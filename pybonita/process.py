# -*- coding: utf-8 -*-

from pybonita import BonitaObject
from pybonita.utils import dictToMapString

__all__ = ['BonitaProcess']

class BonitaProcess(BonitaObject):

    def __init__(self, uuid):
        super(BonitaProcess, self).__init__(uuid)

    def instanciate(self, user="john", variables=None):

        data = dict()

        if variables == None:
            url = "/runtimeAPI/instantiateProcess/%s" % self.uuid
        else:
            url = "/runtimeAPI/instantiateProcessWithVariables/%s" % self.uuid
            data['variables'] = dictToMapString(variables)

        self.server.sendRESTRequest(url, data, user)