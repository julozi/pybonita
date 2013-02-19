# -*- coding: utf-8 -*-

from xml.dom.minidom import parseString

from pybonita import BonitaObject, BonitaServer, logger
from pybonita.utils import dictToMapString

__all__ = ['BonitaProcess']

class BonitaProcess(BonitaObject):

    def __init__(self, uuid):
        super(BonitaProcess, self).__init__(uuid)

    @classmethod
    def get(cls, uuid):
        return BonitaProcess(uuid)


class BonitaCase(BonitaObject):

    @classmethod
    def get(cls, uuid):
        case = super(BonitaCase, self).__init__(uuid)

        url = "/queryRuntimeAPI/getProcessInstance/%s" % self.uuid

        xml = BonitaServer.get_instance().sendRESTRequest(url=url)

        print xml

        return case

    def __init__(self, process, variables=None):

        self._process = process
        self._variables = variables

    def start(self, user=None):

        data = dict()

        if self._variables == None:
            url = "/runtimeAPI/instantiateProcess/%s" % self._process.uuid
        else:
            url = "/runtimeAPI/instantiateProcessWithVariables/%s" % self._process.uuid
            data['variables'] = dictToMapString(self._variables)

        xml = BonitaServer.get_instance().sendRESTRequest(url=url, user=user, data=data)

        dom = parseString(xml)
        process_instances = dom.getElementsByTagName("ProcessInstanceUUID")
        if len(process_instances) != 1:
            raise Exception #FIXME: raise clear Exception
        values = process_instances[0].getElementsByTagName("value")
        if len(values) != 1:
            raise Exception #FIXME: raise clear Exception

        uuid = values[0].childNodes[0].data

        self.uuid = uuid

    def _generate_delete_url(self):
        """ Generate URL and data to used to call Bonita server to perform a
        delete operation.

        """
        return ("/runtimeAPI/deleteProcessInstance/%s" % self.uuid, None)