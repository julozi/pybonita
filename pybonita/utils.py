# -*- coding: utf-8 -*-

from xml.dom.minidom import Document

__all__ = ['getMapString','set_if_available']

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

def set_if_available(bonita_object, soup, tags):
    """ Sets up properties of a BonitaObject from the given list of tags if available in soup.

    :param bonita_object: Object where to put the new properties
    :type bonita_object: BonitaObject, but all python object can be used
    :param soup: xml soup where to extract the tags
    :type soup: BeautifulSoup instance
    :param tags: list of the tags to add if available
    :type tags: list[unicode or str]

    """
    for tag in tags:
        attr = getattr(soup,tag)
        if attr != None and 'string' in dir(attr):
            setattr(bonita_object,tag,attr.string)
