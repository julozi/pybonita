#-*- coding: utf-8 -*-
from nose.tools import raises

from pybonita import BonitaServer
from pybonita.tests import TestWithMockedServer, build_dumb_bonita_error_body,\
    build_bonita_group_xml
from pybonita.user import BonitaGroup


class TestGetGroup(TestWithMockedServer):
    pass

class TestGetGroupByPath(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

#    def test_unknown_group(self):
#        """ Try to retrieve group by path but no group matching """
#        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
#        url = '/identityAPI/getGroupUsingPath'
#        code = 500
#        xml = build_dumb_bonita_error_body('UserNotFoundException',message='can\'t find User: unknown')
#        BonitaServer.set_response_list([[url,code,xml]])

#        group = BonitaGroup.get_group_by_path('unknown')

#        assert group == None

#    def test_known_group(self):
#        """ Retrieve a group using the path """
#        # Setup the response for MockServer
#        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
#        url = '/identityAPI/getGroupUsingPath'
#        code = 200
#        xml = build_bonita_group_xml(uuid='996633',)
#        BonitaServer.set_response_list([[url,code,xml]])

#        group = BonitaGroup.get_group_by_path('known')

#        assert isinstance(group,BonitaGroup)
#        #assert group. == 


class TestGetGroupByUUID(TestWithMockedServer):
    pass

class TestGetDefaultRootGroup(TestWithMockedServer):
    pass
