===============================
How to develop the PyBonita lib
===============================

Test case
========

With bonita Server
------------------

.. code:: python
    

    from pybonita.tests import TestWithBonitaServer

    class TestBidonA(TestWithBonitaServer):
        
        def testA(self):
            BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
            
            user = BonitaUser('u1','p1')
            user.save()

Without bonita Server
---------------------

.. code:: python
    

    from pybonita.tests import TestWithMockedServer

    class TestBidonB(TestWithMockedServer):

        def testB(self):
            BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')
            
            url = '/identityAPI/addUser'
            code = 204
            xml = ''
            BonitaServer.set_response_list([[url,code,xml]])
            
            user = BonitaUser('u2','p2')
            user.save()
