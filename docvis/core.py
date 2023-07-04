"""
RepVis

Elements that produce an intermediate format (i.e. Markdown), of complex
visualisation elements which are then all brought together in one top level 
element and can also be saved to disk as standalone documents.

Since markdown will not be rendered if inside block level HTML, the elements 
that produce markdown should be nested within the elements that produce HTML (If any)

:author: Athanasios Anastasiou
:date: Mar 2023
"""

import os
import collections
import functools


HTMLRenderedElement = collections.namedtuple("HTMLRenderedElement", ["extra_resources", "code"])

class HTMLTag:
    """
    Represents a given HTML tag

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
            rendered_content = f"{start_tag}\n{self._content}\n{end_tag}\n"
        else:
            rendered_content = f"{start_tag}{end_tag}\n"


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
        # TODO: HIGH, optimise the following
        self._content = "".join([u.code for u in rendered_content])
        if len(self._children)>0:
            self._content = "\n".join(map(lambda x:f"    {x}",self._content.split("\n")))
        deeper_resources = list(functools.reduce(lambda x,y:x+y, [u.extra_resources for u in rendered_content], [])) + self._external_resources
        return HTMLRenderedElement(extra_resources=deeper_resources, 
                                   code = super().render().code)


class HTMLHead(HTMLNestedTag):
    def __init__(self, children, external_resources=[], attributes={}):
        super().__init__("head", children, external_resources, attributes)


class HTMLMeta(HTMLTag):
    def __init__(self, attributes):
        super().__init__("meta","", [], attributes, is_empty=True)


class HTMLStylesheet(HTMLTag):
    def __init__(self, content, external_resources=[], attributes={}):
        super().__init__("link", "", external_resources, attributes|{"rel":"stylesheet", "href":content}, is_empty=True)


class HTMLPassthrough(HTMLTag):
    def __init__(self, content, external_resources=[]):
        super().__init__("", content, external_resources, attributes={})


class HTMLScript(HTMLTag):
    def __init__(self, content, external_resources=[], attributes={}):
        super().__init__("script", "", external_resources, attributes|{"src":content, "defer":""})


class HTMLTitle(HTMLTag):
    def __init__(self, content):
        super().__init__("title", content)


class HTMLBody(HTMLNestedTag):
    def __init__(self, children, external_resources=[], attributes={}):
        super().__init__("body", children, external_resources, attributes)


class HTMLDiv(HTMLNestedTag):
    def __init__(self, children, external_resources=[], attributes={}):
        super().__init__("div", children, external_resources, attributes)


class HTMLParagraph(HTMLTag):
    def __init__(self, content, external_resources=[], attributes={}):
        super().__init__("p", content, external_resources, attributes)


class HTMLPage:
    def __init__(self, html_body, extra_head_components=[]):
        self._extra_head_components = extra_head_components
        self._html_body = html_body

    def render(self,):
        # First of all, render the body
        rendered_body = self._html_body.render()
        # Now collect the required resources
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

        # Add the external head components
        head_content = self._extra_head_components + head_content
        rendered_head = HTMLHead(head_content).render().code
        
        return f"<!DOCTYPE html>\n{rendered_head}\n{rendered_body.code}"





# class DataToRenderable:
#     def __init__(self): 
#         """
#         Initialises an element with all the information that is required to generate the final visualisation.
#         """
#         pass
#     
#     def _main_render(self, indent_level=0):
#         """
#         Process the data passed at __init__ and produces a VisElementRendered.
#         """
#         return ""
# 
#     def _clear(self):
#         pass
# 
#     def render(self, indent_level=0):
#         """
#         Kickstarts the whole rendering process and returns the string representation of the data
#         """
#         # Clear any temporary resources that may have been created
#         self._clear()
#         return self._main_render(indent_level)
# 
# 
# class StringTemplate(DataToRenderable):
#     """
#     Render a Jinja2 Template defined by a string.
#     """
#     def __init__(self, template_string, **context_args):
#         """
#         Automates the rendering of a very simple Jinja2 Template.
# 
#         :param template_string: A Jinja2 template string
#         :param context_args: Any variables that are used by the template
#         """
#         super().__init__()
#         self._context_args = context_args
#         self._template_string = template_string
# 
#     def render(self, indent_level=0, **updated_context):
#         self._context_args|=updated_context
#         return super().render(indent_level)
# 
#     def _main_render(self, indent_level=0):
#         """
#         Finalises the rendering of this element down to its final form.
#         """
#         return jinja2.Template(self._template_string).render(self._context_args)
# 
# 
# class FileTemplate(StringTemplate):
#     """
#     Renders a Jinja2 Template defined by a file.
#     """
#     def __init__(self, template_file, **context_args):
#         with open(template_file, "rt", encoding = "utf-8") as fd:
#             super().__init__(fd.read(), **context_args)
# 
# 
# class HTMLTag(StringTemplate):
#     def __init__(self, tag, content, external_resources=[], **attributes):
#         super().__init__("<{{element_tag}}{{element_attributes}}>\n\t"
#                          "{{element_content}}\n"
#                          "</{{element_tag}}>\n",
#                          element_tag=tag,
#                          element_content=content,
#                          element_attributes=(" " + " ".join([f"{u}={v}" for u,v in self._attributes.items()])) if len(attributes) > 0 else "")
#         self._tag = tag
#         self._attributes = attributes
#         self._external_resources = external_resources
# 
#     def _main_render(self, indent_level=0):
#         return HTMLRenderedElement(extra_resources=self._external_resources, 
#                                    code=super()._main_render(indent_level))
# 
# 
# class HTMLNestedTag(HTMLTag):
#     def __init__(self, tag, children=[], external_resources=[], **attributes):
#         super().__init__(tag, "", external_resources, **attributes)
#         self._children = children
# 
#     def _main_render(self, indent_level=0):
#         rendered_content = []
#         for a_child in self._children:
#             rendered_content.append(a_child.render(indent_level+1))
#         cnt = "".join([f"{u.code}" for u in rendered_content])
#         res = self._external_resources + [u.extra_resources for u in rendered_content]
#         attrs = " ".join([f"{u}={v}" for u,v in self._attributes.items()])
#         attrs = f" {attrs}"
#         self._context_args|={"element_tag":self._tag,
#                              "element_attributes":attrs,
#                              "element_content":cnt}
#         return HTMLRenderedElement(extra_resources=res, 
#                                    code=super()._main_render(indent_level))
# 
#     
# class HTMLPage(HTMLNestedTag):
#     def __init__(self, title, body, external_resources=[]):
#         super().__init__("", body, external_resources)
#         self._template_string = "<!DOCTYPE html>\n"
#         "<html>\n"
#         "    <head>\n"
#         "        <meta charset=\"utf-8\" />\n"
#         "{% for res, ext in page_externals %}"
#         "{% if ext == '.css' %}"
#         "        <link rel=\"stylesheet\" href=\"{{res}}\">\n"
#         "{% endif %}"
#         "{% if ext == '.js' %}"
#         "        <script type=\"application/javascript\" src=\"{{res}}\" defer/>\n"
#         "{% endif %}"
#         "{% endfor %}"
#         "        <title>{{page_title}}</title>\n"
#         "    </head>\n"
#         "    <body>\n"
#         "    {{page_body}}\n"
#         "    </body>\n"
#         "</html>\n"
#         self._context_args = {"page_title":"", 
#                               "page_body":"",
#                               "page_externals":""}
#         self._body = body
#         self._title = title
# 
#     def render(self, indent_level=0,):
#         rendered_body = self._body.render(indent_level+1)
#         self._context_args |= {"page_title":self._title,
#                                "page_body":rendered_body.code,
#                                "page_externals":self._external_resources + rendered_body.extra_resources}
#         return super().render(indent_level)
# 
#         
# class HTMLDiv(HTMLNestedTag):
#     def __init__(self, children, external_resources=[]):
#         super().__init__("div", children, external_resources)
# 
# class HTMLParagraph(HTMLTag):
#     def __init__(self, content, external_resources=[]):
#         super().__init__("p", content, external_resources)
# 
# 
# class HTMLBody(HTMLNestedTag):
#     def __init__(self, children, external_resources=[]):
#         super().__init__("body", children, external_resources)
# 
# 
# 
# # class VisElementStyle(dict):
# #     """
# #     Determines common styles across different visual components.
# # 
# #     A component that is used to structure a report might make use of different technologies and toolkits. These
# #     components, although they might have similar capabilities, do not necessarily use the same colours, fonts,
# #     line thicknesses, text alignments and so on.
# # 
# #     A VisElementStyle's purpose is similar to a CSS class. It captures a set of properties that can be used to
# #     enforce a consistent style across document components.
# # 
# #     A VisElementStyle is basically a python dictionary with additional functionality to save and load that dictionary
# #     in the form of a JSON object.
# #     """
# #     def save(self, filename):
# #         with open(filename, "wt", encoding = "utf-8") as fd:
# #             json.dump(self, fd)
# # 
# #     def load(self, filename):
# #         self.clear()
# #         with open(filename, "rt", encoding = "utf-8") as fd:
# #             self.update(json.load(fd))
# # 
# #     def get_style_attributes(self, style_attributes):
# #         """
# #         Returns a subset of style attributes as a dictionary.
# # 
# #         :param style_attributes: A list of attribute names to extract from the VisElementStyle
# #         :return: dict
# #         """
# #         style_subset = dict.fromkeys(style_attributes)
# #         for an_attribute in style_attributes:
# #             if an_attribute in self:
# #                 style_subset[an_attribute] = self[an_attribute]
# #             else:
# #                 del style_subset[an_attribute]
# #         #style_subset = dict(zip(style_attributes, map(lambda x: self[x] if x in self else None, style_attributes)))
# #         return style_subset
# # 
# # 
# # class StyledVisElement(VisElement):
# #     """
# #     A VisElement with common style parameters.
# #     """
# #     def __init__(self, style=None, **context_args):
# #         super().__init__(**context_args)
# #         if style is not None:
# #             self._style = style
# #         else:
# #             self._style = VisElementStyle()
# # 
# # # TODO: LOW, Now something can derive from this and represent one report with all of its data
# # class HTMLTemplatedDocument(RenderToFileMixin, FileTemplateVisElement):
# #     """
# #     Represents a templated HTML document.
# # 
# #     The thinking behind this was to have an HTML template that includes the preamble and the closing of the document
# #     with a small number of context variables controlling the rendering of the content to the HTML document.
# #     """
# #     def __init__(self, body_variable, body_element, html_template_file, output_file, additional_files=None, **context_args):
# #         # Initialise the RenderToFile mixin
# #         RenderToFileMixin.__init__(self, output_file, additional_files)
# #         # Initialise the templated vis element
# #         FileTemplateVisElement.__init__(self, html_template_file, **context_args)
# #         # Inject the body variable explicitly to ensure that it will be there during rendering
# #         self.context[body_variable] = body_element
# # 
# # 
# # class SimpleAssociativeMappingDisplay(StringTemplateVisElement):
# #     """
# #     Renders a key-value type of associative mapping. It requires certain styles (mappingvis,keyvalue,key,value,mappingvistitle) to already have been defined.
# #     """
# #     def __init__(self, a_dict, a_title=""):
# #         super().__init__("<div class=""mappingvis"">\n\t<div class=""mappingvistitle"">\n\t\t{{a_title}}\n\t</div>\n\t{% for item in items.items() %}\n\t<div class=""keyvalue"">\n\t\t<div class=""key"">{{item[0]}}</div>\n\t\t<div class=""value"">{{item[1]}}</div>\n\t</div>{% endfor %}\n</div>", items=a_dict, a_title=a_title)
# # 
# 
