#-*- coding: utf-8 -*-


from pybonita import BonitaServer
from unittest import TestCase

__all__ = ['BonitaMockedServer','TestWithBonitaServer','TestWithMockedServer']


class TestWithBonitaServer(TestCase):
    
    def __init__(self,methodName='runTest'):
        import pybonita
        pybonita.BonitaServer = pybonita.BonitaServer
        super(TestWithMockedServer,self).__init__(methodName)

class TestWithMockedServer(TestCase):

    def __init__(self,methodName='runTest'):
        import pybonita.tests
        pybonita.BonitaServer = pybonita.tests.BonitaMockedServer
        super(TestWithMockedServer,self).__init__(methodName)

class BonitaMockedServer(BonitaServer):
    """ Mocked server for testing purpose

    """

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
            # First extract base path of called URL
            import urlparse
            parse = urlparse.urlparse(full_url).path
            if parse[0] == '/':
                parse = parse[1:]
            split_parse = parse.split('/')
            if len(split_parse) == 0:
                raise Exception('not supported url : %s'%(full_url))
            url_parse = split_parse[0]

            if not (url_parse,method) in self.responses:
                raise Exception('No already sets response for url %s and method %s' % (url_parse,method))

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
            cls.response_list_instance = URLRequest.ResponseList()

        return cls.response_list_instance

    @classmethod
    def set_response_list(cls,response_list):
        """ Set the response list for next requests.
        
        :param list: List of entries as detailled after
        :raise: ValueError if response_list is not a list and each entry does not belong to the correct schema
        
        An Entry is a list containing :
        :base_url: base URL the Request will be call (any further params will be ignored)
        :method: the HTTP method of the Request
        :status: the HTTP response status
        :type: the HTTP response mime type. None or empty string means response function tries to find it
        :message: the HTTP response body
        
        """
        if not isinstance(response_list,list):
            raise ValueError('response_list arg must be a list')
        
        # Run through the responses
        for response in response_list:
            if not isinstance(response,list):
                raise ValueError('response_list entry must be a list')
            if len(response) != 3:
                raise ValueError('response_list entry must have 3 fields')
            
            # Grab each fields
            url = response[0]
            method = 'POST'
            status = response[1]
            type = 'xml'
            message = response[2]
            
            response_list = cls.get_response_list()
            response_list.add_or_augment_response_list(url,method,status,type,message)

    @classmethod
    def extract_response(cls,url,method,extra_environ):
        """ Retrieve a response from already sets response list

        """
        if len(cls.get_response_list().get_responses()) == 0:
            # No already set response
            raise Exception('No prepared response list')
        else:
            # Already set responses : find the good one
            status,content_type,data = cls.get_response_list().search_and_consume_reponse(url,method)

        return status,content_type,data

    def sendRESTRequest(self, url, user=None, data=dict()):
        """ Do not call a BonitaServer, but rather access the reponses list given prior to this method call.
        
        """
        response = URLResponse()
        
        response.status,response.content_type,response.data = self__class__.extract_response(url,'POST')
        
        return response
