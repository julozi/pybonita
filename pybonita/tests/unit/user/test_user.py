#-*- coding: utf-8 -*-
from nose.tools import raises

from pybonita.tests import TestWithMockedServer

from pybonita.user import BonitaUser

# getUser
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
        BonitaUser.get_user(unknwon_parama='32')


class TestGetUserByUsername(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_unknown_user(self):
        """ Try to retrieve user by username but no user matching """
        BonitaUser.get_user_by_username('unknown')
        pass

    def test_known_user(self):
        """ Retrieve a user using the username """
        pass

class TestGetUserByUUID(TestWithMockedServer):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_unknown_user(self):
        """ Try to retrieve user by UUID but no user matching """
        pass

    def test_known_user(self):
        """ Retrieve a user using the UUID """
        pass
