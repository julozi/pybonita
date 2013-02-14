# -*- coding: utf-8 -*-

import logging

import requests
from requests.auth import HTTPBasicAuth

__all__ = ['BonitaObject', 'BonitaServer', 'logger']

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BonitaObject(object):
    """ All Bonita's entities inherit from BonitaObject """

    server = None

    def __init__(self, uuid):
        self.uuid = uuid

    def __str__(self):
        return "%s %s" % (self.__class__, self.uuid)


class BonitaServer:
    """
    A BonitaServer instance is required to establish a connection with a
    Bonita REST server

    """

    host = None
    username = None
    password = None

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