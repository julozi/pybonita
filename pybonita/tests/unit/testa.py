#-*- coding: utf-8 -*-

from pybonita import BonitaServer
from pybonita.user import BonitaUser
from pybonita.tests import TestWithBonitaServer,TestWithMockedServer

class TestBidonA(TestWithBonitaServer):
    
    def testA(self):
        BonitaServer.connect('localhost', 9090, 'restuser', 'restbpm')
        
        user = BonitaUser('u1','p1')
        user.save()

class TestBidonB(TestWithMockedServer):

    def testB(self):
        BonitaServer.connect('localhost', 9090, 'restuser', 'restbpm')
        url = ''
        code = 204
        xml = ''
        BonitaServer.set_response_list([url,code,xml])
        
        user = BonitaUser('u2','p2')
        user.save()


