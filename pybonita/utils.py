# -*- coding: utf-8 -*-

from xml.dom.minidom import Document

__all__ = ['getMapString']

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
