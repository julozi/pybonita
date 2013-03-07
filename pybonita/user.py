# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from lxml.etree import XMLSchemaParseError

from . import logger, BonitaServer
from .exception import BonitaHTTPError, BonitaXMLError
from .object import BonitaObject
from .utils import dictToMapString, set_if_available, xml_find

__all__ = ['BonitaUser','BonitaGroup','BonitaRole','BonitaMembership']


class BonitaUser(BonitaObject):
    """ A class to map a user in Bonita.
    
    """
    
    def __init__(self,username,password,membership=None,role=None,group=None,**kwargs):
        """ Build up a new BonitaUser
        
        :param username: username to use
        :type username: str
        :param password: password to set
        :type password: str
        
        """
        #TODO Add other params
        # membership ou (role,group) mais ils sont exclusifs
        # Prends aussi d'autres parametres qui sont les champs d'un user dans bontia :
        # firstname, lastname, title, jobtitle
        # professional contact : email, phone, mobiel, fax, website, apt./room, building, address, city, zipcode, state, country
        # personal contact : email, phone, mobiel, fax, website, apt./room, building, address, city, zipcode, state, country
        # other : added as metadata
        
        self.username = username
        self.password = password
    
    def _generate_save_url(self,variables):
        url = "/identityAPI/addUser"
        
        data = dict()
        
        data['username'] = self.username
        data['password'] = self.password
        
        return (url,data)
    
    @classmethod
    def _instanciate_from_xml(cls, xml):
        """ Instanciate a BonitaUser from XML
        
        :param xml: the XML description of a user
        :type xml: unicode
        :return: BonitaUser
        :raise lxml.etree.XMLSchemaParseError: given XML does not belong to Bonita XML schema for User
        
        """
        if not isinstance(xml,(str,unicode)):
            raise TypeError('xml must be a string or unicode not %s' % (type(xml)))

        soup = BeautifulSoup(xml,'xml')

        try:
            # First thing first : instanciate a new BonitaUser with username and password
            user_soup = xml_find(soup,'user')
            username = xml_find(user_soup,'username').string
            password = xml_find(user_soup,'password').string
            user = BonitaUser(username,password)

            # Main properties now
            user.uuid = xml_find(user_soup,'uuid').string
            #TODO Must first check there is a firstname and a lastName in the soup
            #user.firstName = soup.user.firstName.text
            #user.lastName = soup.user.lastName.text

            #TODO Other properties then
        except XMLSchemaParseError as exc:
            raise

        return user

#<User>
#  <dbid>0</dbid>
#  <uuid>3f4fee49-391c-4847-ac23-b99526773b02</uuid>
#  <firstName>John</firstName>
#  <lastName>Doe</lastName>
#  <password>46e490cac450e85a9cba3059365826296771cc3</password>
#  <username>john</username>
#  <metadata/>
#  <memberships>
#    <Membership>
#      <dbid>0</dbid>
#      <uuid>ef1fc933-a95b-443e-8c30-772eb394c123</uuid>
#      <role class="Role">
#        <description>The user role</description>
#        <dbid>0</dbid>
#        <uuid>6a20e8a9-d703-44af-9cf6-cb2eea4ac515</uuid>
#        <name>user</name>
#        <label>User</label>
#      </role>
#      <group class="Group">
#        <description>The default group</description>
#        <dbid>0</dbid>
#        <uuid>603b07ad-7891-4843-8fda-6749a35cbd4d</uuid>
#        <name>platform</name>
#        <label>Platform</label>
#      </group>
#    </Membership>
#  </memberships>
#</User>

    def _set_membership(self,membership):
        """ Add a user to a Membership.
        
        :param membership: the membership to add the user in
        :type membership: BonitaMembership
        :raise Exception: if provided data does not lead to something on the BonitaServer (unknown role for ex.)
        
        """
        url = "/identityAPI/addMembershipToUser/"+self.uuid+"/"+membership.uuid
        
        try:
            response = self.server.sendRESTRequest(url=url)
        except Exception:
            print 'Exception'
    
    
    membership = property(None,_set_membership,None)
    
#    def _set_membership(self,membership=None,role=None,group=None):
#        """ Add a user to a Membership.
#        You should define membership or at least role and group.
#        
#        :param membership:
#        :type membership:
#        :param role:
#        :type role:
#        :param group:
#        :type group:
#        :raise Exception: if no data is provided
#        :raise Exception: if provided data does not lead to something on the BonitaServer (unknown role for ex.)
#        
#        """
#        pass

    
    def set_manager(self,user):
        """ Define the Manager of a user 
        
        :param user: the manager to set with
        :type user: BonitaUser
        :raise ValueError: manager user is unknown in BonitaServer

        """
        pass
    
    def set_delegee(self,user):
        """ Define the Delegee of a user 
        
        :param user: the delegee to set with
        :type user: BonitaUser
        :raise ValueError: delegee user is unknown in BonitaServer
        """
        pass
    
    @classmethod
    def get_by_username(cls,username):
        """ Retrieve a User with the username

        :param username: the username of the user to retrieve
        :type username: str

        """
        url = '/identityAPI/getUser/'+username

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            if 'UserNotFoundException'.lower() in err.bonita_exception.lower():
                return None
            else:
                raise


        user = cls._instanciate_from_xml(xml)

        return user

    @classmethod
    def get_by_uuid(cls,uuid):
        """ Retrieve a User with the UUID 

        :param uuid: the UUID of the user to retrieve
        :type uuid: str

        """
        url = '/identityAPI/getUserByUUID/'+uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            if 'UserNotFoundException'.lower() in err.bonita_exception.lower():
                return None
            else:
                raise


        user = cls._instanciate_from_xml(xml)

        return user

    @classmethod
    def get(cls,**kwargs):
        """ Retrieve a User with given parameter

        Parameter can be any of :
        - username
        - uuid

        :raise TypeError: if call with unknown parameter
        :return: BonitaUser instance or None if not found

        """
        if 'username' in kwargs:
            return cls.get_by_username(username=kwargs['username'])
        if 'uuid' in kwargs:
            return cls.get_by_uuid(uuid=kwargs['uuid'])
        
        raise TypeError('called get_user with unknown param : %s' % (kwargs.keys()))
    
    # setter par parametre
    # par exemple on fait :
    # user = BonitaUser(login,pass)
    # puis on peut faire user.firstname = 'coucou' et ca mets a jour le champs firstname directement

class BonitaGroup(BonitaObject):
    """ A class to map a group in Bonita.
    
    """
    
    def __init__(self,name,label,description,parent=None):
        """ Build up a new BonitaGroup
        
        :param name: Name of the group
        :type name: str
        :param label: Label of the group
        :type label: str
        :param description: Description of the group
        :type description: str
        :param parent: Parent of the group, default to root ('/')
        :type parent: BonitaGroup
        
        """
        self.name = name
        self.label = label
        self.description = description

        if parent != None and not isinstance(parent,BonitaGroup):
            raise TypeError('parent must be None or a BonitaGroup')

        self.parent = parent

    @classmethod
    def _instanciate_from_xml(cls, xml, is_parent=False):
        """ Instanciate a BonitaGroup from XML
        
        :param xml: the XML description of a group
        :type xml: unicode
        :param is_parent: State that the XML provided describe a parent Group (default False)
        :type is_parent: bool
        :return: BonitaGroup
        
        """
        if not isinstance(xml,(str,unicode)):
            raise TypeError('xml must be a string or unicode not %s' % (type(xml)))

        soup = BeautifulSoup(xml,'xml')

        try:
            # First thing first : instanciate a new BonitaGroup
            group_soup = xml_find(soup,'parentGroup') if is_parent else xml_find(soup,'Group')
        except XMLSchemaParseError as exc:
                raise BonitaXMLError('xml does not seem to be for a Group')

        try:
            description = xml_find(group_soup,'description').string
            name = xml_find(group_soup,'name').string
            label = xml_find(group_soup,'label').string

            new_group = BonitaGroup(name,label,description)

            # Main properties now
            new_group.uuid = xml_find(group_soup,'uuid').string

            # Other properties then
            set_if_available(new_group,group_soup,['dbid'])

            # Parent hierarchy
            parent_soup = xml_find(group_soup,'parentGroup',raise_exception=False)
            if parent_soup is not None:
                new_group.parent = cls._instanciate_from_xml(unicode(parent_soup),is_parent=True)
        except XMLSchemaParseError as exc:
            raise

        return new_group

    @classmethod
    def get_by_path(cls,path):
        """ Retrieve a Group with the path

        :param path: the path of the group to retrieve
        :type path: str

        """
        url = '/identityAPI/getGroupUsingPath'

        # remove heading /
        if path[0] == '/':
            path = path[1:]
        data = dict()
        data['hierarchy'] = []
        for part_path in path.split('/'):
            data['hierarchy'].append(part_path)

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url,data=data)
        except BonitaHTTPError as err:
            if 'GroupNotFoundException'.lower() in err.bonita_exception.lower():
                return None
            else:
                raise

        group = cls._instanciate_from_xml(xml)

        return group

    @classmethod
    def get_by_uuid(cls,uuid):
        """ Retrieve a Group with the UUID 

        :param uuid: the UUID of the group to retrieve
        :type uuid: str

        """
        url = '/identityAPI/getGroupByUUID/'+uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            if 'GroupNotFoundException'.lower() in err.bonita_exception.lower():
                return None
            else:
                raise

        group = cls._instanciate_from_xml(xml)

        return group

    @classmethod
    def get(cls,**kwargs):
        """  Retrieve a Group with given parameter

        Parameter can be any of :
        - path
        - uuid

        :raise TypeError: if call with unknown parameter
        :return: BonitaGroup instance or None if not found

        """
        if 'path' in kwargs:
            return cls.get_by_path(path=kwargs['path'])
        if 'uuid' in kwargs:
            return cls.get_by_uuid(uuid=kwargs['uuid'])
        
        raise TypeError('called get with unknown param : %s' % (kwargs.keys()))

    @classmethod
    def get_default_root(cls):
        """ Retrieve BonitaGroup which is the root, currently the /platform group.

        :return: BonitaGroup for /platform
        """
        return cls.get_by_path('/platform')


class BonitaRole(BonitaObject):
    """ A class to map a role in Bonita.
    
    """
    
    def __init__(self,name,label,description):
        """ Build up a new BonitaRole
        
        :param name: name of the role
        :type name: str or unicode
        :param label: label of the role
        :type label: str or unicode
        :param description: description of the role
        :type description: str or unicode
        
        """
        self.name = name
        self.label = label
        self.description = description

    @classmethod
    def _instanciate_from_xml(cls, xml):
        """ Instanciate a BonitaRole from XML
        
        :param xml: the XML description of a rpme
        :type xml: unicode
        :return: BonitaRole
        
        """
        if not isinstance(xml,(str,unicode)):
            raise TypeError('xml must be a string or unicode not %s' % (type(xml)))

        soup = BeautifulSoup(xml,'xml')

        try:
            # First thing first : instanciate a new BonitaRole
            role_soup = xml_find(soup,'role')

            description = xml_find(role_soup,'description').string
            name = xml_find(role_soup,'name').string
            label = xml_find(role_soup,'label').string

            new_role = BonitaRole(name,label,description)

            # Main properties now
            new_role.uuid = xml_find(role_soup,'uuid').string

            # Other properties then
            set_if_available(new_role,role_soup,['dbid'])

        except XMLSchemaParseError as exc:
            raise

        return new_role

    @classmethod
    def get_by_name(cls,name):
        """ Retrieve a Role with the name

        :param path: the name of the role to retrieve
        :type path: str

        """
        url = '/identityAPI/getRole/'+name

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            if 'RoleNotFoundException'.lower() in err.bonita_exception.lower():
                return None
            else:
                raise

        role = cls._instanciate_from_xml(xml)

        return role

    @classmethod
    def get_by_uuid(cls,uuid):
        """ Retrieve a Role with the UUID 

        :param uuid: the UUID of the role to retrieve
        :type uuid: str

        """
        url = '/identityAPI/getRoleByUUID/'+uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            if 'RoleNotFoundException'.lower() in err.bonita_exception.lower():
                return None
            else:
                raise

        role = cls._instanciate_from_xml(xml)

        return role

    @classmethod
    def get(cls,**kwargs):
        """  Retrieve a Role with given parameter

        Parameter can be any of :
        - name
        - uuid

        :raise TypeError: if call with unknown parameter
        :return: BonitaRole instance or None if not found

        """
        if 'name' in kwargs:
            return cls.get_by_name(name=kwargs['name'])
        if 'uuid' in kwargs:
            return cls.get_by_uuid(uuid=kwargs['uuid'])
        
        raise TypeError('called get with unknown param : %s' % (kwargs.keys()))



#    def _generate_save_url(self,variables):
#        url = "/identityAPI/addRole/"+self.name
#        data = None
#        
#        return (url,data)
#    
#    def _generate_delete_url(self,variables):
#        url = "/identityAPI/removeRole/"+self.name
#        data = None
#        
#        return (url,data)
#    

class BonitaMembership(BonitaObject):
    """ A class to map a membership in Bonita.
    
    """

    def __init__(self,role,group):
        """ Build up a new BonitaMembership

        :param role: the role bound to this membership
        :type role: BonitaRole instance
        :param group: the group bound to this membership
        :type group: BonitaGroup instance
        :raise TypeError: if role is not a BonitaRole instance
        :raise TypeError: if group is not a BonitaGroup instance

        """
        if not isinstance(role,BonitaRole):
            raise TypeError('role must be a BonitaRole instance')
        if not isinstance(group,BonitaGroup):
            raise TypeError('group must be a BonitaGroup instance')

        self.role = role
        self.group = group

    @classmethod
    def _instanciate_from_xml(cls, xml):
        """ Instanciate a BonitaMembership from XML
        
        :param xml: the XML description of a rpme
        :type xml: unicode
        :return: BonitaMembership
        :raise BonitaException: if group or role can't be instanciate from XML
        
        """
        soup = BeautifulSoup(xml,'xml')

        # First try to decode Role and Group
        membership = soup.Membership
        group = BonitaGroup._instanciate_from_xml(membership.Group)
        if group is None:
            raise BonitaXMLError('can\'t properly creat a group from XML')
        role = BonitaRole._instanciate_from_xml(membership.Role)
        if role is None:
            raise BonitaXMLError('can\'t properly creat a role from XML')

        new_membership = BonitaMembership(role,group)

        # Other properties then
        set_if_available(new_membership,membership,['dbid'])

        return new_membership

    @classmethod
    def get_by_role_and_group_uuid(cls,role_uuid,group_uuid):
        """ Retrieve a Membership with the role and group UUID.
        If membership does not exists but role and group exist, the membership will be created

        :param role_uuid: UUID of the role bound to the membership
        :type role_uuid: str or unicode
        :param group_uuid: UUID of the group bound to the membership
        :type group_uuid: str or unicode

        """
        url = '/identityAPI/getMembershipForRoleAndGroup/'+role_uuid+'/'+group_uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            if ('RoleNotFoundException'.lower() in err.bonita_exception.lower() or
                'GroupNotFoundException'.lower() in err.bonita_exception.lower() ):
                return None
            else:
                raise

        membership = cls._instanciate_from_xml(xml)

        return membership

    @classmethod
    def get_by_role_and_group(cls,role,group):
        """ Retrieve a Membership with the role and group.
        If membership does not exists but role and group exist, the membership will be created

        :param role: role bound to the membership
        :type role: BonitaRole
        :param group: group bound to the membership
        :type group: BonitaGroup

        """
        url = '/identityAPI/getMembershipForRoleAndGroup/'+role.uuid+'/'+group.uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            if ('RoleNotFoundException'.lower() in err.bonita_exception.lower() or
                'GroupNotFoundException'.lower() in err.bonita_exception.lower() ):
                return None
            else:
                raise

        membership = cls._instanciate_from_xml(xml)

        return membership

    @classmethod
    def get_by_uuid(cls,uuid):
        """ Retrieve a Membership with the UUID 

        :param uuid: the UUID of the membership to retrieve
        :type uuid: str

        """
        url = '/identityAPI/getMembershipByUUID/'+uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            if 'MembershipNotFoundException'.lower() in err.bonita_exception.lower():
                return None
            else:
                raise

        membership = cls._instanciate_from_xml(xml)

        return membership

    @classmethod
    def get(cls,**kwargs):
        """  Retrieve a Membership with given parameter

        Parameter can be any of :
        - [role,group]
        - uuid

        :raise TypeError: if call with unknown parameter
        :return: BonitaMembership instance or None if not found

        """
        if 'role' in kwargs:
            if 'group' in kwargs:
                return cls.get_by_role_and_group(role=kwargs['role'],group=kwargs['group'])
        if 'uuid' in kwargs:
            return cls.get_by_uuid(uuid=kwargs['uuid'])
        
        raise TypeError('called get with unknown param : %s' % (kwargs.keys()))


