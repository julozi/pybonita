# -*- coding: utf-8 -*-

from pybonita import logger
from pybonita.object import BonitaObject
from pybonita.utils import dictToMapString

__all__ = ['BonitaUser','BonitaGroup','BonitaRole','BonitaMembership']


class BonitaUser(BonitaObject):
    """ A class to map a user in Bonita.
    
    """
    
    def __init__(self,username,password,membership=None,role=None,group=None,**kwargs):
        """ Add a new user in Bonita.
        
        At least username and password must be provided.
        
        :param username: username to use
        :type username: str
        :param password: password to set
        :type paswword: str
        
        """
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

    
    def setManager(self,user):
        """ Define the Manager of a user 
        
        :param user: the manager to set with
        :type user: BonitaUser
        :raise ValueError: manager user is unknown in BonitaServer
        """
        pass
    
    def setDelegee(self,user):
        """ Define the Delegee of a user 
        
        :param user: the delegee to set with
        :type user: BonitaUser
        :raise ValueError: delegee user is unknown in BonitaServer
        """
        pass
    
    @classmethod
    def get_user_by_username(cls,username):
        pass
    
    @classmethod
    def get_user_by_uuid(cls,uuid):
        pass
    
    @classmethod
    def get_user(cls,**kwargs):
        if 'username' in kwargs:
            return cls.get_user_by_username(username=kwargs['username'])
        if 'uuid' in kwargs:
            return cls.get_user_by_uuid(uuid=kwargs['uuid'])
        
        raise TypeError('called getUser with unknown param : %s' % (kwargs.keys()))
    
    # setter par parametre
    # par exemple on fait :
    # user = BonitaUser(login,pass)
    # puis on peut faire user.firstname = 'coucou' et ca mets a jour le champs firstname directement

class BonitaGroup(BonitaObject):
    """ A class to map a group in Bonita.
    
    """
    
    def __init__(self,name,label,description,parent=None):
        pass
    
    def setParent(self,parent):
        pass
    
    def _get_path(self):
        pass
    
    path = property(_get_path,None,None)

class BonitaRole(BonitaObject):
    """ A class to map a role in Bonita.
    
    """
    
    def __init__(self,name):
        self.name = name
    
    def _generate_save_url(self,variables):
        url = "/identityAPI/addRole/"+self.name
        data = None
        
        return (url,data)
    
    def _generate_delete_url(self,variables):
        url = "/identityAPI/removeRole/"+self.name
        data = None
        
        return (url,data)
    
    @classmethod
    def getRoleByName(cls,name):
        """ Retrieve a role given a name """
        url = "/identityAPI/getRole/"+name
        pass
    
    @classmethod
    def getRoleByUUID(cls,uuid):
        pass
    
    @classmethod
    def getRole(cls,**kwargs):
        pass
    

class BonitaMembership(BonitaObject):
    """ A class to map a membership in Bonita.
    
    """
    
    @classmethod
    def getMembershipByRoleAndGroup(cls,role,group):
        """ Retrieve a membership given a role and a group 
        
        :param role:
        :type role: BonitaRole
        :param group:
        :type group: BonitaGroup
        :raise Exception: if role or group is unknwo on server
        
        TODO Return None or Raise exception if no membership found ?
        
        """
        pass
    
    @classmethod
    def getMembershipByUUID(cls,uuid):
        pass
    
    @classmethod
    def getMembership(cls,**kwargs):
        pass

