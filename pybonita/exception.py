# -*- coding: utf-8 -*-

__all__ = ['BonitaException','BonitaServerNotInitializedError',
    'ServerNotReachableError','UnexpectedResponseError']


class BonitaException(Exception):
    """ Base class for exception raised in this package """
    def __init__(self,err_info=None):
        self.err_info = err_info
        
        message = self.__class__._base_message + (' '+str(err_info) if err_info != None else '')
        
        super(BonitaException,self).__init__(message)

class BonitaServerNotInitializedError(BonitaException):
    """ BonitaServer has not been initialized prior to any action """
    _base_message = 'BonitaServer not initialized'

class ServerNotReachableError(BonitaException):
    """ Bonita server is not reachable """
    _base_message = 'unable to reach Bonita server'

class UnexpectedResponseError(BonitaException):
    """ Response from Bonita server is unexpected """
    _base_message = 'unexpected server response'

