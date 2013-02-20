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

AttributeError
ValueError
BonitaServerError (defini dans __init__.py)
     avec les messages
     'not initialized'
     'unable tot reach Bonita server'
     'unexpected server response'

