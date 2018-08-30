# Copyright: 2008 MoinMoin:BastianBlank
# License: GNU GPL v2 (or any later version), see LICENSE.txt for details.

"""
MoinMoin - Text highlighting converter
"""


from __future__ import absolute_import, division

import re

from flask import request

from MoinMoin.util.tree import html, moin_page


class Converter(object):
    @classmethod
    def _factory(cls, input, output, highlight='', regex='', **kw):
        if highlight == 'highlight':
            regex = request.args['regex']
            return cls(regex)

    def recurse(self, elem):
        new_childs = []

        for child in elem:
            if isinstance(child, (unicode, str)):
                pos = 0

                # Restrict it to our own namespace for now
                if elem.tag.uri == moin_page.namespace:
                    for match in re.finditer(self.pattern, child):
                        text = child[pos:match.start()]
                        new_childs.append(text)

                        text = child[match.start():match.end()]
                        attrib = {html.class_: 'moin-highlight'}
                        e = moin_page.strong(attrib=attrib, children=[text])
                        new_childs.append(e)

                        pos = match.end()

                new_childs.append(child[pos:])
            else:
                self.recurse(child)
                new_childs.append(child)

        # Use inline replacement to avoid a complete tree copy
        if len(new_childs) > len(elem):
            elem[:] = new_childs

    def __init__(self, regex):
        self.pattern = re.compile(regex)

    def __call__(self, tree):
        self.recurse(tree)
        return tree


from . import default_registry
from MoinMoin.util.mime import Type, type_moin_document
default_registry.register(Converter._factory, type_moin_document, type_moin_document)
