===============================
How to develop the PyBonita lib
===============================

Guideline
=========

- get_something methods return None if nothing found
- method header must include docstring with something like this :

.. code:: python

    def my_kick_ass_method(self,param1,param2,param3=default_value,**kwargs):
        """ Short description of the method in one line.
        
        Longer description. Could include some specific behaviors description.
        
        Description of usable extra paramaters if any (those given in kwargs).
        
        :param param1: description of param1, also set the default value if any
        :type param1: type of param1 (either standard as int, str or class as BonitaUser)
        :raise ExceptionClass: when the exception may be raised
        
        """
        pass # my method code

Test case
=========

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
