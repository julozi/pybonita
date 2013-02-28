#-*- coding: utf-8 -*-
from nose.tools import raises

from pybonita import BonitaServer
from pybonita.tests import TestWithMockedServer, build_dumb_bonita_error_body,\
    build_bonita_group_xml
from pybonita.user import BonitaGroup


class TestInstanciateFromXML(TestWithMockedServer):
    """ Test the _instanciate_from_xml method, which is not really usefull with MockedServer """

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
        xml = build_bonita_group_xml('group uuid','group name',description='a desc',label='a label')

        group = BonitaGroup._instanciate_from_xml(xml)

        assert isinstance(group,BonitaGroup)
        assert group.uuid == 'group uuid'
        assert group.name == 'group name'
        assert group.description == 'a desc'
        assert group.label == 'a label'
        assert group.parent is None

    def test_group_with_several_parents(self):
        """ Instanciate a Boinita group with a hierarchy of parents """
        xml = ''

        group = BonitaGroup._instanciate_from_xml(xml)


