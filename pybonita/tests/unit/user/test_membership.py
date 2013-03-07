#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from nose.tools import raises

from pybonita import BonitaServer
from pybonita.exception import BonitaXMLError
from pybonita.tests import TestCase, TestWithMockedServer, build_dumb_bonita_error_body,\
    build_bonita_role_xml, build_bonita_group_xml, build_bonita_membership_xml
from pybonita.user import BonitaMembership, BonitaRole, BonitaGroup

class TestConstructor(TestCase):
    """ Test the __init__ method """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(TypeError)
    def test_bad_role(self):
        """ Try to build a membership but role is not a BonitaRole """
        group = BonitaGroup('mygroup','','')

        membership = BonitaMembership(role='role',group=group)

    @raises(TypeError)
    def test_bad_group(self):
        """ Try to build a membership but group is not a BonitaGroup """
        role = BonitaRole('myrole','','')

        membership = BonitaMembership(role=role,group=123)

    def test_init(self):
        """ Build a membership """
        role = BonitaRole('myrole','','')
        group = BonitaGroup('mygroup','','')

        membership = BonitaMembership(role=role,group=group)

        assert membership.role == role
        assert membership.group == group


class TestInstanciateFromXML(TestCase):
    """ Test the _instanciate_from_xml method """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(BonitaXMLError)
    def test_instanciate_bad_role_xml(self):
        """ Instanciate a Bonita membership from XML : role is not well formed """
        role_xml = '<Role>et boom</Role>'
        group_xml = build_bonita_group_xml(uuid='112233',name='mygroup',with_class=True)
        xml = build_bonita_membership_xml(uuid='uuid-12',role=role_xml, group=group_xml,dbid='dbid-1234')
        print 'xml : %s (%s)' % (xml,type(xml))
        membership = BonitaMembership._instanciate_from_xml(xml)

    @raises(BonitaXMLError)
    def test_instanciate_bad_group_xml(self):
        """ Instanciate a Bonita membership from XML : group is not well formed """
        role_xml = build_bonita_role_xml(uuid='334455',name='myrole',with_class=True)
        group_xml = '<PasGroup><uuid>1234</uuid></PasGroup>'
        xml = build_bonita_membership_xml(uuid='uuid-12',role=role_xml, group=group_xml,dbid='dbid-1234')

        membership = BonitaMembership._instanciate_from_xml(xml)

    def test_instanciate(self):
        """ Instanciate a Bonita membership from XML """
        role_xml = build_bonita_role_xml(uuid='334455',name='myrole',with_class=True)
        group_xml = build_bonita_group_xml(uuid='112233',name='mygroup',with_class=True)
        xml = build_bonita_membership_xml(uuid='uuid-12',role=role_xml, group=group_xml,dbid='dbid-1234')

        membership = BonitaMembership._instanciate_from_xml(xml)

        assert isinstance(membership,BonitaMembership)
        assert membership.uuid == u'uuid-12'
        assert membership.dbid == u'dbid-1234'
        assert isinstance(membership.role,BonitaRole)
        assert isinstance(membership.group,BonitaGroup)


class TestGetMembership(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(TypeError)
    def test_unknown_param(self):
        """ Try to retrieve membership but gives an unknown param """
        BonitaMembership.get(unknown_param='32')

    def test_get_membership_by_uuid(self):
        """ Retrieve a membership using UUID """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipByUUID'
        code = 200
        role_xml = build_bonita_role_xml(uuid='334455',name='myrole',with_class=True)
        group_xml = build_bonita_group_xml(uuid='112233',name='mygroup',with_class=True)
        xml = build_bonita_membership_xml(uuid='uuid-12',role=role_xml, group=group_xml)
        BonitaServer.set_response_list([[url,code,xml]])

        membership = BonitaMembership.get_by_uuid('uuid-12')

        assert isinstance(membership,BonitaMembership)
        assert membership.uuid == u'uuid-12'
        assert isinstance(membership.role,BonitaRole)
        assert isinstance(membership.group,BonitaGroup)

    def test_get_membership_by_role_and_group_uuid(self):
        """ Retrieve a membership using role and group UUID """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipForRoleAndGroup'
        code = 200

        role_xml = build_bonita_role_xml(uuid='334455',name='role-2',with_class=True)
        group_xml = build_bonita_group_xml(uuid='112233',name='group-14',with_class=True)
        xml = build_bonita_membership_xml(uuid='996633',role=role_xml, group=group_xml)
        BonitaServer.set_response_list([[url,code,xml]])

        membership = BonitaMembership.get(role_uuid='334455',group_uuid='112233')

        assert isinstance(membership,BonitaMembership)
        assert isinstance(membership.role,BonitaRole)
        assert membership.role.uuid == u'334455'
        assert isinstance(membership.group,BonitaGroup)
        assert membership.group.uuid == u'112233'

    def test_get_membership_by_role_and_group(self):
        """ Retrieve a membership using BonitaRole and BonitaGroup  """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipForRoleAndGroup'
        code = 200

        role = BonitaRole('myrole','','')
        role.uuid = '1234'
        group = BonitaGroup('mygroup','','')
        group.uuid = '2345'

        xml = build_bonita_membership_xml(uuid='996633',role=role, group=group)
        BonitaServer.set_response_list([[url,code,xml]])

        membership = BonitaMembership.get(role=role,group=group)

        assert isinstance(membership,BonitaMembership)
        assert isinstance(membership.role,BonitaRole)
        assert membership.role.uuid == u'1234'
        assert isinstance(membership.group,BonitaGroup)
        assert membership.group.uuid == u'2345'


class TestGetMembershipByRoleAndGroupUUID(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_unknown_role(self):
        """ Try to retrieve membership by role and group UUID : no role matching given UUID"""
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipForRoleAndGroup'
        code = 500
        xml = build_dumb_bonita_error_body('RoleNotFoundException',message='can\'t find Role : unknown')
        BonitaServer.set_response_list([[url,code,xml]])
        membership = BonitaMembership.get_by_role_and_group_uuid(role_uuid='unknown',group_uuid='group-14')

        assert membership == None

    def test_unknown_group(self):
        """ Try to retrieve membership by role and group  UUID : no group matching given UUID"""
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipForRoleAndGroup'
        code = 500
        xml = build_dumb_bonita_error_body('GroupNotFoundException',message='can\'t find Group: unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        membership = BonitaMembership.get_by_role_and_group_uuid(role_uuid='role-2',group_uuid='unknown')

        assert membership == None

    def test_get_membership_by_role_and_group(self):
        """ Retrieve a membership using role and group UUID """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipForRoleAndGroup'
        code = 200

        role_xml = build_bonita_role_xml(uuid='334455',name='myrole',with_class=True)
        group_xml = build_bonita_group_xml(uuid='112233',name='mygroup',with_class=True)
        xml = build_bonita_membership_xml(uuid='996633',role=role_xml, group=group_xml)
        BonitaServer.set_response_list([[url,code,xml]])

        membership = BonitaMembership.get_by_role_and_group_uuid(role_uuid='334455',group_uuid='112233')

        assert isinstance(membership, BonitaMembership)
        assert isinstance(membership.role,BonitaRole)
        assert membership.role.uuid == u'334455'
        assert isinstance(membership.group,BonitaGroup)
        assert membership.group.uuid == u'112233'


class TestGetMembershipByRoleAndGroup(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @raises(TypeError)
    def test_role_not_bonitarole(self):
        """ Try to retrieve membership by role and group but role is not a BonitaRole """
        group = BonitaGroup('mygroup','','')
        group.uuid = '2345'

        membership = BonitaMembership.get_by_role_and_group(role='unknown',group=group)

    @raises(TypeError)
    def test_group_not_bonitagroup(self):
        """ Try to retrieve membership by role and group but group is not a BonitaGroup """
        role = BonitaRole('myrole','','')
        role.uuid = '1234'

        membership = BonitaMembership.get_by_role_and_group(role=role,group='unknown')

    def test_unknown_role(self):
        """ Try to retrieve membership by role and group : no role matching """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipForRoleAndGroup'
        code = 500
        xml = build_dumb_bonita_error_body('RoleNotFoundException',message='can\'t find Role : unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        role = BonitaRole('myrole','','')
        role.uuid = '1234'
        group = BonitaGroup('mygroup','','')
        group.uuid = '2345'

        membership = BonitaMembership.get_by_role_and_group(role=role,group=group)

        assert membership == None

    def test_unknown_group(self):
        """ Try to retrieve membership by role and group : no group matching """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipForRoleAndGroup'
        code = 500
        xml = build_dumb_bonita_error_body('GroupNotFoundException',message='can\'t find Group: unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        role = BonitaRole('myrole','','')
        role.uuid = '1234'
        group = BonitaGroup('mygroup','','')
        group.uuid = '2345'

        membership = BonitaMembership.get_by_role_and_group(role=role,group=group)

        assert membership == None

    def test_get_membership_by_role_and_group(self):
        """ Retrieve a membership using role and group """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipForRoleAndGroup'
        code = 200

        role = BonitaRole('myrole','','')
        role.uuid = '1234'
        group = BonitaGroup('mygroup','','')
        group.uuid = '2345'

        xml = build_bonita_membership_xml(uuid='996633',role=role, group=group)
        BonitaServer.set_response_list([[url,code,xml]])


        membership = BonitaMembership.get_by_role_and_group(role,group)

        assert isinstance(membership, BonitaMembership)
        assert isinstance(membership.role,BonitaRole)
        assert isinstance(membership.group,BonitaGroup)


class TestGetMembershipByUUID(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_unknown_membership(self):
        """ Try to retrieve membership by UUID but no membership matching """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipByUUID'
        code = 500
        xml = build_dumb_bonita_error_body('MembershipNotFoundException',message='can\'t find Membership : unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        membership = BonitaMembership.get_by_uuid('unknown')

        assert membership == None

    def test_known_membership(self):
        """ Retrieve a membership using the UUID """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getMembershipByUUID'
        code = 200
        role_xml = build_bonita_role_xml(uuid='334455',name='myrole',with_class=True)
        group_xml = build_bonita_group_xml(uuid='112233',name='mygroup',with_class=True)
        xml = build_bonita_membership_xml(uuid='996633',role=role_xml, group=group_xml)
        BonitaServer.set_response_list([[url,code,xml]])

        membership = BonitaMembership.get_by_uuid('996633')

        assert isinstance(membership,BonitaMembership)
        assert membership.uuid == '996633'
