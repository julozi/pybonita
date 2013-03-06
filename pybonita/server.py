# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, UnicodeDammit

import requests
from requests.auth import HTTPBasicAuth

from pybonita import logger
from .exception import BonitaServerNotInitializedError,ServerNotReachableError,\
    UnexpectedResponseError, BonitaHTTPError

__all__ = ['BonitaServer']


class _MetaBonitaServer(type):

    def __instancecheck__(self, inst):
        return isinstance(inst, BonitaServer._BonitaServerImpl)

class BonitaServer:
    """ Singleton object to declare Bonita server to be used


    BonitaServer is a singleton object used by all BonitaObject within the
    pybonita package.

    You can't instanciate BonitaServer.
    To get the unique BonitaServer instance please use the static get_instance
    method.

    """

    __metaclass__ = _MetaBonitaServer

    class _BonitaServerImpl(object):

        def __init__(self):
            self._user = "john"
            self._host = None
            self._port = None
            self._login = None
            self._password = None
            self._charsets= []
            self._ready = False

        def sendRESTRequest(self, url, user=None, data=dict()):

            if self._ready == False:
                raise BonitaServerNotInitializedError

            user = user if user != None else self._user

            if data is None:
                data = dict()
            elif type(data) != dict:
                raise TypeError

            data['options'] = u"user:%s" % user

            headers = {'content-type': 'application/x-www-form-urlencoded'}
            full_url = 'http://%s:%s/bonita-server-rest/API%s' % (self.host, self.port, url)

            try:
                response = requests.post(full_url, data=data, headers=headers, auth=HTTPBasicAuth(self.login, self.password))
            except ConnectionError, Timeout:
                raise ServerNotReachableError
            except HTTPError:
                raise UnexpectedResponseError

            if response.status_code != requests.codes.ok:
                # Bonita Server always return a 500 (yes, i'm not joking. What are RFC made for ?!)
                # with a body containing XML with 2 interesting fields :
                # - <errorCode></errorCode> : the real error code, for example 404
                # - <detailMessage></detailMessage> : message describing the problem
                if response.status_code == 500:
                    import re
                    soup = BeautifulSoup(response.text,'xml')
                    bonita_exception = soup.find(name=re.compile("exception")).name
                    message = soup.detailmessage.text
                    code = int(soup.errorCode.text) if soup.errorCode != None else 500
                    if code != None or message != None:
                        raise BonitaHTTPError(bonita_exception=bonita_exception,code=code,message=message)
                    else:
                        raise UnexpectedResponseError

            # Convert response to unicode, using UnicodeDammit
            # Try to extract content-type from XML
            # No way ! Bonita does not return even a proper content-type, only text/*
            # Try to guess what is the charset
            dammit = UnicodeDammit(response.text,self.charsets)
            unicode_response = dammit.unicode_markup

            return unicode_response

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

    @classmethod
    def get_instance(cls):
        """ Returns the singleton instance of BonitaServer

        Upon its first call, it creates a new instance of the BonitaServer
        implementation class
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return cls._instance
        except AttributeError:
            cls._instance = cls._BonitaServerImpl()
            return cls._instance

    @classmethod
    def use(cls, host, port, login, password,charsets=[]):
        """ Set the connexion params to the BonitaServer

        Returns the unique BonitaServer instance

        :param host: Bonita REST API server host
        :type host: str
        :param port: Bonita REST API server port
        :type port: int
        :param login: Bonita REST request credential login
        :type login: str
        :param password: Bonita REST request credential password
        :type password: str
        :param charsets: List of charsets the Bonita Server could use to encode (to unicode)
        :type charsets: list of str

        """

        server = cls.get_instance()
        server.host = host
        server.port = port
        server.login = login
        server.password = password
        server.charsets = charsets
        server._ready = True

        return server

    def __init__(self):
        raise TypeError('BonitaServer must be accessed through `get_instance()`.')

