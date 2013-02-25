#-*- coding: utf-8 -*-
from nose.tools import raises

from pybonita import BonitaServer
from pybonita.tests import TestWithMockedServer, build_dumb_bonita_error_body,\
    build_bonita_process_definition_xml
from pybonita.process import BonitaProcess


class TestGetProcess(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_not_found_process(self):
        """ Retrieve not existing process """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/queryDefinitionAPI/getProcess/MonProcessus1--1.0'
        code = 500
        xml = build_dumb_bonita_error_body('ProcessNotFoundException',message='Bonita Error: bai_QDAPII_5\nCan\'t find a process with uuid MonProcessus1--1.0')
        BonitaServer.set_response_list([[url,code,xml]])

        process = BonitaProcess.get('MonProcessus1--1.0')

        assert process == None

    def test_get_process(self):
        """ Retrieve a process """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = u'/queryDefinitionAPI/getProcess/MonProcessus1--1.0'
        code = 200
        xml = build_bonita_process_definition_xml(uuid=u'MonProcessus1--1.0', name=u'MonProcessus1', version=u'1.0')
        BonitaServer.set_response_list([[url,code,xml]])

        process = BonitaProcess.get(u'MonProcessus1--1.0')

        assert process != None
        assert isinstance(process,BonitaProcess)
        assert process.uuid == u'MonProcessus1--1.0'
        assert process.name == u'MonProcessus1'
        assert process.version == u'1.0'