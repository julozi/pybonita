===========================
How to use the PyBonita lib
===========================

First, initialize a BonitaServer. Each commands then rely on the BonitaServer.

Examples
========

Creating a Process instance (opening a new case)
------------------------------------------------

.. code:: python
    
    BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')

    process = BonitaProcess('Demande_de_genotypage--1.0')

    variables = {'demandeur':'julien.seiler@igbmc.fr', 'titre':'Au secours', 'demande_initiale':'Plein de soucis'}
    case = process.instanciate(variables=variables)

    case.delete()

Adding a user
-------------

.. code:: python
    
    BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')

    user = BonitaUser(username="john",password="onepass")
    user.save()


Exception thrown
================

Each exception has its own error message.
When catching an Exception, you can retrieve additional information in the 
err_info instance variable.

For example

.. code:: python

    try:
        # Some code raising a BonitaException or subclass
    except BonitaException as be:
        print 'additional info : %s' % (str(be.err_info))

- :class:`BonitaException <pybonita.exception.BonitaException>`
- :class:`BonitaServerNotInitializedError <pybonita.exception.BonitaServerNotInitializedError>`
- :class:`ServerNotReachableError <pybonita.exception.ServerNotReachableError>`
- :class:`UnexpectedResponseError <pybonita.exception.UnexpectedResponseError>`


    
