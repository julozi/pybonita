# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from lxml.etree import XMLSchemaParseError

from . import BonitaServer
from .exception import BonitaHTTPError, BonitaXMLError, BonitaException
from .object import BonitaObject
from .utils import set_if_available, xml_find, xml_find_all,\
    TrackableList, TrackableObject, TrackableDict

__all__ = ['BonitaUser', 'BonitaGroup', 'BonitaRole', 'BonitaMembership']


class BonitaUser(BonitaObject, TrackableObject):
    """ A class to map a user in Bonita.

    """
    # Optional properties for a BonitaUser
    USER_PROPERTIES = ['firstName', 'lastName', 'title', 'jobTitle']

    def __init__(self, username, password, **kwargs):
        """ Build up a new BonitaUser

        :param username: username to use
        :type username: str
        :param password: password to set
        :type password: str

        """
        #TODO: Add other params
        # membership ou (role,group) mais ils sont exclusifs
        # Prends aussi d'autres parametres qui sont les champs d'un user dans
        # bontia :
        # professional contact : email, phone, mobiel, fax, website, apt./room,
        # building, address, city, zipcode, state, country
        # personal contact : email, phone, mobiel, fax, website, apt./room,
        # building, address, city, zipcode, state, country
        # other : added as metadata

        TrackableObject.__init__(self, **kwargs)

        self._uuid = None
        self.username = username
        self.password = password
        self.personal_infos = TrackableDict()
        self.professional_infos = TrackableDict()

        # Set other user properties
        # TODO: loading of personal_infos
        # TODO: loading of professional_infos
        for (arg_key, arg_value) in kwargs.iteritems():
            if arg_key in self.USER_PROPERTIES:
                setattr(self, arg_key, arg_value)

        self._memberships = TrackableList()

    def _get_memberships(self):
        """ Retrieve the memberships for a BonitaUser """
        return self._memberships

    memberships = property(_get_memberships, None, None)

    def _get_uuid(self):
        """ Retrieve the UUID of a Bonita User """
        return self._uuid

    uuid = property(_get_uuid, None, None)  # This property ensure the UUID is not hand-written

    def clear(self, attribute=None):
        """ Clear an attribute or all data from modified flag.
        *If attribute is not given, clear all modified attributes.*

        """
        if attribute is None:
            getattr(self,'personal_infos',TrackableDict()).clear_state()
            getattr(self,'professional_infos',TrackableDict()).clear_state()

        super(BonitaUser,self).clear(attribute)

    @classmethod
    def _instanciate_from_xml(cls, xml):
        """ Instanciate a BonitaUser from XML

        :param xml: the XML description of a user
        :type xml: unicode
        :return: BonitaUser
        :raise lxml.etree.XMLSchemaParseError: given XML does not belong to
            Bonita XML schema for User

        """
        if not isinstance(xml, (str, unicode)):
            raise TypeError('xml must be a string or unicode not %s' % (type(xml)))

        soup = BeautifulSoup(xml, 'xml')

        try:
            # First thing first : instanciate a new BonitaUser with username and password
            user_soup = xml_find(soup, 'user')
            username = xml_find(user_soup, 'username').string
            password = xml_find(user_soup, 'password').string
            user = BonitaUser(username, password)

            # Main properties now
            user._uuid = xml_find(user_soup, 'uuid').string

            # Other properties then
            set_if_available(user, user_soup, cls.USER_PROPERTIES)

            # Memberships
            tag_memberships = xml_find_all(user_soup, 'membership')
            for tag_membership in tag_memberships:
                membership = BonitaMembership._instanciate_from_xml(unicode(tag_membership))
                user._memberships.append(membership)
            # Clean the state of user._memberships
            user._memberships.clear_state()

        except XMLSchemaParseError:
            raise

        # Mark this user as unchanged because we've just build it !
        user.clear()

        return user

#<User>
#  <dbid>0</dbid>
# <uuid>8d3b69f2-2835-43c9-b3bc-e261b6ed9372</uuid>
# <firstName>Tony</firstName>
# <lastName>Moutaux</lastName>
# <password>101e8702733cced254345e193c88aaa47a4f5de</password>
# <username>tony.moutaux@igbmc.fr</username>
#  <manager>bed453a7-0573-47ff-9378-a7dda1b15644</manager>
#  <delegee>75d16be7-8a37-47aa-ae3d-bbe484a1464c</delegee>
# <title>Mr</title>
# <jobTitle>Ing.</jobTitle>
#  <professionalContactInfo class="org.ow2.bonita.facade.identity.impl.ContactInfoImpl">
#    <email>tony.moutaux@igbmc.fr</email>
#    <phoneNumber>0388653395</phoneNumber>
#    <mobileNumber>0606060606</mobileNumber>
#    <faxNumber>0388653201</faxNumber>
#    <building>IGBMC</building>
#    <room>0078</room>
#    <address>1, rue Laurent Friess</address>
#    <zipCode>67400</zipCode>
#    <city>Illkirch-Graffenstaden</city>
#    <state>Alsace</state>
#    <country>France</country>
#    <website>http://www.igbmc.fr</website>
#  </professionalContactInfo>
#  <personalContactInfo class="org.ow2.bonita.facade.identity.impl.ContactInfoImpl">
#    <email>gaelle_tony.moutaux@libertysurf.fr</email>
#    <phoneNumber>0303030303</phoneNumber>
#    <mobileNumber>0603030303</mobileNumber>
#    <faxNumber>0303030304</faxNumber>
#    <building>Petite maison aprÃ¨s le pont</building>
#    <room>Dans le toit</room>
#    <address>6, grand rue de la Kirneck</address>
#    <zipCode>67140</zipCode>
#    <city>Bourgheim</city>
#    <state>Alsace</state>
#    <country>France</country>
#    <website>http://renovalsace.blogspot.com</website>
#  </personalContactInfo>
#  <metadata>
#    <entry>
#      <ProfileMetadata>
#        <dbid>0</dbid>
#        <uuid>6da83b0d-d8dc-4a77-a89b-7e0dbd189ba6</uuid>
#        <name>meta1</name>
#        <label>label-meta1</label>
#      </ProfileMetadata>
#      <string>valeur de meta1</string>
#    </entry>
#  </metadata>
#  <memberships>
#    <Membership>
#      <dbid>0</dbid>
#      <uuid>1c5dac3a-d54c-4d94-8dad-46e7ac32720a</uuid>
#      <role class="Role">
#        <description>The user role</description>
#        <dbid>0</dbid>
#        <uuid>03d22c81-d41c-4b1b-b6d5-7bb944aeaea4</uuid>
#        <name>user</name>
#        <label>User</label>
#      </role>
#      <group class="Group">
#        <description>Responsables d&apos;entreprise pour les Services communs</description>
#        <dbid>0</dbid>
#        <uuid>40ea29d1-5abc-44ca-a6b1-159977e0b6d6</uuid>
#        <name>responsables_entreprise</name>
#        <label>responsables_entreprise</label>
#        <parentGroup class="Group">
#          <description>The default group : ave un texte Ã©&amp;&apos;Ã¨`-[{}$Ã¹%&amp; blabla</description>
#          <dbid>0</dbid>
#          <uuid>c18bb42b-2fee-4a08-9ab6-fe61d3be726e</uuid>
#          <name>platform</name>
#          <label>Platform</label>
#        </parentGroup>
#      </group>
#    </Membership>
#    <Membership>
#      <dbid>0</dbid>
#      <uuid>b70d39d3-44ea-4bb0-8fae-6d285457682f</uuid>
#      <role class="Role">
#        <description>The admin role</description>
#        <dbid>0</dbid>
#        <uuid>98b4df11-9623-4c44-8c7a-c575d504439c</uuid>
#        <name>admin</name>
#        <label>Admin</label>
#      </role>
#      <group class="Group">
#        <description>Responsables d&apos;entreprise pour les Services communs</description>
#        <dbid>0</dbid>
#        <uuid>40ea29d1-5abc-44ca-a6b1-159977e0b6d6</uuid>
#        <name>responsables_entreprise</name>
#        <label>responsables_entreprise</label>
#        <parentGroup class="Group">
#          <description>The default group : ave un texte Ã©&amp;&apos;Ã¨`-[{}$Ã¹%&amp; blabla</description>
#          <dbid>0</dbid>
#          <uuid>c18bb42b-2fee-4a08-9ab6-fe61d3be726e</uuid>
#          <name>platform</name>
#          <label>Platform</label>
#        </parentGroup>
#      </group>
#    </Membership>
#    <Membership>
#      <dbid>0</dbid>
#      <uuid>a7ee072a-77c1-4ffa-8a6f-d55fabd39a51</uuid>
#      <role class="Role">
#        <description>The admin role</description>
#        <dbid>0</dbid>
#        <uuid>98b4df11-9623-4c44-8c7a-c575d504439c</uuid>
#        <name>admin</name>
#        <label>Admin</label>
#      </role>
#      <group class="Group">
#        <description>desc1</description>
#        <dbid>0</dbid>
#        <uuid>dc947b56-7f46-4aa6-9f14-d2c904e2c79c</uuid>
#        <name>testtony</name>
#        <label>label1</label>
#        <parentGroup class="Group">
#          <description>Service de genotypage</description>
#          <dbid>0</dbid>
#          <uuid>fc13ad9b-1666-47e4-9ec0-d18607cd35ad</uuid>
#          <name>genotypage</name>
#          <label>Genotypage</label>
#          <parentGroup class="Group">
#            <description>The default group : ave un texte Ã©&amp;&apos;Ã¨`-[{}$Ã¹%&amp; blabla</description>
#            <dbid>0</dbid>
#            <uuid>c18bb42b-2fee-4a08-9ab6-fe61d3be726e</uuid>
#            <name>platform</name>
#            <label>Platform</label>
#          </parentGroup>
#        </parentGroup>
#      </group>
#    </Membership>
#  </memberships>
#</User>

    def save(self, user=None, variables=None):
        """ Save a BonitaUser : sends data to create a BonitaUser on the server.
        It also create all associated resources, like BonitaMembership.

        """
        # If nothing modified, nothing to do
        if self.is_unchanged:
            return

        # Is this a new user ?
        if self.uuid is None:
            self._create_user(user=user)

        # Now we can deal with all other attributes
        self._update(user=user)


    def _create(self, user=None):
        """ Create a new BonitaUser.
        This method will set the username, password and uuid attributes.

        """
        url = "/identityAPI/addUser"

        data = dict()

        data['username'] = self.username
        data['password'] = self.password

        # Call the BonitaServer
        xml = BonitaServer.get_instance().sendRESTRequest(url=url, user=user, data=data)

        # Extract UUID of newly created object
        soup = BeautifulSoup(xml, 'xml')
        instances = soup.findAll("uuid")
        if len(instances) != 1:
            raise Exception  # fixme: raise clear Exception
        self._uuid = instances[0].text

        # Mark as cleared of any modification
        self.clear()

    def _update(self, user=None):
        """ Update a BonitaUser.
        The BonitaUser muste already have been saved, and so has an UUID.

        """
        # for membership
        # http://www.bonitasoft.org/docs/javadoc/rest/5.9/API/identityAPI/setUserMemberships/%7BuserUUID%7D/index.html
        # for roles
        # http://www.bonitasoft.org/docs/javadoc/rest/5.9/API/identityAPI/setUserRoles/%7Busername%7D/index.html

        if self._uuid is None:
            raise BonitaException('must save BonitaUser before updating it')
        if self.is_unchanged:
            return

        # Look out if dictionnaries are dirties
        if self.personal_infos.is_modified:
            # Personal contact infos modified
            self._update_personal_contact_infos(user)

        if self.professional_infos.is_modified:
            # Professional contact infos modified
            self._update_professional_contact_infos(user)

        # Get dirties attributes
        dirties = self.get_dirties()

        # Some base attributes are dirty ?
        dirties_base_attributes = set(dirties).intersection(set(self.BASE_ATTRIBUTES))
        if len(dirties_base_attributes) > 0:
            self._update_base_attributes(user)

        # Password dirty ?
        if 'password' in dirties:
            self._update_password(user)

        # Mark as cleared of any modification
        self.clear()

    def _update_professional_contact_infos(self, user=None):
        """ Update professional contact infos of a BonitaUser:
        building, website, state, city, country, faxNumber, phoneNumber, email, address, zipCode,
        mobileNumber, room

        http://www.bonitasoft.org/docs/javadoc/rest/5.9/API/identityAPI/updateUserProfessionalContactInfo/index.html

        """
        if self._uuid is None:
            raise BonitaException('must save BonitaUser before updating it')
        if self.is_unchanged:
            return

        url = "/identityAPI/updateUserProfessionalContactInfo"

        data = dict()

        data['userUUID'] = self.uuid

        data['building'] = self.professional_infos.get('building','')
        data['website'] = self.professional_infos.get('website','')
        data['state'] = self.professional_infos.get('state','')
        data['city'] = self.professional_infos.get('city','')
        data['country'] = self.professional_infos.get('country','')
        data['faxNumber'] = self.professional_infos.get('faxNumber','')
        data['phoneNumber'] = self.professional_infos.get('phoneNumber','')
        data['email'] = self.professional_infos.get('email','')
        data['address'] = self.professional_infos.get('address','')
        data['zipCode'] = self.professional_infos.get('zipCode','')
        data['mobileNumber'] = self.professional_infos.get('mobileNumber','')
        data['room'] = self.professional_infos.get('room','')

        # Call the BonitaServer
        BonitaServer.get_instance().sendRESTRequest(url=url, user=user, data=data)

        # Mark as cleared of any modification
        self.professional_infos.clear_state()

    def _update_personal_contact_infos(self, user=None):
        """ Update personal contact infos of a BonitaUser:
        building, website, state, city, country, faxNumber, phoneNumber, email, address, zipCode,
        mobileNumber, room

        http://www.bonitasoft.org/docs/javadoc/rest/5.9/API/identityAPI/updateUserPersonalContactInfo/index.html#POST

        """
        if self._uuid is None:
            raise BonitaException('must save BonitaUser before updating it')
        if self.is_unchanged:
            return

        url = "/identityAPI/updateUserPersonalContactInfo"

        data = dict()

        data['userUUID'] = self.uuid

        data['building'] = self.personal_infos.get('building','')
        data['website'] = self.personal_infos.get('website','')
        data['state'] = self.personal_infos.get('state','')
        data['city'] = self.personal_infos.get('city','')
        data['country'] = self.personal_infos.get('country','')
        data['faxNumber'] = self.personal_infos.get('faxNumber','')
        data['phoneNumber'] = self.personal_infos.get('phoneNumber','')
        data['email'] = self.personal_infos.get('email','')
        data['address'] = self.personal_infos.get('address','')
        data['zipCode'] = self.personal_infos.get('zipCode','')
        data['mobileNumber'] = self.personal_infos.get('mobileNumber','')
        data['room'] = self.personal_infos.get('room','')

        # Call the BonitaServer
        BonitaServer.get_instance().sendRESTRequest(url=url, user=user, data=data)

        # Mark as cleared of any modification
        self.personal_infos.clear_state()

    def _update_password(self, user=None):
        """ Update password of a BonitaUser

        http://www.bonitasoft.org/docs/javadoc/rest/5.9/API/identityAPI/updateUserPassword/index.html

        """
        if self._uuid is None:
            raise BonitaException('must save BonitaUser before updating it')
        if self.is_unchanged:
            return

        url = "/identityAPI/updateUserPassword"

        data = dict()

        data['userUUID'] = self.uuid

        data['password'] = self.password

        # Call the BonitaServer
        BonitaServer.get_instance().sendRESTRequest(url=url, user=user, data=data)

        # Mark as cleared of any modification
        self.clear('password')

    BASE_ATTRIBUTES = ['lastname', 'title', 'username', 'firstname', 'jobtitle']

    def _update_base_attributes(self, user=None):
        """ Update base attributes of a BonitaUser :
        lastname, title, username, firstname, jobtitle
        
        # IMPROVE: add managerUserUUID, profileMetadata

        http://www.bonitasoft.org/docs/javadoc/rest/5.9/API/identityAPI/updateUserByUUID/index.html

        """
        if self._uuid is None:
            raise BonitaException('must save BonitaUser before updating it')
        if self.is_unchanged:
            return

        url = "/identityAPI/updateUserByUUID"

        data = dict()

        data['userUUID'] = self.uuid

        data['lastName'] = getattr(self,'last_name','')
        data['title'] = getattr(self,'title','')
        data['username'] = getattr(self,'username','')
        data['firstName'] = getattr(self,'first_name','')
        data['jobTitle'] = getattr(self,'job_title','')

        # Call the BonitaServer
        BonitaServer.get_instance().sendRESTRequest(url=url, user=user, data=data)

        # Mark as cleared of any modification
        for attribute in self.BASE_ATTRIBUTES:
            self.clear(attribute)

    @classmethod
    def get_by_username(cls, username):
        """ Retrieve a User with the username

        :param username: the username of the user to retrieve
        :type username: str

        """
        url = '/identityAPI/getUser/' + username

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
    def get_by_uuid(cls, uuid):
        """ Retrieve a User with the UUID

        :param uuid: the UUID of the user to retrieve
        :type uuid: str

        """
        url = '/identityAPI/getUserByUUID/' + uuid

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
    def get(cls, **kwargs):
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

    @classmethod
    def find(cls, **kwargs):
        """ Retrieve a list of User with given parameter

        If no parameter, retrieve all users in server.
        TODO accept some parameter like role, group
        Parameter can be any of :

        - role : BonitaRole
        - group : BonitaGroup

        :return: list of BonitaUser, possibly a void list
        :raise TypeError: if call with unknown parameter

        """
        if len(kwargs) == 0:
            # Get all Users
            return cls.find_all()
        elif 'role' in kwargs and 'group' in kwargs:
            return cls.find_by_role_and_group(role=kwargs['role'], group=kwargs['group'])
        elif 'role' in kwargs:
            return cls.find_by_role(kwargs['role'])
        elif 'group' in kwargs:
            return cls.find_by_group(kwargs['group'])
        else:
            raise TypeError('some param(s) not supported : %s' % (kwargs.keys()))

    @classmethod
    def find_all(cls):
        """ Retrieve all Users.

        :return: list of BonitaUser

        """
        url = "/identityAPI/getUsers"

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except Exception:
            raise

        # Decode the XML response
        soup = BeautifulSoup(xml, 'xml')

        users = []
        try:
            # Get the set of Users
            set_soup = xml_find(soup, 'set')

            users_tag = xml_find_all(set_soup, 'user')
            for user_tag in users_tag:
                user = BonitaUser._instanciate_from_xml(unicode(user_tag))
                users.append(user)

        except XMLSchemaParseError:
            raise

        return users

    @classmethod
    def find_by_role(cls, role):
        """ Retrieve all Users bound to a Role

        :param role: role the users must be bound to
        :type role: BonitaRole
        :return: list of BonitaUser
        :raise TypeError: if role not an instance of BonitaRole

        """
        if not isinstance(role, BonitaRole):
            raise TypeError('role must be a BonitaRole instance')

        url = "/identityAPI/getAllUsersInRole/" + role.uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except Exception:
            raise

        # Decode the XML response
        soup = BeautifulSoup(xml, 'xml')

        users = []
        try:
            # Get the list of Users
            list_soup = xml_find(soup, 'list')

            users_tag = xml_find_all(list_soup, 'user')
            for user_tag in users_tag:
                user = BonitaUser._instanciate_from_xml(unicode(user_tag))
                users.append(user)

        except XMLSchemaParseError:
            raise

        return users

    @classmethod
    def find_by_group(cls, group):
        """ Retrieve all Users bound to a Group

        :param group: group the users must be bound to
        :type group: BonitaGroup
        :return: list of BonitaUser
        :raise TypeError: if group not an instance of BonitaRole

        """
        if not isinstance(group, BonitaGroup):
            raise TypeError('group must be a BonitaGroup instance')

        url = "/identityAPI/getAllUsersInGroup/" + group.uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except Exception:
            raise

        # Decode the XML response
        soup = BeautifulSoup(xml, 'xml')

        users = []
        try:
            # Get the list of Users
            list_soup = xml_find(soup, 'list')

            users_tag = xml_find_all(list_soup, 'user')
            for user_tag in users_tag:
                user = BonitaUser._instanciate_from_xml(unicode(user_tag))
                users.append(user)

        except XMLSchemaParseError:
            raise

        return users

    @classmethod
    def find_by_role_and_group(cls, role, group):
        """ Retrieve all Users bound to a Role and a Group

        :param role: role the users must be bound to
        :type role: BonitaRole
        :param group: group the users must be bound to
        :type group: BonitaGroup
        :return: list of BonitaUser
        :raise TypeError: if group/role not an instance of BonitaGroup/BonitaRole

        """
        if not isinstance(group, BonitaGroup):
            raise TypeError('group must be a BonitaGroup instance')
        if not isinstance(role, BonitaRole):
            raise TypeError('role must be a BonitaRole instance')

        url = "/identityAPI/getAllUsersInRoleAndGroup/" + role.uuid + "/" + group.uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except Exception:
            raise

        # Decode the XML response
        soup = BeautifulSoup(xml, 'xml')

        users = []
        try:
            # Get the list of Users
            list_soup = xml_find(soup, 'list')

            users_tag = xml_find_all(list_soup, 'user')
            for user_tag in users_tag:
                user = BonitaUser._instanciate_from_xml(unicode(user_tag))
                users.append(user)

        except XMLSchemaParseError:
            raise

        return users


class BonitaGroup(BonitaObject):
    """ A class to map a group in Bonita.

    """

    def __init__(self, name, label, description, parent=None):
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

        if parent is not None and not isinstance(parent, BonitaGroup):
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
        if not isinstance(xml, (str, unicode)):
            raise TypeError('xml must be a string or unicode not %s' % (type(xml)))

        soup = BeautifulSoup(xml, 'xml')

        try:
            # First thing first : instanciate a new BonitaGroup
            group_soup = xml_find(soup, 'parentGroup') if is_parent else xml_find(soup, 'group')
        except XMLSchemaParseError:
                raise BonitaXMLError('xml does not seem to be for a Group')

        try:
            description = xml_find(group_soup, 'description').string
            name = xml_find(group_soup, 'name').string
            label = xml_find(group_soup, 'label').string

            new_group = BonitaGroup(name, label, description)

            # Main properties now
            new_group.uuid = xml_find(group_soup, 'uuid').string

            # Other properties then
            set_if_available(new_group, group_soup, ['dbid'])

            # Parent hierarchy
            parent_soup = xml_find(group_soup, 'parentGroup', raise_exception=False)
            if parent_soup is not None:
                new_group.parent = cls._instanciate_from_xml(unicode(parent_soup), is_parent=True)
        except XMLSchemaParseError:
            raise

        return new_group

    @classmethod
    def get_by_path(cls, path):
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
            xml = BonitaServer.get_instance().sendRESTRequest(url=url, data=data)
        except BonitaHTTPError as err:
            if 'GroupNotFoundException'.lower() in err.bonita_exception.lower():
                return None
            else:
                raise

        group = cls._instanciate_from_xml(xml)

        return group

    @classmethod
    def get_by_uuid(cls, uuid):
        """ Retrieve a Group with the UUID

        :param uuid: the UUID of the group to retrieve
        :type uuid: str

        """
        url = '/identityAPI/getGroupByUUID/' + uuid

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
    def get(cls, **kwargs):
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

    def __init__(self, name, label, description):
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
        if not isinstance(xml, (str, unicode)):
            raise TypeError('xml must be a string or unicode not %s' % (type(xml)))

        soup = BeautifulSoup(xml, 'xml')

        try:
            # First thing first : instanciate a new BonitaRole
            role_soup = xml_find(soup, 'role')

            description = xml_find(role_soup, 'description').string
            name = xml_find(role_soup, 'name').string
            label = xml_find(role_soup, 'label').string

            new_role = BonitaRole(name, label, description)

            # Main properties now
            new_role.uuid = xml_find(role_soup, 'uuid').string

            # Other properties then
            set_if_available(new_role, role_soup, ['dbid'])

        except XMLSchemaParseError:
            raise

        return new_role

    @classmethod
    def get_by_name(cls, name):
        """ Retrieve a Role with the name

        :param path: the name of the role to retrieve
        :type path: str

        """
        url = '/identityAPI/getRole/' + name

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
    def get_by_uuid(cls, uuid):
        """ Retrieve a Role with the UUID

        :param uuid: the UUID of the role to retrieve
        :type uuid: str

        """
        url = '/identityAPI/getRoleByUUID/' + uuid

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
    def get(cls, **kwargs):
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

    def __init__(self, role, group):
        """ Build up a new BonitaMembership

        :param role: the role bound to this membership
        :type role: BonitaRole instance
        :param group: the group bound to this membership
        :type group: BonitaGroup instance
        :raise TypeError: if role is not a BonitaRole instance
        :raise TypeError: if group is not a BonitaGroup instance

        """
        if not isinstance(role, BonitaRole):
            raise TypeError('role must be a BonitaRole instance')
        if not isinstance(group, BonitaGroup):
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
        if not isinstance(xml, (str, unicode)):
            raise TypeError('xml must be a string or unicode not %s' % (type(xml)))

        soup = BeautifulSoup(xml, 'xml')

        try:
            membership_soup = xml_find(soup, 'membership')

            # First try to decode Role and Group
            try:
                group_soup = xml_find(membership_soup, 'group')
                group = BonitaGroup._instanciate_from_xml(unicode(group_soup))
            except XMLSchemaParseError:
                raise BonitaXMLError('can\'t properly creat a group from XML')

            try:
                role_soup = xml_find(membership_soup, 'role')
                role = BonitaRole._instanciate_from_xml(unicode(role_soup))
            except XMLSchemaParseError:
                raise BonitaXMLError('can\'t properly creat a role from XML')

            new_membership = BonitaMembership(role, group)

            # Main properties now
            new_membership.uuid = xml_find(membership_soup, 'uuid').string

            # Other properties then
            set_if_available(new_membership, membership_soup, ['dbid'])
        except:
            raise

        return new_membership

#<Membership>
#  <dbid>0</dbid>
#  <uuid>1c5dac3a-d54c-4d94-8dad-46e7ac32720a</uuid>
#  <role class="Role">
#    <description>The user role</description>
#    <dbid>0</dbid>
#    <uuid>03d22c81-d41c-4b1b-b6d5-7bb944aeaea4</uuid>
#    <name>user</name>
#    <label>User</label>
#  </role>
#  <group class="Group">
#    <description>Responsables d&apos;entreprise pour les Services communs</description>
#    <dbid>0</dbid>
#    <uuid>40ea29d1-5abc-44ca-a6b1-159977e0b6d6</uuid>
#    <name>responsables_entreprise</name>
#    <label>responsables_entreprise</label>
#    <parentGroup class="Group">
#      <description>The default group : ave un texte Ã©&amp;&apos;Ã¨`-[{}$Ã¹%&amp; blabla</description>
#      <dbid>0</dbid>
#      <uuid>c18bb42b-2fee-4a08-9ab6-fe61d3be726e</uuid>
#      <name>platform</name>
#      <label>Platform</label>
#    </parentGroup>
#  </group>
#</Membership>

    @classmethod
    def get_by_role_and_group_uuid(cls, role_uuid, group_uuid):
        """ Retrieve a Membership with the role and group UUID.
        If membership does not exists but role and group exist, the membership will be created

        :param role_uuid: UUID of the role bound to the membership
        :type role_uuid: str or unicode
        :param group_uuid: UUID of the group bound to the membership
        :type group_uuid: str or unicode

        """
        url = '/identityAPI/getMembershipForRoleAndGroup/' + role_uuid + '/' + group_uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            err_string = err.bonita_exception.lower()
            rnf_exc_string = 'RoleNotFoundException'.lower()
            gnf_exc_string = 'GroupNotFoundException'.lower()
            if (rnf_exc_string in err_string or gnf_exc_string in err_string):
                return None
            else:
                raise

        membership = cls._instanciate_from_xml(xml)

        return membership

    @classmethod
    def get_by_role_and_group(cls, role, group):
        """ Retrieve a Membership with the role and group.
        If membership does not exists but role and group exist, the membership will be created

        :param role: role bound to the membership
        :type role: BonitaRole
        :param group: group bound to the membership
        :type group: BonitaGroup

        """
        if not isinstance(role, BonitaRole):
            raise TypeError('role must be a BonitaRole instance')
        if not isinstance(group, BonitaGroup):
            raise TypeError('group must be a BonitaGroup')

        url = '/identityAPI/getMembershipForRoleAndGroup/' + role.uuid + '/' + group.uuid

        try:
            xml = BonitaServer.get_instance().sendRESTRequest(url=url)
        except BonitaHTTPError as err:
            err_string = err.bonita_exception.lower()
            rnf_exc_string = 'RoleNotFoundException'.lower()
            gnf_exc_string = 'GroupNotFoundException'.lower()
            if (rnf_exc_string in err_string or gnf_exc_string in err_string):
                return None
            else:
                raise

        membership = cls._instanciate_from_xml(xml)

        return membership

    @classmethod
    def get_by_uuid(cls, uuid):
        """ Retrieve a Membership with the UUID

        :param uuid: the UUID of the membership to retrieve
        :type uuid: str

        """
        url = '/identityAPI/getMembershipByUUID/' + uuid

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
    def get(cls, **kwargs):
        """  Retrieve a Membership with given parameter

        Parameter can be any of :

        - role and group
        - role_uuid and group_uuid
        - uuid

        :raise TypeError: if call with unknown parameter
        :return: BonitaMembership instance or None if not found

        """
        if 'role' in kwargs and 'group' in kwargs:
                return cls.get_by_role_and_group(role=kwargs['role'], group=kwargs['group'])
        if 'role_uuid' in kwargs and 'group_uuid' in kwargs:
                return cls.get_by_role_and_group_uuid(role_uuid=kwargs['role_uuid'], group_uuid=kwargs['group_uuid'])
        if 'uuid' in kwargs:
            return cls.get_by_uuid(uuid=kwargs['uuid'])

        raise TypeError('called get with unknown param : %s' % (kwargs.keys()))
