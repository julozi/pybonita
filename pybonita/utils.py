# -*- coding: utf-8 -*-
from bs4.element import Tag
from xml.dom.minidom import Document

from lxml.etree import XMLSchemaParseError

__all__ = ['dictToMapString','set_if_available','xml_find']

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
            attr = xml_find(soup,tag)
            setattr(bonita_object,tag,attr.string)
        except XMLSchemaParseError as exc:
            if raise_exception:
                raise

def xml_find(soup,name,raise_exception=True):
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
    if not isinstance(soup,Tag):
        raise TypeError('soup must be a bs4.element.Tag instance : %s' % (type(soup)))
    if not isinstance(name,(str,unicode)):
        raise TypeError('name muse be a string or unicode')

    base_name = name
    capitalize_name = base_name.capitalize()

    tag = soup.find({base_name:True, capitalize_name:True})

    if raise_exception and tag is None:
        raise XMLSchemaParseError('tag %s not found' % (name))

    return(tag)
