#-*- coding: utf-8 -*-
from lxml.etree import XMLSchemaParseError
from nose.tools import raises, assert_raises

from pybonita import BonitaServer
from pybonita.exception import BonitaException
from pybonita.tests import TestCase, TestWithMockedServer, build_dumb_bonita_error_body,\
    build_bonita_user_xml, build_xml_set, build_xml_list
from pybonita.user import BonitaUser, BonitaRole, BonitaGroup, BonitaMembership


class TestConstructor(TestCase):
    """ Test the __init__ method """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_init_base(self):
        """ Build a user with just base data """
        user = BonitaUser(username=u'myusername', password=u'mypassword')

        assert isinstance(user, BonitaUser)
        assert user.username == u'myusername'
        assert user.password == u'mypassword'
        assert isinstance(user.memberships, list)
        assert len(user.memberships) == 0
        assert user.is_modified is True

    def test_init_base_and_unsupported(self):
        """ Build a user with base data and some unsupported data """
        user = BonitaUser(username=u'myusername', password=u'mypassword', truc=u'muche')

        assert isinstance(user, BonitaUser)
        assert user.username == u'myusername'
        assert user.password == u'mypassword'
        assert_raises(AttributeError, getattr, user, 'truc')

    def test_init_optional_data(self):
        """ Build a user with some optional data """
        user = BonitaUser(username=u'myusername', password=u'mypassword',
                          firstName=u'myfirstname', lastName=u'mylastname',
                          title=u'mytittle', jobTitle=u'myjobTitle')

        assert isinstance(user, BonitaUser)
        assert user.username == u'myusername'
        assert user.password == u'mypassword'
        assert user.firstName == u'myfirstname'
        assert user.lastName == u'mylastname'
        assert user.title == u'mytittle'
        assert user.jobTitle == u'myjobTitle'
        assert user.is_modified is True

# IMPROVE: check personal_infos at __init__
# IMPROVE: check professional_infos at __init__
# TODO: add tests for personal_infos
# TODO: add tests for professional_infos


class TestInstanciateFromXML(TestCase):
    """ Test the _instanciate_from_xml method """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(XMLSchemaParseError)
    def test_invalid_xml(self):
        """ Try to instanciate a BonitaUser from invalid XML """
        xml = '<coucou>une valeur</coucou>'

        BonitaUser._instanciate_from_xml(xml)

    def test_user_base(self):
        """ Instanciate a BonitaUser with base properties """
        xml = build_bonita_user_xml('user uuid', 'user pass', 'user name')

        user = BonitaUser._instanciate_from_xml(xml)

        assert isinstance(user, BonitaUser)
        assert user.is_modified is False
        assert user.uuid == u'user uuid'
        assert user.username == u'user name'
        assert user.password == u'user pass'

    def test_user_optional(self):
        """ Instanciate a BonitaUser with optional properties """
        user_properties = {'firstName': u'firstname', 'lastName': u'lastname',
                           'title': u'title', 'jobTitle': u'jobtitle'}
        xml = build_bonita_user_xml('user uuid', 'user pass', 'user name', user_properties)

        user = BonitaUser._instanciate_from_xml(xml)

        assert isinstance(user, BonitaUser)
        assert user.is_modified is False
        assert user.uuid == u'user uuid'
        assert user.username == u'user name'
        assert user.password == u'user pass'
        assert user.firstName == u'firstname'
        assert user.lastName == u'lastname'
        assert user.title == u'title'
        assert user.jobTitle == u'jobtitle'

    def test_user_with_memberships(self):
        """ Instanciate a BonitaUser with memberships """
        role = BonitaRole('myrole', '', '')
        role.uuid = '1234'

        group1 = BonitaGroup('mygroup1', '', '')
        group1.uuid = '2345'
        group2 = BonitaGroup('mygroup2', '', '')
        group2.uuid = '2346'

        membership1 = BonitaMembership(role, group1)
        membership1.uuid = 'uuid-12'
        membership2 = BonitaMembership(role, group2)
        membership2.uuid = 'uuid-13'

        user_properties = {'firstName': u'firstname', 'lastName': u'lastname',
                           'title': u'title', 'jobTitle': u'jobtitle',
                           'memberships': [membership1, membership2]}
        xml = build_bonita_user_xml('user uuid', 'user pass', 'user name', user_properties)

        user = BonitaUser._instanciate_from_xml(xml)

        assert isinstance(user, BonitaUser)
        assert isinstance(user.memberships, list)
        assert len(user.memberships) == 2


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
        xml = build_dumb_bonita_error_body('UserNotFoundException', message='can\'t find User: not found uuid')
        BonitaServer.set_response_list([[url, code, xml]])

        user = BonitaUser.get(uuid='not found uuid')

        assert user is None

    def test_get_user_by_uuid(self):
        """ Retrieve a user with UUID """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUserByUUID'
        code = 200
        xml = build_bonita_user_xml(uuid='12345678', password='', username='username')
        BonitaServer.set_response_list([[url, code, xml]])

        user = BonitaUser.get(uuid='12345678')

        assert isinstance(user, BonitaUser)
        assert user.uuid == '12345678'

    def test_get_user_by_username(self):
        """ Retrieve a user with username """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUser'
        code = 200
        xml = build_bonita_user_xml(uuid='996633', password='', username='myuser')
        BonitaServer.set_response_list([[url, code, xml]])

        user = BonitaUser.get(username='myuser')

        assert isinstance(user, BonitaUser)
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
        xml = build_dumb_bonita_error_body('UserNotFoundException', message='can\'t find User: unknown')
        BonitaServer.set_response_list([[url, code, xml]])

        user = BonitaUser.get_by_username('unknown')

        assert user is None

    def test_known_user(self):
        """ Retrieve a user using the username """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUser'
        code = 200
        xml = build_bonita_user_xml(uuid='996633', password='', username='known')
        BonitaServer.set_response_list([[url, code, xml]])

        user = BonitaUser.get_by_username('known')

        assert isinstance(user, BonitaUser)
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
        xml = build_dumb_bonita_error_body('UserNotFoundException', message='can\'t find User: unknown')
        BonitaServer.set_response_list([[url, code, xml]])

        user = BonitaUser.get_by_uuid('unknown')

        assert user is None

    def test_known_user(self):
        """ Retrieve a user using the UUID """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUserByUUID'
        code = 200
        xml = build_bonita_user_xml(uuid='996633', password='', username='username')
        BonitaServer.set_response_list([[url, code, xml]])

        user = BonitaUser.get_by_uuid('996633')

        assert isinstance(user, BonitaUser)
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
        xml = build_xml_set([])
        BonitaServer.set_response_list([[url, code, xml]])

        users = BonitaUser.find_all()

        assert isinstance(users, list)
        assert len(users) == 0

    def test_some_users(self):
        """ Retrieve all users """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getUsers'
        code = 200
        user1_xml = build_bonita_user_xml(uuid='996633', password='', username='user1')
        user2_xml = build_bonita_user_xml(uuid='112345', password='', username='user2')
        xml = build_xml_set([user1_xml, user2_xml])
        BonitaServer.set_response_list([[url, code, xml]])

        users = BonitaUser.find_all()

        assert isinstance(users, list)
        assert len(users) == 2

        for user in users:
            assert isinstance(user, BonitaUser)

        sorted_users = sorted(users, key=lambda user: user.uuid)
        assert sorted_users[0].uuid == u'112345'
        assert sorted_users[1].uuid == u'996633'


class TestFindByRole(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(TypeError)
    def test_not_role(self):
        """ Try to retrieve Users for a Role but not given a Role """
        BonitaUser.find_by_role(role='coucou')

    def test_no_user(self):
        """ Retrieve all users for a role but there are none """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getAllUsersInRole'
        code = 200
        xml = build_xml_list([])
        BonitaServer.set_response_list([[url, code, xml]])

        role = BonitaRole('myrole', '', '')
        role.uuid = '1234'

        users = BonitaUser.find_by_role(role)

        assert isinstance(users, list)
        assert len(users) == 0

    def test_some_users(self):
        """ Retrieve all users for a role """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getAllUsersInRole'
        code = 200
        user1_xml = build_bonita_user_xml(uuid='1234', password='', username='user1')
        user2_xml = build_bonita_user_xml(uuid='6789', password='', username='user2')
        xml = build_xml_list([user1_xml, user2_xml])
        BonitaServer.set_response_list([[url, code, xml]])

        role = BonitaRole('myrole', '', '')
        role.uuid = '1234'

        users = BonitaUser.find_by_role(role)

        assert isinstance(users, list)
        assert len(users) == 2

        for user in users:
            assert isinstance(user, BonitaUser)

        sorted_users = sorted(users, key=lambda user: user.uuid)
        assert sorted_users[0].uuid == u'1234'
        assert sorted_users[1].uuid == u'6789'


class TestFindByGroup(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(TypeError)
    def test_not_group(self):
        """ Try to retrieve Users for a Group but not given a Group """
        BonitaUser.find_by_group(group='coucou')

    def test_no_user(self):
        """ Retrieve all users for a group but there are none """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getAllUsersInGroup'
        code = 200
        xml = build_xml_list([])
        BonitaServer.set_response_list([[url, code, xml]])

        group = BonitaGroup('mygroup', '', '')
        group.uuid = '2345'

        users = BonitaUser.find_by_group(group)

        assert isinstance(users, list)
        assert len(users) == 0

    def test_some_users(self):
        """ Retrieve all users for a group """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getAllUsersInGroup'
        code = 200
        user1_xml = build_bonita_user_xml(uuid='1234', password='', username='user1')
        user2_xml = build_bonita_user_xml(uuid='6789', password='', username='user2')
        xml = build_xml_list([user1_xml, user2_xml])
        BonitaServer.set_response_list([[url, code, xml]])

        group = BonitaGroup('mygroup', '', '')
        group.uuid = '2345'

        users = BonitaUser.find_by_group(group)

        assert isinstance(users, list)
        assert len(users) == 2

        for user in users:
            assert isinstance(user, BonitaUser)

        sorted_users = sorted(users, key=lambda user: user.uuid)
        assert sorted_users[0].uuid == u'1234'
        assert sorted_users[1].uuid == u'6789'


class TestFindByGroupAndRole(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(TypeError)
    def test_not_role(self):
        """ Try to retrieve Users for a role and group but not given a Role """
        group = BonitaGroup('mygroup', '', '')
        group.uuid = '2345'

        BonitaUser.find_by_role_and_group('coucou', group)

    @raises(TypeError)
    def test_not_group(self):
        """ Try to retrieve Users for a role and group but not given a Group """
        role = BonitaRole('myrole', '', '')
        role.uuid = '1234'

        BonitaUser.find_by_role_and_group(role, 123.45)

    def test_no_user(self):
        """ Retrieve all users for a role but there are none """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getAllUsersInRoleAndGroup'
        code = 200
        xml = build_xml_list([])
        BonitaServer.set_response_list([[url, code, xml]])

        role = BonitaRole('myrole', '', '')
        role.uuid = '1234'
        group = BonitaGroup('mygroup', '', '')
        group.uuid = '2345'

        users = BonitaUser.find_by_role_and_group(role, group)

        assert isinstance(users, list)
        assert len(users) == 0

    def test_some_users(self):
        """ Retrieve all users for a role """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getAllUsersInRoleAndGroup'
        code = 200
        user1_xml = build_bonita_user_xml(uuid='1234', password='', username='user1')
        user2_xml = build_bonita_user_xml(uuid='6789', password='', username='user2')
        xml = build_xml_list([user1_xml, user2_xml])
        BonitaServer.set_response_list([[url, code, xml]])

        role = BonitaRole('myrole', '', '')
        role.uuid = '1234'
        group = BonitaGroup('mygroup', '', '')
        group.uuid = '2345'

        users = BonitaUser.find_by_role_and_group(role, group)

        assert isinstance(users, list)
        assert len(users) == 2

        for user in users:
            assert isinstance(user, BonitaUser)

        sorted_users = sorted(users, key=lambda user: user.uuid)
        assert sorted_users[0].uuid == u'1234'
        assert sorted_users[1].uuid == u'6789'


class TestCreate(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_fresh_user(self):
        """ Save a freshly create BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')

        url = '/identityAPI/addUser'
        code = 204
        user_xml = build_bonita_user_xml(uuid='myuuid', password='mypassword', username='myusername')
        BonitaServer.set_response_list([[url, code, user_xml]])

        user._create()

        assert user.is_modified is False
        assert user.uuid == 'myuuid'


class TestUpdateBaseAttributes(TestWithMockedServer):
    # IMPROVE: add tests with only parts of base attributes modified

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_not_modified(self):
        """ Update base attributes for unmodified BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        # Mark user as unmodified
        user.clear_state()

        user._update_base_attributes()

        assert user.is_modified is False

    @raises(BonitaException)
    def test_update_not_saved(self):
        """ Update base attributes fors BonitaUser which is not already saved """
        user = BonitaUser(username=u'myusername', password=u'mypassword')

        user._update_base_attributes()

    def test_modified(self):
        """ Update base attributes of a BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        # Prepare response of MockedServer
        url = '/identityAPI/updateUserByUUID'
        code = 200
        user_xml = build_bonita_user_xml(uuid='myuuid', password='mypassword', username='other_usernames')
        BonitaServer.set_response_list([[url, code, user_xml]])

        # Modify some base attributes
        user.last_name = u'last_name'
        user.title = u'Doctor'
        user.username = u'other_username'
        user.first_name = u'first_name'
        user.job_title = u'job_title'

        user._update_base_attributes()

        assert user.last_name == u'last_name'
        assert user.title == u'Doctor'
        assert user.username == u'other_username'
        assert user.first_name == u'first_name'
        assert user.job_title == u'job_title'

        dirties = user.get_dirties()
        for attribute in user.BASE_ATTRIBUTES:
            assert attribute not in dirties


class TestUpdatePassword(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_not_modified(self):
        """ Update password for unmodified BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        # Mark user as unmodified
        user.clear_state()

        user._update_password()

        assert user.is_modified is False

    @raises(BonitaException)
    def test_update_not_saved(self):
        """ Update password for BonitaUser which is not already saved """
        user = BonitaUser(username=u'myusername', password=u'mypassword')

        user._update_password()

    def test_modified(self):
        """ Update password of a BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        # Prepare response of MockedServer
        url = '/identityAPI/updateUserPassword'
        code = 200
        user_xml = build_bonita_user_xml(uuid='myuuid', password='mypassword', username='other_usernames')
        BonitaServer.set_response_list([[url, code, user_xml]])

        # Modify password
        user.password = u'some pass'

        user._update_password()

        assert user.password == u'some pass'

        dirties = user.get_dirties()
        assert 'password' not in dirties


class TestUpdatePersonalContactInfos(TestWithMockedServer):
    # IMPROVE: add tests with only parts of personal contact infos modified

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_not_modified(self):
        """ Update personal contact infos for unmodified BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        # Mark user as unmodified
        user.clear_state()

        user._update_personal_contact_infos()

        assert user.is_modified is False

    @raises(BonitaException)
    def test_update_not_saved(self):
        """ Update personal contact infos for BonitaUser which is not already saved """
        user = BonitaUser(username=u'myusername', password=u'mypassword')

        user._update_personal_contact_infos()

    def test_modified(self):
        """ Update personal contact infos of a BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        # Prepare response of MockedServer
        url = '/identityAPI/updateUserPersonalContactInfo'
        code = 200
        user_xml = build_bonita_user_xml(uuid='myuuid', password='mypassword', username='other_usernames')
        BonitaServer.set_response_list([[url, code, user_xml]])

        # Modify some personal contact data
        user.personal_infos['building'] = u'building'
        user.personal_infos['website'] = u'website'
        user.personal_infos['state'] = u'state'
        user.personal_infos['city'] = u'city'
        user.personal_infos['country'] = u'country'
        user.personal_infos['faxNumber'] = u'faxNumber'
        user.personal_infos['phoneNumber'] = u'phoneNumber'
        user.personal_infos['email'] = u'email'
        user.personal_infos['address'] = u'address'
        user.personal_infos['zipCode'] = u'zipCode'
        user.personal_infos['mobileNumber'] = u'mobileNumber'
        user.personal_infos['room'] = u'room'

        user._update_personal_contact_infos()

        assert user.personal_infos['building'] == u'building'
        assert user.personal_infos['website'] == u'website'
        assert user.personal_infos['state'] == u'state'
        assert user.personal_infos['city'] == u'city'
        assert user.personal_infos['country'] == u'country'
        assert user.personal_infos['faxNumber'] == u'faxNumber'
        assert user.personal_infos['phoneNumber'] == u'phoneNumber'
        assert user.personal_infos['email'] == u'email'
        assert user.personal_infos['address'] == u'address'
        assert user.personal_infos['zipCode'] == u'zipCode'
        assert user.personal_infos['mobileNumber'] == u'mobileNumber'
        assert user.personal_infos['room'] == u'room'

        assert user.personal_infos.is_modified is False


class TestUpdateProfessionalContactInfos(TestWithMockedServer):
    # IMPROVE: add tests with only parts of personal contact infos modified

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_not_modified(self):
        """ Update professional contact infos for unmodified BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        # Mark user as unmodified
        user.clear_state()

        user._update_professional_contact_infos()

        assert user.is_modified is False

    @raises(BonitaException)
    def test_update_not_saved(self):
        """ Update professional contact infos for BonitaUser which is not already saved """
        user = BonitaUser(username=u'myusername', password=u'mypassword')

        user._update_professional_contact_infos()

    def test_modified(self):
        """ Update professional contact infos of a BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        # Prepare response of MockedServer
        url = '/identityAPI/updateUserProfessionalContactInfo'
        code = 200
        user_xml = build_bonita_user_xml(uuid='myuuid', password='mypassword', username='other_usernames')
        BonitaServer.set_response_list([[url, code, user_xml]])

        # Modify some professional contact data
        user.professional_infos['building'] = u'building'
        user.professional_infos['website'] = u'website'
        user.professional_infos['state'] = u'state'
        user.professional_infos['city'] = u'city'
        user.professional_infos['country'] = u'country'
        user.professional_infos['faxNumber'] = u'faxNumber'
        user.professional_infos['phoneNumber'] = u'phoneNumber'
        user.professional_infos['email'] = u'email'
        user.professional_infos['address'] = u'address'
        user.professional_infos['zipCode'] = u'zipCode'
        user.professional_infos['mobileNumber'] = u'mobileNumber'
        user.professional_infos['room'] = u'room'

        user._update_professional_contact_infos()

        assert user.professional_infos['building'] == u'building'
        assert user.professional_infos['website'] == u'website'
        assert user.professional_infos['state'] == u'state'
        assert user.professional_infos['city'] == u'city'
        assert user.professional_infos['country'] == u'country'
        assert user.professional_infos['faxNumber'] == u'faxNumber'
        assert user.professional_infos['phoneNumber'] == u'phoneNumber'
        assert user.professional_infos['email'] == u'email'
        assert user.professional_infos['address'] == u'address'
        assert user.professional_infos['zipCode'] == u'zipCode'
        assert user.professional_infos['mobileNumber'] == u'mobileNumber'
        assert user.professional_infos['room'] == u'room'

        assert user.professional_infos.is_modified is False


class TestUpdate(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_not_modified(self):
        """ Update an unmodified BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        # Mark user as unmodified
        user.clear()

        user._update()

        assert user.is_modified is False

    @raises(BonitaException)
    def test_update_not_saved(self):
        """ Update a BonitaUser which is not already saved """
        user = BonitaUser(username=u'myusername', password=u'mypassword')

        user._update()

    def test_professional_contact_infos_modified(self):
        """ Update profressional contact infos of BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'
        user.clear()

        # Prepare response of MockedServer
        url = '/identityAPI/updateUserProfessionalContactInfo'
        code = 200
        user_xml = build_bonita_user_xml(uuid='myuuid', password='mypassword', username='other_usernames')
        BonitaServer.set_response_list([[url, code, user_xml]])

        # Modify some professional contact data
        user.professional_infos['building'] = u'building'
        user.professional_infos['website'] = u'website'
        user.professional_infos['state'] = u'state'
        user.professional_infos['city'] = u'city'
        user.professional_infos['country'] = u'country'
        user.professional_infos['faxNumber'] = u'faxNumber'
        user.professional_infos['phoneNumber'] = u'phoneNumber'
        user.professional_infos['email'] = u'email'
        user.professional_infos['address'] = u'address'
        user.professional_infos['zipCode'] = u'zipCode'
        user.professional_infos['mobileNumber'] = u'mobileNumber'
        user.professional_infos['room'] = u'room'

        user._update()

        assert user.is_modified is False
        assert user.professional_infos['building'] == u'building'
        assert user.professional_infos['website'] == u'website'
        assert user.professional_infos['state'] == u'state'
        assert user.professional_infos['city'] == u'city'
        assert user.professional_infos['country'] == u'country'
        assert user.professional_infos['faxNumber'] == u'faxNumber'
        assert user.professional_infos['phoneNumber'] == u'phoneNumber'
        assert user.professional_infos['email'] == u'email'
        assert user.professional_infos['address'] == u'address'
        assert user.professional_infos['zipCode'] == u'zipCode'
        assert user.professional_infos['mobileNumber'] == u'mobileNumber'
        assert user.professional_infos['room'] == u'room'

    def test_personal_contact_infos_modified(self):
        """ Update personal contact infos of BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'
        user.clear()

        # Prepare response of MockedServer
        url = '/identityAPI/updateUserPersonalContactInfo'
        code = 200
        user_xml = build_bonita_user_xml(uuid='myuuid', password='mypassword', username='other_usernames')
        BonitaServer.set_response_list([[url, code, user_xml]])

        # Modify some personal contact data
        user.personal_infos['building'] = u'building'
        user.personal_infos['website'] = u'website'
        user.personal_infos['state'] = u'state'
        user.personal_infos['city'] = u'city'
        user.personal_infos['country'] = u'country'
        user.personal_infos['faxNumber'] = u'faxNumber'
        user.personal_infos['phoneNumber'] = u'phoneNumber'
        user.personal_infos['email'] = u'email'
        user.personal_infos['address'] = u'address'
        user.personal_infos['zipCode'] = u'zipCode'
        user.personal_infos['mobileNumber'] = u'mobileNumber'
        user.personal_infos['room'] = u'room'

        user._update()

        assert user.is_modified is False
        assert user.personal_infos['building'] == u'building'
        assert user.personal_infos['website'] == u'website'
        assert user.personal_infos['state'] == u'state'
        assert user.personal_infos['city'] == u'city'
        assert user.personal_infos['country'] == u'country'
        assert user.personal_infos['faxNumber'] == u'faxNumber'
        assert user.personal_infos['phoneNumber'] == u'phoneNumber'
        assert user.personal_infos['email'] == u'email'
        assert user.personal_infos['address'] == u'address'
        assert user.personal_infos['zipCode'] == u'zipCode'
        assert user.personal_infos['mobileNumber'] == u'mobileNumber'
        assert user.personal_infos['room'] == u'room'

    def test_password_modified(self):
        """ Update password contact infos of BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'

        user.clear()

        # Prepare response of MockedServer
        url = '/identityAPI/updateUserPassword'
        code = 200
        user_xml = build_bonita_user_xml(uuid='myuuid', password='mypassword', username='other_usernames')
        BonitaServer.set_response_list([[url, code, user_xml]])

        # Modify password
        user.password = u'some pass'

        user._update()

        assert user.is_modified is False
        assert user.password == u'some pass'

    def test_base_attributes_modified(self):
        """ Update BonitaUser base attributes """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        user._uuid = 'myuuid'
        user.clear()

        # Prepare response of MockedServer
        url = '/identityAPI/updateUserByUUID'
        code = 200
        user_xml = build_bonita_user_xml(uuid='myuuid', password='mypassword', username='other_usernames')
        BonitaServer.set_response_list([[url, code, user_xml]])

        # Modify some base attributes
        user.last_name = u'last_name'
        user.title = u'Doctor'
        user.username = u'other_username'
        user.first_name = u'first_name'
        user.job_title = u'job_title'

        user._update()

        assert user.is_modified is False
        assert user.last_name == u'last_name'
        assert user.title == u'Doctor'
        assert user.username == u'other_username'
        assert user.first_name == u'first_name'
        assert user.job_title == u'job_title'


class TestSave(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_not_modified(self):
        """ Save an unmodified BonitaUser """
        user = BonitaUser(username=u'myusername', password=u'mypassword')
        # Mark user as unmodified
        user.clear_state()

        user.save()

        assert user.is_modified is False

    def test_newly_created(self):
        """ Save a newly create BonitaUser """
        # TODO: to develop
        pass

# TODO: add more tests for save : save must create but also update if needed
