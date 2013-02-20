# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulStoneSoup

from pybonita.server import BonitaServer

__all__ = ['BonitaObject']


class BonitaObject(object):
    """ All Bonita's entities inherit from BonitaObject """

    def __init__(self, uuid):
        self.uuid = uuid

    def __str__(self):
        return "%s %s" % (self.__class__, self.uuid)

    def save(self, user=None, variables=None):
        """ Save a BonitaObject : sends data to create a resource on the Bonita server.

        """

        # Delegate generation of URL to subclasses
        (url,data) = self._generate_save_url(variables)

        # Call the BonitaServer
        xml = BonitaServer.get_instance().sendRESTRequest(url=url, user=user, data=data)

        # Extract UUID of newly created object
        soup = BeautifulStoneSoup(xml)
        instances = soup.findAll("uuid")
        if len(instances) != 1:
            raise Exception #fixme: raise clear Exception
        self.uuid = instances[0].text

    def delete(self, user=None):
        """ Delete a BonitaObject : remove it from the Bonita server

        """

        (url,data) = self._generate_delete_url()

        # Call the BonitaServer
        xml = BonitaServer.get_instance().sendRESTRequest(url = url, user=user, data=data)

        #TODO Test return code for completion

    def _generate_save_url(self,variables):
        """ Generate URL and data to used to call Bonita server to perform a save operation.
        You must define this method when you want to provide a save method.

        """
        raise NotImplementedError

    def _generate_delete_url(self):
        """ Generate URL and data to used to call Bonita server to perform a delete operation.
        You must define this method when you want to provide a delete method.

        """
        raise NotImplementedError

