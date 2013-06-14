PyBonita
========

pybonita is a Python wrapper for the Bonita REST API

Python packages installation
----------------------------

^python setup.py install

Examples
--------

Here are 2 examples using the PyBonita library

Creating a new case
...................

    # -*- coding: utf-8 -*-
    from pybonita import BonitaServer
    from pybonita import BonitaCase, BonitaProcess

    def main():
        # Connect with the Bonita server
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm')

        # Retrieve the process where we want a new case open
        process = BonitaProcess.get(u'MyProcess--1.0')

        # Initialize params of the Case : use your own names here
        variables = {'demandeur':'julien',
                     'titre':'Au secours',
                     'demande_initiale':'Plein de soucis'}

        # Prepare the new case
        case = BonitaCase(process=process, variables=variables)

        # Add an attachment
        filepath = "~/Desktop/machin.txt"
        case.add_attachment(name="pj", filepath=filepath)

        # Create the new case on the bonita server
        case.start()

    if __name__ == '__main__':
        main()


Creating a new user in a group, for a given role
................................................

    #-*- coding: utf-8 -*-
    from pybonita import BonitaServer
    from pybonita import BonitaUser, BonitaGroup, BonitaRole, BonitaMembership


    def main():
        # Setup the connexion to the server
        BonitaServer.use('localhost', 9090, 'restuser', 'restbpm', ['latin-1'])

        # Retrieve group of "response entreprise"
        group = BonitaGroup.get(path='/platform/responsables_entreprise')

        # Retrieve users allready registrered in this group
        allready_registered_users = BonitaUser.find(group=group)

        # Get role "user"
        role = BonitaRole.get(name='user')

        # Get Membership for group and role
        membership = BonitaMembership.get(group=group, role=role)

        # Register new user for this group and role
        user = BonitaUser(username='email@user.com', password='123456')
        user.memberships.append(membership)
        user.save()


    if __name__ == '__main__':
        main()
