#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from nose.tools import raises

from pybonita import BonitaServer
from pybonita.exception import BonitaXMLError
from pybonita.tests import TestCase, TestWithMockedServer, build_dumb_bonita_error_body,\
    build_bonita_role_xml
from pybonita.user import BonitaRole


class TestInstanciateFromXML(TestCase):
    """ Test the _instanciate_from_xml method """

    @raises(BonitaXMLError)
    def test_invalid_xml(self):
        """ Try to instanciate a BonitaRole from invalid XML """
        xml = '<coucou>une valeur</coucou>'

        role = BonitaRole._instanciate_from_xml(xml)

    def test_role(self):
        """ Instanciate a Bonita role """
        xml = build_bonita_role_xml('role uuid','role name',description='a role desc',label='a role label',dbid='dbid-1234')

        role = BonitaRole._instanciate_from_xml(xml)

        assert isinstance(role,BonitaRole)
        assert role.uuid == u'role uuid'
        assert role.name == u'role name'
        assert role.description == u'a role desc'
        assert role.label == u'a role label'
        assert role.dbid == u'dbid-1234'


class TestGetRole(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(TypeError)
    def test_unknown_param(self):
        """ Try to retrieve role but gives an unknown param """
        BonitaRole.get(unknown_param='32')
    
    def test_not_found_role_by_uuid(self):
        """ Try to retrieve role but nothing found with given key """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getRoleByUUID'
        code = 500
        xml = build_dumb_bonita_error_body('RoleNotFoundException',message='can\'t find Role: unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        role = BonitaRole.get(uuid='unknown')

        assert role == None
    
    def test_get_role_by_uuid(self):
        """ Retrieve a role with UUID """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getRoleByUUID'
        code = 200
        xml = build_bonita_role_xml(uuid='996633',name='myrole')
        BonitaServer.set_response_list([[url,code,xml]])

        role = BonitaRole.get(uuid='996633')

        assert isinstance(role,BonitaRole)
        assert role.uuid == '996633'

    def test_get_role_by_name(self):
        """ Retrieve a role with name """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getRole'
        code = 200
        xml = build_bonita_role_xml(uuid='996633',name='myrole')
        BonitaServer.set_response_list([[url,code,xml]])

        role = BonitaRole.get(name='myrole')

        assert isinstance(role,BonitaRole)
        assert role.name == 'myrole'


class TestGetRoleByName(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_unknown_role(self):
        """ Try to retrieve role by name but no role matching """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getRole'
        code = 500
        xml = build_dumb_bonita_error_body('RoleNotFoundException',message='can\'t find Role: unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        role = BonitaRole.get_by_name('unknown')

        assert role == None

    def test_known_role(self):
        """ Retrieve a role using the name """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getRole'
        code = 200
        xml = build_bonita_role_xml(uuid='996633',name='something')
        BonitaServer.set_response_list([[url,code,xml]])

        role = BonitaRole.get_by_name('something')

        assert isinstance(role,BonitaRole)
        assert role.uuid == '996633'
        assert role.name == u'something'


class TestGetRoleByUUID(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_unknown_role(self):
        """ Try to retrieve role by UUID but no role matching """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getRoleByUUID'
        code = 500
        xml = build_dumb_bonita_error_body('RoleNotFoundException',message='can\'t find Role: unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        role = BonitaRole.get_by_uuid('unknown')

        assert role == None

    def test_known_role(self):
        """ Retrieve a role using the UUID """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getRoleByUUID'
        code = 200
        xml = build_bonita_role_xml(uuid='996633',name='myrole')
        BonitaServer.set_response_list([[url,code,xml]])

        role = BonitaRole.get_by_uuid('996633')

        assert isinstance(role,BonitaRole)
        assert role.uuid == '996633'
