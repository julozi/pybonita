===============================
How to develop the PyBonita lib
===============================

Test case
========

With bonita Server
------------------

.. code:: python
    

    from pybonita import BonitaServer
    from pybonita.tests import TestWithBonitaServer

    class TestBidonA(TestWithBonitaServer):
        
        def testA(self):
            BonitaServer.connect('localhost', 9090, 'restuser', 'restbpm')
            
            user = BonitaUser('u1','p1')
            user.save()

Without bonita Server
---------------------

.. code:: python
    

    from pybonita import BonitaServer
    from pybonita.tests import TestWithMockedServer

    class TestBidonB(TestWithMockedServer):

        def testB(self):
            BonitaServer.connect('localhost', 9090, 'restuser', 'restbpm')
            url = '/instanceAPI/user/'
            code = 204
            xml = '' # Add your XML response right here
            BonitaServer.set_response_list([url,code,xml])
            
            user = BonitaUser('u2','p2')
            user.save()

