# -*- coding: utf-8 -*-

__all__ = ['server', 'BonitaObject']

server = BonitaServer()

class BonitaObject:
    """ All Bonita's entities inherit from BonitaObject """

    def __init__(self, server):
        pass


class BonitaServer:
    """
    A BonitaServer instance is required to establish a connection with a
    Bonita REST server

    """

    host = None
    username = None
    password = None

    def __init__(self):
        pass

    def connect(host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def sendRESTRequest(self, url, data, user):

        data = dict()
        data['options'] = u"user:%s" % user
        # add data from method params

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(host+url, data=data, headers=headers, auth=HTTPBasicAuth(self.username, self.password))

        if response.status_code != requests.codes.ok:
            raise Exception