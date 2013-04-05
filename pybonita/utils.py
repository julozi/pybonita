# -*- coding: utf-8 -*-
from bs4.element import Tag
from xml.dom.minidom import Document

from lxml.etree import XMLSchemaParseError

__all__ = ['dictToMapString', 'set_if_available', 'xml_find', 'xml_find_all',
           'TrackableList', 'TrackableObject','TrackableDict']


def dictToMapString(data_dict):

    doc = Document()
    maps = doc.createElement("map")
    doc.appendChild(maps)

    for key, value in data_dict.items():
        entry = doc.createElement("entry")
        maps.appendChild(entry)
        key_tag = doc.createElement("string")
        entry.appendChild(key_tag)
        key_value = doc.createTextNode(key)
        key_tag.appendChild(key_value)
        value_tag = doc.createElement("string")
        entry.appendChild(value_tag)
        value_value = doc.createTextNode(value)
        value_tag.appendChild(value_value)

    return doc.toxml()


def set_if_available(bonita_object, soup, tags, raise_exception=False):
    """ Sets up properties of a BonitaObject from the given list of tags if available in soup.

    :param bonita_object: Object where to put the new properties
    :type bonita_object: BonitaObject, but all python object can be used
    :param soup: xml soup where to extract the tags
    :type soup: bs4.element.Tag instance
    :param tags: list of the tags to add if available
    :type tags: list[unicode or str]
    :param raise_exception: should we raise an exception if the tag is not found ?
    :type raise_exception: bool (default : False)
    :raise XMLSchemaParseError: if soup does not contain the tag with the given name and raise_exception is true

    """
    for tag in tags:
        try:
            attr = xml_find(soup, tag)
            setattr(bonita_object, tag, attr.string)
        except XMLSchemaParseError:
            if raise_exception:
                raise


def xml_find(soup, name, raise_exception=True):
    """ Extends the bs4.find method to look for name in soup in a first-letter case insensitive manner.
    Yes, Bonita has the great feature (!!) to return either upper or lower case tag (inside/ouside of XML-like contains)

    :param soup: the soup to look into
    :type soup: bs4.element.Tag
    :param name: tag name to look for
    :type name: str or unicode
    :param raise_exception: should we raise an exception if the tag is not found ?
    :type raise_exception: bool (default : True)
    :return: None or bs4.element.Tag
    :raise TypeError: if soup is not a bs4.element.Tag instance
    :raise XMLSchemaParseError: if soup does not contain the tag with the given name and raise_exception is true

    """
    if not isinstance(soup, Tag):
        raise TypeError('soup must be a bs4.element.Tag instance : %s' % (type(soup)))
    if not isinstance(name, (str, unicode)):
        raise TypeError('name muse be a string or unicode')

    base_name = name
    capitalize_name = base_name[0].upper() + base_name[1:]

    tag = soup.find({base_name: True, capitalize_name: True})

    if raise_exception and tag is None:
        raise XMLSchemaParseError('tag %s not found' % (name))

    return(tag)


def xml_find_all(soup, name):
    """ Extends the bs4.find_all method to look for name in soup in a first-letter case insensitive manner.
    Yes, Bonita has the great feature (!!) to return either upper or lower case tag (inside/ouside of XML-like contains)

    :param soup: the soup to look into
    :type soup: bs4.element.Tag
    :param name: tag name to look for
    :type name: str or unicode
    :return: list of bs4.element.Tag, possibly void list
    :raise TypeError: if soup is not a bs4.element.Tag instance

    """
    if not isinstance(soup, Tag):
        raise TypeError('soup must be a bs4.element.Tag instance : %s' % (type(soup)))
    if not isinstance(name, (str, unicode)):
        raise TypeError('name muse be a string or unicode')

    base_name = name
    capitalize_name = base_name[0].upper() + base_name[1:]

    tags = soup.find_all({base_name: True, capitalize_name: True})

    return(tags)


class TrackableMixin(object):
    """ A mixin to track modification of object.

    Derived class set the state with _set_modified, _set_unchanged and clear.
    Upper class only gets the state with is_modified or is_unchanged.

    """

    class Enum(set):
        def __getattr__(self, name):
            if name in self:
                return name
            raise AttributeError

    STATES = Enum(['UNCHANGED', 'MODIFIED'])

    def __init__(self, state=None):
        """ Set the object to the given state, default to unchanged """
        self._state = state if state is not None else self.STATES.UNCHANGED

    def clear_state(self):
        """ Clear object state """
        self._state = self.STATES.UNCHANGED

    def _get_is_modified(self):
        """ Get if object has been modified """
        return self._state == self.STATES.MODIFIED

    def _get_is_unchanged(self):
        """ Get if object is unchanged """
        return self._state == self.STATES.UNCHANGED

    def _set_modified(self):
        """ Set the object as modified """
        self._state = self.STATES.MODIFIED

    def _set_unchanged(self):
        """ Set the object is unchanged """
        self._state = self.STATES.UNCHANGED

    is_modified = property(_get_is_modified, None, None)
    is_unchanged = property(_get_is_unchanged, None, None)


class TrackableList(list, TrackableMixin):
    """ A List with tracked changes

    Example
.. code ::

    tl = TracklableList(['a','b']) # tl.is_modified == False
    tl.append('c') # tl.is_modified == True
    tl.clear_state() # tl.is_modified == False

    """

    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        TrackableMixin.__init__(self)

    def _wrap(method):
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self._set_modified()
            return result
        return wrapper

    append = _wrap(list.append)
    extend = _wrap(list.extend)
    insert = _wrap(list.insert)
    pop = _wrap(list.pop)
    remove = _wrap(list.remove)
    reverse = _wrap(list.reverse)
    sort = _wrap(list.sort)


class TrackableDict(dict, TrackableMixin):
    """ A Dictionnary with tracked changes

    Example
.. code ::

    td = TracklableDict({'a': 1, 'b': 2})  # td.is_modified == False
    td['a'] = 3  # td.is_modified == True
    td.clear_state() # td.is_modified == False

    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        TrackableMixin.__init__(self)

    def __setitem__(self, key, value):
        super(TrackableDict, self).__setitem__(key, value)

    def update(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("update expected at most 1 arguments, got %d" % len(args))

        other = dict(*args, **kwargs)
        for key in other:
            self[key] = other[key]

        self._set_modified()

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
            self._set_modified()

        return self[key]


class TrackableObject(TrackableMixin):
    """ A class that tracks attributes modification """

    def __init__(self, *args, **kwargs):
        TrackableMixin.__init__(self, *args)
        self.clear()

    def clear(self, attribute=None):
        """ Clear an attribute, if given, or all the dirty attributes.
        *If all attributes are cleared, object state is cleared also.*

        """
        if attribute is not None:
            if attribute in self._dirties:
                self._dirties.remove(attribute)
                if len(self._dirties) == 0:
                    self._state = self.STATES.UNCHANGED
        else:
            self._dirties = set()
            self._state = self.STATES.UNCHANGED

    def get_dirties(self):
        """ Return attributes marked as dirty """
        return list(self._dirties)

    def __setattr__(self, attribute, value):
        # Set the new value
        object.__setattr__(self, attribute, value)
        # And mark object as dirty except if changing _state attribute of course
        if attribute not in ['_state', '_dirties']:
            object.__setattr__(self, '_state', TrackableMixin.STATES.MODIFIED)
            # Track dirties attributes
            self._dirties.add(attribute)
