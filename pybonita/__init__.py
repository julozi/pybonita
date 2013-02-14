# -*- coding: utf-8 -*-
import logging

import requests
from requests.auth import HTTPBasicAuth
from xml.dom.minidom import parseString

__all__ = ['BonitaObject', 'BonitaServer', 'logger']

logger = logging.getLogger(__name__)

class BonitaObject(object):
    """ All Bonita's entities inherit from BonitaObject """

    server = None

    def __init__(self, uuid):
        self.uuid = uuid

    def __str__(self):
        return "%s %s" % (self.__class__, self.uuid)

    def save(self, user=None, variables=None):
        """ Save a BonitaObject : sends data to create a resource on the Bonita server.
        
        """
        user = user if user != None else self.server.user
        
        # Delegate generation of URL to subclasses
        (url,data) = self._generate_save_url(variables)
        data['options'] = u"user:"+user
        
        # Call the BonitaServer
        xml = self.server.sendRESTRequest(url=url, user=user, data=data)
        
        # Extact UUID of newly created object
        dom = parseString(xml)
        instances = dom.getElementsByTagName("uuid")
        if len(instances) != 1:
            raise Exception #fixme: raise clear Exception
        self.uuid = instances[0].childNodes[0].data
    
    def delete(self, user=None):
        """ Delete a BonitaObject : remove it from the Bonita server
        
        """
        user = user if user != None else self.server.user
        
        (url,data) = self._generate_delete_url()
        data['options'] = u"user:"+user
        
        # Call the BonitaServer
        xml = self.server.sendRESTRequest(url = url, user=user, data=data)
        
        #TODO Test return code for completion
    
    def _generate_save_url(self,variables):
        """ Generate URL and data to used to call Bonita server to perform a save operation.
        You must define this method when you want to provide a save method.
        
        """
        raise NotImplementedError
    
    def _generate_delete_url(self,variables):
        """ Generate URL and data to used to call Bonita server to perform a delete operation.
        You must define this method when you want to provide a delete method.
        
        """
        raise NotImplementedError
    

class BonitaServer:
    """
    A BonitaServer instance is required to establish a connection with a
    Bonita REST server

    """

    host = None
    username = None
    password = None
    
    user = u"john"

    @classmethod
    def connect(cls, host, port, username, password):
        """
        Instanciate a BonitaServer object and define it as the server singleton
        for all BonitaObject

        """

        #fixme: we should check that the host is responding or raise an
        #exception

        BonitaObject.server = BonitaServer(host, port, username, password)

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def sendRESTRequest(self, url, user, data=dict()):

        post_data = dict()
        post_data['options'] = u"user:%s" % user
        post_data.update(data)

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        full_url = 'http://%s:%s/bonita-server-rest/API%s' % (self.host, self.port, url)

        response = requests.post(full_url, data=post_data, headers=headers, auth=HTTPBasicAuth(self.username, self.password))

        if response.status_code != requests.codes.ok:
            print response.text

        return response.text
