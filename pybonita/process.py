# -*- coding: utf-8 -*-

import os.path
import base64

from datetime import datetime
from xml.dom.minidom import parseString

from BeautifulSoup import BeautifulStoneSoup

from pybonita import logger
from pybonita.object import BonitaObject
from pybonita.server import BonitaServer
from pybonita.utils import dictToMapString

__all__ = ['BonitaCase', 'BonitaProcess']

class BonitaProcess(BonitaObject):

    def __init__(self, uuid):
        logger.debug("Instanciating BonitaProcess with uuid : %s" % uuid)

        super(BonitaProcess, self).__init__(uuid)

        self._name = None
        self._version = None

    @classmethod
    def get(cls, uuid):

        url = "/queryDefinitionAPI/getProcess/%s" % uuid

        xml = BonitaServer.get_instance().sendRESTRequest(url=url)

        return BonitaProcess._instanciate_from_xml(xml)

    @classmethod
    def get_processes(cls, process_id):

        url = "/queryDefinitionAPI/getProcessesByProcessId/%s" % process_id

        xml = BonitaServer.get_instance().sendRESTRequest(url=url)

        soup = BeautifulStoneSoup(xml.encode('iso-8859-1'))

        processes = []
        for definition in soup.set.findAll('processdefinition'):
            processes.append(BonitaProcess._instanciate_from_xml(unicode(definition)))

        return processes

    @classmethod
    def _instanciate_from_xml(cls, xml):

        soup = BeautifulStoneSoup(xml.encode('iso-8859-1'))

        uuid = soup.processdefinition.uuid.text
        process = BonitaProcess(uuid)

        process._name = soup.find("name").text
        process._version = soup.processdefinition.version.text

        return process

    def _get_name(self):
        return self._name

    name = property(_get_name, None, None, u"name of the process")

    def _get_version(self):
        return self._version

    version = property(_get_version, None, None, u"version of the process")

    def get_cases(self):
        """ Get all existing cases from the process

        """

        url = "/queryRuntimeAPI/getProcessInstances/%s" % self.uuid

        xml = BonitaServer.get_instance().sendRESTRequest(url=url)

        soup = BeautifulStoneSoup(xml.encode('iso-8859-1'))

        cases = []
        for instance in soup.set.findAll('processinstance'):
            cases.append(BonitaCase._instanciate_from_xml(unicode(instance)))

        return cases


class BonitaCase(BonitaObject):

    @classmethod
    def get(cls, uuid):

        url = "/queryRuntimeAPI/getProcessInstance/%s" % uuid

        xml = BonitaServer.get_instance().sendRESTRequest(url=url)

        return BonitaCase._instanciate_from_xml(xml)

    @classmethod
    def get_cases(cls, process_id):

        processes = BonitaProcess.get_processes(process_id)

        cases = []
        for process in processes:
            cases.extend(process.get_cases())

        return cases

    @classmethod
    def _instanciate_from_xml(cls, xml):

        soup = BeautifulStoneSoup(xml.encode('iso-8859-1'))
        process = BonitaProcess(soup.processinstance.processuuid.text)
        uuid = soup.processinstance.instanceuuid.text

        case = BonitaCase(process, uuid=uuid)
        case.refresh(xml)

        return case

    def __init__(self, process, uuid=None, variables=None):

        self.uuid = uuid
        self._process = process
        self._variables = variables
        self._state = None
        self._is_archived = None
        self._started_date = None

    def start(self, user=None):

        if self.state != None:
            raise Exception("case already started on uuid %s" % self.uuid)

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

        self.refresh()

    def save(self):

        if self.state == None:
            raise Exception("The Bonita case is not started")

        url = "/runtimeAPI/setProcessInstanceVariable/%s" % self.uuid

        for (key, value) in self.variables.items():
            data = {}
            data["variableId"] = key
            data["variableValue"] = value

            BonitaServer.get_instance().sendRESTRequest(url=url, data=data)


    def refresh(self, xml=None):
        """ Refresh current instance with data from the BonitaServer

        """

        if xml == None:
            url = "/queryRuntimeAPI/getProcessInstance/%s" % self.uuid
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)

        soup = BeautifulStoneSoup(xml.encode('iso-8859-1'))

        variables = {}
        for variable in soup.processinstance.clientvariables.findAll('entry'):
            strings = variable.findAll('string')
            if len(strings) == 2:
                variables[strings[0].text] = strings[1].text
            else:
                variables[strings[0].text] = None

        self._variables = variables

        self._state = soup.processinstance.state.text
        self._is_archived = False if soup.processinstance.isarchived.text == "false" else True
        self._started_date = datetime.fromtimestamp(float(soup.processinstance.starteddate.text) / 1000.0)
        self._last_update = datetime.fromtimestamp(float(soup.processinstance.lastupdate.text) / 1000.0)

    def add_attachment(self, name, descriptor=None, filename=None, filepath=None, description=None, user=None):
        """ Add an attachment to the current case instance

        :param name: Name of the attachment variable in the process
        :type name: str
        :param descriptor: File object to attach to the case (mandatory if no filepath is given)
        :type name: file
        :param filename: Name of the file to attach to the case (mandatory if no filepath is given)
        :type filename: str
        :param filepath: Path to the file to attach to the case (mandatory if no descriptor or filename is given)
        :type filepath: str
        :param user: Login of the actor to use to attach the file within the case (mandatory)
        :type user: str

        """

        if self.state == None:
            raise Exception("The Bonita case is not started")

        #FIXME: check params types

        if descriptor == None and filepath == None:
            raise ValueError("add_attachment requires at least a descriptor or a filepath")

        if filename == None and filepath == None:
            raise ValueError("add_attachment requires at least a filename or a filepath")

        if filepath != None:
            filepath = os.path.expandvars(filepath)
            filepath = os.path.expanduser(filepath)
            if not os.path.exists(filepath) or not os.path.isfile(filepath):
                raise ValueError("invalid filepath : %s" % filepath)

            descriptor = open(filepath, "rb")

        if filename == None:
            filename = os.path.basename(filepath)

        import array
        bts = array.array('b', descriptor.read())

        data = dict()
        data['value'] = bts
        data['fileName'] = filename

        url = "/runtimeAPI/addAttachment/%s/%s" % (self.uuid, name)
        BonitaServer.get_instance().sendRESTRequest(url=url, data=data, user=user)

    # def get_attachment(self, name):
    #
    #     url = "/queryRuntimeAPI/getAttachments/%s/%s" % (self.uuid, name)
    #     print BonitaServer.get_instance().sendRESTRequest(url=url)
    #
    # def get_attachment_value(self, instance):
    #
    #     url = "/queryRuntimeAPI/getAttachmentValue"
    #     data = {"attachmentInstance": "<AttachmentInstance><dbid>0</dbid><attachmentUUID><value>24</value></attachmentUUID><name>pj</name><fileName>test.txt</fileName><metaData><entry><string>content-type</string><string>application/octet-stream</string></entry></metaData><processInstanceUUID><value>Demande_de_genotypage--2.0--2</value></processInstanceUUID><author>admin</author><versionDate>1361368042546</versionDate></AttachmentInstance>"}
    #
    #     print BonitaServer.get_instance().sendRESTRequest(url=url, data=data)

    def _get_process(self):
        return self._process

    def _set_process(self, value):

        if self.state != None:
            raise Exception("case already started on uuid %s" % self.uuid)

        if value != None and type(value) != BonitaProcess:
            raise TypeError("process must be a BonitaProcess instance")

        self._process = value

    process = property(_get_process, _set_process, None, u"BonitaProcess running the case")

    def _get_variables(self):
        return self._variables

    def _set_variables(self, value):

        if value != None and type(value) != dict:
            raise TypeError("variables must be a dictionnary")

        self._variables = variables

    variables = property(_get_variables, _set_variables, None, u"variables of the case")

    def _get_state(self):
        return self._state

    state = property(_get_state, None, None, u"state of the case")

    def _get_is_archived(self):
        return self._is_archived

    is_archived = property(_get_is_archived, None, None, u"archived status of the case")

    def _get_started_date(self):
        return self._started_date

    started_date = property(_get_started_date, None, None, u"start date of the case")

    def _get_last_update(self):
        return self._last_update

    last_update = property(_get_last_update, None, None, u"last update date of the case")

    def _generate_delete_url(self):
        """ Generate URL and data to used to call Bonita server to perform a
        delete operation.

        """
        return ("/runtimeAPI/deleteProcessInstance/%s" % self.uuid, None)
