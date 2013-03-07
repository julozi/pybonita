#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup, Tag
from unittest import TestCase

__all__ = ['TestWithBonitaServer','TestWithMockedServer',
    'build_dumb_bonita_error_body','build_bonita_user_xml',
    'build_bonita_group_xml','build_bonita_role_xml',
    'build_bonita_membership_xml']


class TestWithBonitaServer(TestCase):

    def __init__(self,methodName='runTest'):
        import pybonita
        pybonita.BonitaServer = pybonita.BonitaServer
        super(TestWithBonitaServer,self).__init__(methodName)


class TestWithMockedServer(TestCase):

    def __init__(self,methodName='runTest'):
        from pybonita import BonitaServer
        import pybonita.tests
        BonitaServer._instance = pybonita.tests.BonitaMockedServerImpl()
        BonitaServer.__metaclass__ = pybonita.tests._MetaBonitaMockedServer
        BonitaServer.set_response_list = set_response_list
        super(TestWithMockedServer,self).__init__(methodName)


class _MetaBonitaMockedServer(type):

    def __instancecheck__(self, inst):
        return isinstance(inst, BonitaMockedServerImpl)


class BonitaMockedServerImpl(object):

    __metaclass__ = _MetaBonitaMockedServer

    def __init__(self):
        self._user = "john"
        self._host = None
        self._port = None
        self._login = None
        self._password = None
        self._ready = False

    def sendRESTRequest(self, url, user=None, data=dict()):
        """ Do not call a BonitaServer, but rather access the reponses list given prior to this method call.

        """
        import re
        from requests import codes
        from pybonita.exception import BonitaHTTPError

        (status, content_type, data) = self.__class__.extract_response(url,'POST')

        if status != str(codes.ok):
            soup = BeautifulSoup(data,'xml')
            if soup == None:
                raise Exception('data : %s[%s] and can\'t build soup with that' % (str(data),type(data)))
            soup_exception = soup.find(name=re.compile("exception"))
            bonita_exception = soup_exception.name
            message = soup.detailMessage
            code = soup.errorCode
            raise BonitaHTTPError(bonita_exception,code,message)

        return data

    def _get_host(self):
        return self._host

    def _set_host(self, value):
        if type(value) != str:
            raise TypeError(u"host must be a string")

        self._host = value

    host = property(_get_host, _set_host, None, u"Bonita REST API server host")

    def _get_port(self):
        return self._port

    def _set_port(self, value):
        if type(value) != int:
            raise TypeError(u"port must be an integer")

        self._port = value

    port = property(_get_port, _set_port, None, u"Bonita REST API server port")

    def _get_login(self):
        return self._login

    def _set_login(self, value):
        if type(value) != str:
            raise TypeError(u"login must be a string")

        self._login = value

    login = property(_get_login, _set_login, None, u"Bonita REST request credential login")

    def _get_password(self):
        return self._password

    def _set_password(self, value):

        if type(value) != str:
            raise TypeError

        self._password = value

    password = property(_get_password, _set_password, None, u"Bonita REST request credential password")


    class ResponseList(object):
        # Internal singleton class for responses list

        def __init__(self):
            self.responses = {}

        def clear_responses(self):
            self.responses = {}

        def add_or_augment_response_list(self,url,method,status,type,message):
            if not (url,method) in self.responses:
                self.responses[(url,method)] = [{'status':status,'type':type,'message':message}]
            else:
                # Add the new entry at end of list of responses for the current (url,method)
                self.responses[(url,method)].append({'status':status,'type':type,'message':message})

        def get_responses(self):
            return self.responses

        def search_and_consume_reponse(self,full_url,method):
            """

            """
            # Look for url,method in MockedServer responses
            from requests.packages import urllib3

            parse = urllib3.util.parse_url(full_url).path
            split_parse = parse.split('/')

            n = len(split_parse)
            while n > 0 and ('/'.join(split_parse[0:n]),'POST') not in self.responses:
                n -= 1

            if n == 0:
                raise Exception('No already sets response for url %s and method %s' % (parse,method))

            url_parse = '/'.join(split_parse[0:n])
            # Extract the first response in row
            url_method_responses = self.responses.pop((url_parse,method))
            current_response = url_method_responses[0]

            if len(url_method_responses) > 1:
                self.responses[(url_parse,method)] = url_method_responses[1:]

            status = str(current_response['status'])
            data = current_response['message']

            if current_response['type'] != None or current_response['type'] != '':
                content_type = current_response['type']
            elif (current_response['type'] == None or current_response['type'] == '') and isinstance(data,(str,unicode)):
                content_type = 'text/html'
            else:
                raise Exception('content_type not specified for url %s method %s' % (url_parse,method))

            return status, content_type, data

    response_list_instance = None

    @classmethod
    def clear_response_list(cls):
        response_list = cls.get_response_list()
        response_list.clear_responses()

    @classmethod
    def left_responses_in_list(cls):
        return len(cls.get_response_list().get_responses()) > 0

    @classmethod
    def get_response_list(cls):
        if cls.response_list_instance == None:
            cls.response_list_instance = cls.ResponseList()

        return cls.response_list_instance

    @classmethod
    def extract_response(cls,url,method):
        """ Retrieve a response from already sets response list

        """
        if len(cls.get_response_list().get_responses()) == 0:
            # No already set response
            raise Exception('No prepared response list')
        else:
            # Already set responses : find the good one
            status,content_type,data = cls.get_response_list().search_and_consume_reponse(url,method)

        return status,content_type,data

@classmethod
def set_response_list(cls,response_list):
    """ Set the response list for next requests.

    :param list: List of entries as detailled after
    :raise: ValueError if response_list is not a list and each entry does not belong to the correct schema

    An Entry is a dict containing :
    :base_url: base URL the Request will be call (any further params will be ignored)
    :method: the HTTP method of the Request. If not specified, default will be POST
    :status: the HTTP response status
    :type: the HTTP response mime type. If not specified, default will be xml
    :message: the HTTP response body

    An Entry could also be a list of only 3 params :
    :0: base_url
    :1: status
    :2: message

    """
    if not isinstance(response_list,list):
        raise ValueError('response_list arg must be a list')

    # Run through the responses
    for response in response_list:
        if not isinstance(response,(list,dict)):
            raise ValueError('response_list entry must be a list or dict')

        if isinstance(response,list):
            if len(response) != 3:
                raise ValueError('response_list entry must have 3 fields')

            # Grab each fields
            url = response[0]
            method = 'POST'
            status = response[1]
            type = 'xml'
            message = response[2]

        else:
            # response is a dict
            url = response.get('base_url')
            method = response.get('method','POST')
            status = response.get('status')
            type = response.get('type','xml')
            message = response.get('message')

        response_list = BonitaMockedServerImpl.get_response_list()
        response_list.add_or_augment_response_list(url,method,status,type,message)


from pybonita.user import BonitaGroup, BonitaRole

def build_dumb_bonita_error_body(exception='',code='',message=''):
    # Add your own Bonita java Exception in this dict to make your call shorter
    # So you can call with exception='UserNotFoundException'
    # rather than exception = 'org.ow2.bonita.facade.exception.UserNotFoundException'
    java_exception_dict = {'UserNotFoundException':'org.ow2.bonita.facade.exception.UserNotFoundException',
                           'ProcessNotFoundException':'org.ow2.bonita.facade.exception.ProcessNotFoundException',
                           'GroupNotFoundException':'org.ow2.bonita.facade.exception.GroupNotFoundException',
                           'RoleNotFoundException':'org.ow2.bonita.facade.exception.RoleNotFoundException'}
    exception_text = java_exception_dict.get(exception,exception)

    # Build XML body
    soup = BeautifulSoup('','xml')
    tag_exception = soup.new_tag(exception_text)
    tag_code = soup.new_tag('errorCode')
    tag_message = soup.new_tag('detailMessage')

    tag_code.string = code
    tag_message.string = message

    soup.insert(0,tag_exception)
    tag_exception.insert(0,tag_code)
    tag_exception.insert(1,tag_message)

    return unicode(soup)

def build_bonita_user_xml(uuid,password='',username=''):
    """ Build XML for a Bonita User information """
    # Build XML body
    soup = BeautifulSoup('','xml')
    tag_user = soup.new_tag('user')
    tag_uuid = soup.new_tag('uuid')
    tag_password = soup.new_tag('password')
    tag_username = soup.new_tag('username')

    tag_uuid.string = uuid
    tag_password.string = password
    tag_username.string = username
    user_tags = [tag_uuid,tag_password,tag_username]

    for tag in user_tags:
        tag_user.append(tag)

    return unicode(tag_user)

def build_bonita_group_xml(uuid, name, description='', label='', dbid='', parent=None, as_parent=False, with_class=False):
    """ Build XML for a Bonita Group information 

    :param uuid:
    :type uuid:
    :param name:
    :type name:
    :param description:
    :type description:
    :param label:
    :type label:
    :param dbid:
    :type dbid:
    :param parent: parent of this Group, rather as a BonitaGroup or by XML
    :type parent: BonitaGroup ou unicode
    :param as_parent: State that the XML group must be provided as a parentGroup (default False)
    :type as_parent: bool

    """
    # Build XML body
    soup = BeautifulSoup('','xml')

    if as_parent:
        tag_group = soup.new_tag('parentGroup')
    else:
        tag_group = soup.new_tag('Group')

    if as_parent or with_class:
        tag_group.attrs['class']='Group'

    tag_uuid = soup.new_tag('uuid')
    tag_description = soup.new_tag('description')
    tag_name =soup.new_tag('name')
    tag_label = soup.new_tag('label')
    tag_dbid = soup.new_tag('dbid')

    tag_uuid.string = uuid
    tag_description.string = description
    tag_name.string = name
    tag_label.string = label
    tag_dbid.string = dbid
    group_tags = [tag_uuid,tag_description,tag_name,tag_label,tag_dbid]

    for tag in group_tags:
        tag_group.append(tag)

    if parent:
        if isinstance(parent,BonitaGroup):
            # Build parent XML definition
            parent_xml = build_bonita_group_xml(parent.uuid, parent.name, parent.description, parent.label,parent.parent, True)
        else:
            # parent XML is directly in parent
            parent_xml = parent

        parent_soup = BeautifulSoup(parent_xml,'xml')
        tag_group.append(parent_soup.parentGroup)

    return unicode(tag_group)

def build_bonita_process_definition_xml(uuid, name=None, version=None, label=None, description=None):

    soup = BeautifulSoup('','xml')

    tag_process = soup.new_tag("ProcessDefinition")

    tag_description = soup.new_tag("description")
    tag_description.string = description if description != None else "%s description" % uuid

    tag_name = soup.new_tag("name")
    tag_name.string = name if name != None else uuid.split("--")[0]

    tag_label = soup.new_tag("label")
    tag_label.string = label if label != None else uuid.split("--")[0]

    tag_uuid = soup.new_tag("uuid")
    tag_value = soup.new_tag("value")
    tag_value.string = uuid
    tag_uuid.append(tag_value)

    tag_version = soup.new_tag("version")
    tag_version.string = version if version != None else uuid.split("--")[1]

    process_tags = [tag_description, tag_name, tag_label, tag_uuid, tag_version]

    for tag in process_tags:
        tag_process.append(tag)

    return unicode(tag_process)

def build_bonita_role_xml(uuid,name,description='',label='',dbid='',with_class=False):
    """ Build XML for a Bonita Role information """
    # Build XML body
    soup = BeautifulSoup('','xml')

    tag_role = soup.new_tag('Role')
    if with_class:
        tag_role.attrs['class']='Role'

    tag_uuid = soup.new_tag('uuid')
    tag_name = soup.new_tag('name')
    tag_description = soup.new_tag('description')
    tag_label = soup.new_tag('label')
    tag_dbid = soup.new_tag('dbid')

    tag_uuid.string = uuid
    tag_name.string = name
    tag_description.string = description
    tag_label.string = label
    tag_dbid.string = dbid

    role_tags = [tag_uuid,tag_name,tag_description,tag_label,tag_dbid]

    for tag in role_tags:
        tag_role.append(tag)

    return unicode(tag_role)

def build_bonita_membership_xml(uuid,role,group, dbid=''):
    """ Build XML for a Bonita Membership information """
    # Build XML body
    soup = BeautifulSoup('','xml')

    tag_membership = soup.new_tag('Membership')
    tag_uuid = soup.new_tag('uuid')
    tag_dbid = soup.new_tag('dbid')

    tag_uuid.string = uuid
    tag_dbid.string = dbid
    membership_tags = [tag_uuid,tag_dbid]

    for tag in membership_tags:
        tag_membership.append(tag)

    if isinstance(group,BonitaGroup):
        # Build group XML definition
        group_xml = build_bonita_group_xml(group.uuid, group.name, group.description, group.label,group.parent,with_class=True)
    else:
        # group XML is directly in group param
        group_xml = group

    group_soup = BeautifulSoup(group_xml,'xml')
    tag_membership.append(group_soup.Group)

    if isinstance(role,BonitaGroup):
        # Build group XML definition
        role_xml = build_bonita_role_xml(role.uuid,role.name,role.description,role.label,role.dbid,with_class=True)
    else:
        # group XML is directly in group param
        role_xml = role

    role_soup = BeautifulSoup(role_xml,'xml')
    tag_membership.append(role_soup.Role)

    return unicode(tag_membership)
