#-*- coding: utf-8 -*-
from nose.tools import raises

from pybonita import BonitaServer
from pybonita.tests import TestWithMockedServer, build_dumb_bonita_error_body,\
    build_bonita_user_xml, build_xml_set
from pybonita.user import BonitaUser


class TestGetUser(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(TypeError)
    def test_unknown_param(self):
        """ Try to retrieve user but gives an unknown param """
        BonitaUser.get(unknown_param='32')
    
    def test_not_found_user_by_uuid(self):
        """ Try to retrieve user but nothing found with given key """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUserByUUID'
        code = 500
        xml = build_dumb_bonita_error_body('UserNotFoundException',message='can\'t find User: not found uuid')
        BonitaServer.set_response_list([[url,code,xml]])

        user = BonitaUser.get(uuid='not found uuid')

        assert user == None
    
    def test_get_user_by_uuid(self):
        """ Retrieve a user with UUID """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUserByUUID'
        code = 200
        xml = build_bonita_user_xml(uuid='12345678',password='',username='username')
        BonitaServer.set_response_list([[url,code,xml]])

        user = BonitaUser.get(uuid='12345678')
        
        assert isinstance(user,BonitaUser)
        assert user.uuid == '12345678'

    def test_get_user_by_username(self):
        """ Retrieve a user with username """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUser'
        code = 200
        xml = build_bonita_user_xml(uuid='996633',password='',username='myuser')
        BonitaServer.set_response_list([[url,code,xml]])

        user = BonitaUser.get(username='myuser')
        
        assert isinstance(user,BonitaUser)
        assert user.username == 'myuser'


class TestGetUserByUsername(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_unknown_user(self):
        """ Try to retrieve user by username but no user matching """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUser'
        code = 500
        xml = build_dumb_bonita_error_body('UserNotFoundException',message='can\'t find User: unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        user = BonitaUser.get_by_username('unknown')

        assert user == None

    def test_known_user(self):
        """ Retrieve a user using the username """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUser'
        code = 200
        xml = build_bonita_user_xml(uuid='996633',password='',username='known')
        BonitaServer.set_response_list([[url,code,xml]])

        user = BonitaUser.get_by_username('known')

        assert isinstance(user,BonitaUser)
        assert user.username == 'known'


class TestGetUserByUUID(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_unknown_user(self):
        """ Try to retrieve user by UUID but no user matching """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUserByUUID'
        code = 500
        xml = build_dumb_bonita_error_body('UserNotFoundException',message='can\'t find User: unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        user = BonitaUser.get_by_uuid('unknown')

        assert user == None

    def test_known_user(self):
        """ Retrieve a user using the UUID """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUserByUUID'
        code = 200
        xml = build_bonita_user_xml(uuid='996633',password='',username='username')
        BonitaServer.set_response_list([[url,code,xml]])

        user = BonitaUser.get_by_uuid('996633')

        assert isinstance(user,BonitaUser)
        assert user.uuid == '996633'

class TestFindAll(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_no_user(self):
        """ Retrieve all users but there are none """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUsers'
        code = 200
        xml = "<set></set>"
        BonitaServer.set_response_list([[url,code,xml]])

        users = BonitaUser.find_all()

        assert isinstance(users,list)
        assert len(users) == 0

    def test_some_users(self):
        """ Retrieve all users """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUsers'
        code = 200
        user1_xml = build_bonita_user_xml(uuid='996633',password='',username='user1')
        user2_xml = build_bonita_user_xml(uuid='112345',password='',username='user2')
        xml = build_xml_set([user1_xml,user2_xml])
        BonitaServer.set_response_list([[url,code,xml]])

        users = BonitaUser.find_all()

        assert isinstance(users,list)
        assert len(users) == 2

        for user in users:
            assert isinstance(user,BonitaUser)

        sorted_users = sorted(users, key=lambda user: user.uuid)
        assert sorted_users[0].uuid == u'112345'
        assert sorted_users[1].uuid == u'996633'
