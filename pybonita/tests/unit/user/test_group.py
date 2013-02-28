#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from nose.tools import raises

from pybonita import BonitaServer
from pybonita.tests import TestCase, TestWithMockedServer, build_dumb_bonita_error_body,\
    build_bonita_group_xml
from pybonita.user import BonitaGroup


class TestInstanciateFromXML(TestCase):
    """ Test the _instanciate_from_xml method """

    def test_group_without_parent(self):
        """ Instanciate a Bonita group without any parent """
        xml = build_bonita_group_xml('group uuid','group name',description='a desc',label='a label')

        group = BonitaGroup._instanciate_from_xml(xml)

        assert isinstance(group,BonitaGroup)
        assert group.uuid == 'group uuid'
        assert group.name == 'group name'
        assert group.description == 'a desc'
        assert group.label == 'a label'
        assert group.parent is None

    def test_group_with_one_parent(self):
        """ Instanciate a Bonita group with one parent """
        # Build up parent and child XML
        parent_xml = build_bonita_group_xml('parent uuid','parent name','parent description','parent label',None, True)
        child_xml = build_bonita_group_xml('group uuid','group name',description='a desc',label='a label')
        
        # Add the parent XML to the Child
        parent_soup = BeautifulStoneSoup(parent_xml)
        child_soup = BeautifulStoneSoup(child_xml)
        child_soup.append(parent_soup)

        xml = child_soup.prettify()

        group = BonitaGroup._instanciate_from_xml(xml)

        assert isinstance(group,BonitaGroup)
        assert group.uuid == 'group uuid'
        assert group.name == 'group name'
        assert group.description == 'a desc'
        assert group.label == 'a label'

        assert group.parent is not None
        assert isinstance(group.parent, BonitaGroup)
        assert group.parent.parent is None

    def test_group_with_several_parents(self):
        """ Instanciate a Boinita group with a hierarchy of parents """
        # Build up parents and child XML
        parentA_xml = build_bonita_group_xml('parentA uuid','parentA name','parentA description','parentA label',None, True)
        parentB_xml = build_bonita_group_xml('parentB uuid','parentB name','parentB description','parentB label',None, True)
        parentC_xml = build_bonita_group_xml('parentC uuid','parentC name','parentC description','parentC label',None, True)
        child_xml = build_bonita_group_xml('group uuid','group name',description='a desc',label='a label')
        
        # Add the hierachy of parents to the Child
        parentA_soup = BeautifulStoneSoup(parentA_xml)
        parentB_soup = BeautifulStoneSoup(parentB_xml)
        parentC_soup = BeautifulStoneSoup(parentC_xml)

        parentB_soup.append(parentC_soup)
        parentA_soup.append(parentB_soup)

        child_soup = BeautifulStoneSoup(child_xml)
        child_soup.append(parentA_soup)

        xml = child_soup.prettify()

        group = BonitaGroup._instanciate_from_xml(xml)

        assert isinstance(group,BonitaGroup)
        assert group.uuid == 'group uuid'
        assert group.name == 'group name'
        assert group.description == 'a desc'
        assert group.label == 'a label'

        assert group.parent is not None
        assert isinstance(group.parent, BonitaGroup)
        assert group.parent.uuid == 'parentA uuid'

        assert group.parent.parent is not None
        assert isinstance(group.parent.parent, BonitaGroup)
        assert group.parent.parent.uuid == 'parentB uuid'

        assert group.parent.parent.parent is not None
        assert isinstance(group.parent.parent.parent, BonitaGroup)
        assert group.parent.parent.parent.uuid == 'parentC uuid'


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

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_unknown_group(self):
        """ Try to retrieve group by UUID but no group matching """
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getGroupByUUID'
        code = 500
        xml = build_dumb_bonita_error_body('GroupNotFoundException',message='can\'t find Group: unknown')
        BonitaServer.set_response_list([[url,code,xml]])

        group = BonitaGroup.get_group_by_uuid('unknown')

        assert group == None

    def test_known_group(self):
        """ Retrieve a group using the UUID """
        # Setup the response for MockServer
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
        url = '/identityAPI/getGroupByUUID'
        code = 200
        xml = build_bonita_group_xml(uuid='996633',name='mygroup')
        BonitaServer.set_response_list([[url,code,xml]])

        group = BonitaGroup.get_group_by_uuid('996633')

        assert isinstance(group,BonitaGroup)
        assert group.uuid == '996633'

class TestGetDefaultRootGroup(TestWithMockedServer):
    pass