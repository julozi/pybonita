# -*- coding: utf-8 -*-

from xml.dom.minidom import parseString

from pybonita import BonitaObject, logger
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

        xml = self.server.sendRESTRequest(url=url, user=user, data=data)

        dom = parseString(xml)
        process_instances = dom.getElementsByTagName("ProcessInstanceUUID")
        if len(process_instances) != 1:
            raise Exception #FIXME: raise clear Exception
        values = process_instances[0].getElementsByTagName("value")
        if len(values) != 1:
            raise Exception #FIXME: raise clear Exception

        uuid = values[0].childNodes[0].data

        return BonitaCase(uuid)


class BonitaCase(BonitaObject):

    def __init__(self, uuid):
        super(BonitaCase, self).__init__(uuid)

    def _generate_delete_url(self):
        """ Generate URL and data to used to call Bonita server to perform a
        delete operation.

        """
        return ("/runtimeAPI/deleteProcessInstance/%s" % self.uuid, None)