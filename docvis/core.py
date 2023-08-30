"""
Core
====

Docvis' core elements are used to "build" dynamic HTML documents.

The input to these elements are common Python objects describing various user-data
and the output is a well-formed HTML document.

Design
------

* The key entity here is ``HTMLTag``. 
* Every ``HTMLTag`` bears its "name", content, attributes and external resources.
* External resources are any additional elements that must be present in a documents ``<head>`` 
  section, so that it renders properly within the page.

* Here is a simple example based on the ``<meta>`` tag:

  This...

  ::

    meta_data = HTMLTag("meta", "", {"charset":"utf-8"}, is_empty=True)

  
  ... would render as:
  ::

    <meta charset="utf-8" />

  This of course is already available as ``docvis.HTMLMeta``.

* And here is a simple example based on the ``<div>`` tag:

  This...
  ::

    some_script = HTMLTag("div",
                          "<p>Hello World</p>", 
                          ["base_script.js"],
                          {"class":"thediv"})

  ...would render as

  ::

    <div class="thediv">
       <p>Hello World</p>
    </div>

  This is self-explanatory, **but most importantly**, this ``<div>`` has external dependencies (``base_script.js``),
  which will be propagated up to the HTML page's ``head`` element by Docvis.

  This is **not** the way ``div`` is instantiated and used in Docvis, for that, see ``docvis.HTMLDiv``.

* All HTML elements produce an ``HTMLRenderedElement`` data structure that contains two attributes:
  ``extra_resources``, ``code``. 
  ``extra_resources`` are made available to elements that need it to properly represent a given element and 
  ``code`` is the actual HTML code that makes it into the document.

* This design was inspired by Bokeh, but it makes sense in transforming any kind of data to an HTML representation
  without worrying too much about the rest of the elements in a given document. In this way, Bokeh can co-exist with 
  matplotlib and other elements.

* The absolute top-level "object" here is ``HTMLPage``. This element is responsible for rendering a whole HTML page, 
  complete with its dependencies, to a portable standalone document.


:author: Athanasios Anastasiou
:date: Mar 2023
"""

import os
import collections
import functools
import re


HTMLRenderedElement = collections.namedtuple("HTMLRenderedElement", ["extra_resources", "code"])

class RenderableElement:
    """
    Base class for all *elements* that return code or fragments of code
    """
    def render(self):
        raise NotImplementedError(f"type(self) not expected to be instantiated directly")


class HTMLTag(RenderableElement):
    """
    Represents a generic HTML tag

    :param tag: The tag name WITHOUT the brackets
    :type tag: str
    :param content: The content of the tag
    :type content: str
    :param external_resources: Any external resources required for this element to render properly (e.g.
                               script files, css, etc). List of string, one resource per line.
    :type external_resources: list[str]
    :param attributes: Extra attributes for the tag, as a dictionary of attr->attr_value
    :type attributes: dict
    :param is_empty: Whether this tag should be rendered as an empty (i.e. self-closing)
    :type is_empty: bool
    """
    def __init__(self, tag, content, external_resources=[], attributes={}, is_empty=False):
        self._tag = tag
        self._content = content
        self._external_resources = external_resources
        self._attributes = attributes
        self._is_empty = is_empty

    def render(self):
        """
        Transform the element's data into HTML.
        """
        attrs = (" " + " ".join([f"{u}=\"{v}\"" 
                                 if len(v) > 0 else f"{u}"
                                 for u,v in self._attributes.items()])) if len(self._attributes) > 0 else ""
        if len(self._tag) > 0:
            if self._is_empty:
                rendered_content = f"<{self._tag}{attrs}/>"
                start_tag = f"<{self._tag}{attrs}/>"
                end_tag = ""
            else:
                start_tag = f"<{self._tag}{attrs}>"
                end_tag = f"</{self._tag}>"
        else:
            start_tag = end_tag = ""

        if len(self._content) > 0:
            rendered_content = f"{start_tag}{self._content}{end_tag}"
        else:
            rendered_content = f"{start_tag}{end_tag}"


        return HTMLRenderedElement(extra_resources=self._external_resources, 
                                   code=rendered_content)


class HTMLNestedTag(HTMLTag):
    """
    A nested tag only encloses a set of nested elements
    """
    def __init__(self, tag, children, external_resources=[], attributes={}):
        super().__init__(tag, "", external_resources, attributes=attributes)
        self._children = children

    def render(self):
        rendered_content =  [u.render() for u in self._children]
        self._content = "".join([u.code for u in rendered_content])
        deeper_resources = list(functools.reduce(lambda x,y:x+y, [u.extra_resources for u in rendered_content], [])) + self._external_resources
        return HTMLRenderedElement(extra_resources=deeper_resources, 
                                   code = super().render().code)


class HTMLHead(HTMLNestedTag):
    """
    The document header element.

    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/head
    """
    def __init__(self, children, external_resources=[], attributes={}):
        super().__init__("head", children, external_resources, attributes)


class HTMLMeta(HTMLTag):
    """
    The _meta_data element.

    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta
    """
    def __init__(self, attributes):
        super().__init__("meta","", [], attributes, is_empty=True)


class HTMLStylesheet(HTMLTag):
    """
    A link element specifically configured to point to a stylesheet.

    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link
    """
    def __init__(self, content, external_resources=[], attributes={}):
        super().__init__("link", "", external_resources, attributes|{"rel":"stylesheet", "href":content}, is_empty=True)


class HTMLScript(HTMLTag):
    """
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script
    """
    def __init__(self, content, external_resources=[], attributes={}):
        super().__init__("script", "", external_resources, attributes|{"src":content, "defer":""})


class HTMLTitle(HTMLTag):
    """
    Document title element

    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/title
    """
    def __init__(self, content):
        super().__init__("title", content)


class HTMLBody(HTMLNestedTag):
    """
    HTML Body element

    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body
    """
    def __init__(self, children, external_resources=[], attributes={}):
        super().__init__("body", children, external_resources, attributes)


class HTMLDiv(HTMLNestedTag):
    """
    Content division element

    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/div
    """
    def __init__(self, children, external_resources=[], attributes={}):
        super().__init__("div", children, external_resources, attributes)


class HTMLParagraph(HTMLTag):
    """
    A paragraph element

    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/p
    """
    def __init__(self, content, external_resources=[], attributes={}):
        super().__init__("p", content, external_resources, attributes)


class HTMLPassthrough(HTMLTag):
    """
    An element for content that is already formatted as HTML.

    The content of the element is passed verbatim to its output, along with any additional dependencies.
    """
    def __init__(self, content, external_resources=[]):
        super().__init__("", content, external_resources, attributes={})


class HTMLPage(RenderableElement):
    """
    The top level HTML page.
    """
    def __init__(self, html_body, html_head):
        self._html_body = html_body
        # If an HTMLHead was not specified, add an empty one
        self._html_head = html_head if html_head is not None else HTMLHead([])

    def render(self,):
        # First of all, render the body
        rendered_body = self._html_body.render()

        # Now collect the required resources from BOTH the supplied head and body
        resources = list(set(rendered_body.extra_resources))
        # Sort resources so that any file type scripts or stylesheets come first
        resources = sorted(resources, key = lambda x:0 if '.js' in x or '.css' in x else 1)
        head_content = []
        # Scan the resources and dynamically create the head
        for a_resource in resources:
            ext = os.path.splitext(a_resource)[-1]
            element_to_add = None
            if ext == '.css':
                element_to_add = HTMLStylesheet(a_resource)
            elif ext == ".js":
                element_to_add = HTMLScript(a_resource)
            else:
                element_to_add = HTMLPassthrough(a_resource)

            head_content.append(element_to_add)

        # Add the user supplied HTMLHead children
        rendered_head = HTMLHead(list(set(head_content + self._html_head._children))).render().code
        
        return re.sub(r" +", " ",f"<!DOCTYPE html><html>{rendered_head}{rendered_body.code}</html>")

