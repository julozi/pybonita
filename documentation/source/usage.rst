===========================
How to use the PyBonita lib
===========================

First, initialize a BonitaServer. Each commands then rely on the BonitaServer.

Examples
========

Creating a Process instance (opening a new case)
------------------------------------------------

.. code:: python
    
    BonitaServer.connect('localhost', 9090, 'restuser', 'restbpm')

    process = BonitaProcess('Demande_de_genotypage--1.0')

    variables = {'demandeur':'julien.seiler@igbmc.fr', 'titre':'Au secours', 'demande_initiale':'Plein de soucis'}
    case = process.instanciate(variables=variables)

    case.delete()

Adding a user
-------------

.. code:: python
    
    BonitaServer.connect('localhost', 9090, 'restuser', 'restbpm')

    user = BonitaUser(login="john",password="onepass")
    user.save()


Exception thrown
================

Here, description of what kind of Exception could be thrown and the meaning of each one.
