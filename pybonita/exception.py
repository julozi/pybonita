# -*- coding: utf-8 -*-

__all__ = ['BonitaException','BonitaServerNotInitializedError',
    'ServerNotReachableError','UnexpectedResponseError','BonitaHTTPError']


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

class BonitaHTTPError(BonitaException):
    """ Bonita HTTP Error.

    Bonita Server always return a 500 error code, with a body containing XML
    with real HTTP error code and message (RFC are only made for dogs & cats)

    This class embed the HTTP Error code, a message, and the Java exception 
    class provided by the Bonita server.

    """
    _base_message = 'HTTP Error from Bonita Server'

    def __init__(self,bonita_exception='',code='',message=''):
        self.bonita_exception = bonita_exception
        self.code = code
        self.message = message

        err_info = ' HTTP[%s] : %s' % (code,message)
        
        super(BonitaHTTPError,self).__init__(err_info)

