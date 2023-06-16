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

import jinja2
import os
import shutil
import json

# TODO: MED, Elements also need a way of determining any additional dependencies they might have
# e.g. Javascript scripts that much be included before the component can be used succesfully.

class DataToRenderable:
    def __init__(self): 
        """
        Initialises an element with all the information that is required to generate the final visualisation.
        """
        pass
    
    def _main_render(self, indent_level=0):
        """
        Process the data passed at __init__ and produces a VisElementRendered.
        """
        return before_render_result

    def _clear(self):
        pass

    def render(self, indent_level=0):
        """
        Kickstarts the whole rendering process and returns the string representation of the data
        """
        # Clear any temporary resources that may have been created
        self._clear()
        return self._main_render(indent_level)


class StringTemplate(DataToRenderable):
    """
    Render a Jinja2 Template defined by a string.
    """
    def __init__(self, template_string, **context_args):
        """
        Automates the rendering of a very simple Jinja2 Template.

        :param template_string: A Jinja2 template string
        :param context_args: Any variables that are used by the template
        """
        super().__init__()
        self._context_args = context_args
        self._template_string = template_string

    def render(self, indent_level=0, **updated_context):
        self._context_args|=updated_context
        return super().render(indent_level)

    def _main_render(self, indent_level=0):
        """
        Finalises the rendering of this element down to its final form.
        """
        # Update the context before rendering
        rendered_context = {}
        # Update the context and then render
        for key, value in self._context_args.items():
            if issubclass(type(value), DataToRenderable):
                value = value.render(indent_level+1)
            rendered_context[key] = value
        return jinja2.Template(self._template_string).render(**rendered_context)


class FileTemplate(StringTemplate):
    """
    Renders a Jinja2 Template defined by a file.
    """
    def __init__(self, template_file, **context_args):
        with open(template_file, "rt", encoding = "utf-8") as fd:
            super().__init__(fd.read(), **context_args)


class HTMLPage(StringTemplate):
    def __init__(self, title, external_resources, body):
        super().__init__("<!DOCTYPE html>\n"
                         "<html>\n"
                         "    <head>\n"
                         "        <meta charset=\"utf-8\" />\n"
                         "{% for res, ext in page_externals %}"
                         "{% if ext == '.css' %}"
                         "        <link rel=\"stylesheet\" href=\"{{res}}\">\n"
                         "{% endif %}"
                         "{% if ext == '.js' %}"
                         "        <script type=\"application/javascript\" src=\"{{res}}\" defer/>\n"
                         "{% endif %}"
                         "{% endfor %}"
                         "        <title>{{page_title}}</title>\n"
                         "    </head>\n"
                         "    <body>\n"
                         "    {{page_body}}\n"
                         "    </body>\n"
                         "</html>\n",
                         page_title=title, 
                         page_body=body,
                         page_externals = [(a_res, os.path.splitext(a_res)[-1].lower()) for a_res in external_resources])


class HTMLTag(StringTemplate):
    def __init__(self, tag, content, external_resources):
        super().__init__("<{{element_tag}}>\n"
                         "{{element_content}}\n"
                         "</{{element_tag}}>",
                         element_tag=tag,
                         element_content=content)
        self._external_resources = external_resources


class HTMLDiv(HTMLTag):
    def __init__(self, content, external_resources):
        super().__init__("div", content, external_resources)


class HTMLBody(HTMLTag):
    def __init__(self, content, external_resources):
        super().__init__("body", content, external_resources)



# class VisElementStyle(dict):
#     """
#     Determines common styles across different visual components.
# 
#     A component that is used to structure a report might make use of different technologies and toolkits. These
#     components, although they might have similar capabilities, do not necessarily use the same colours, fonts,
#     line thicknesses, text alignments and so on.
# 
#     A VisElementStyle's purpose is similar to a CSS class. It captures a set of properties that can be used to
#     enforce a consistent style across document components.
# 
#     A VisElementStyle is basically a python dictionary with additional functionality to save and load that dictionary
#     in the form of a JSON object.
#     """
#     def save(self, filename):
#         with open(filename, "wt", encoding = "utf-8") as fd:
#             json.dump(self, fd)
# 
#     def load(self, filename):
#         self.clear()
#         with open(filename, "rt", encoding = "utf-8") as fd:
#             self.update(json.load(fd))
# 
#     def get_style_attributes(self, style_attributes):
#         """
#         Returns a subset of style attributes as a dictionary.
# 
#         :param style_attributes: A list of attribute names to extract from the VisElementStyle
#         :return: dict
#         """
#         style_subset = dict.fromkeys(style_attributes)
#         for an_attribute in style_attributes:
#             if an_attribute in self:
#                 style_subset[an_attribute] = self[an_attribute]
#             else:
#                 del style_subset[an_attribute]
#         #style_subset = dict(zip(style_attributes, map(lambda x: self[x] if x in self else None, style_attributes)))
#         return style_subset
# 
# 
# class StyledVisElement(VisElement):
#     """
#     A VisElement with common style parameters.
#     """
#     def __init__(self, style=None, **context_args):
#         super().__init__(**context_args)
#         if style is not None:
#             self._style = style
#         else:
#             self._style = VisElementStyle()
# 
# # TODO: LOW, Now something can derive from this and represent one report with all of its data
# class HTMLTemplatedDocument(RenderToFileMixin, FileTemplateVisElement):
#     """
#     Represents a templated HTML document.
# 
#     The thinking behind this was to have an HTML template that includes the preamble and the closing of the document
#     with a small number of context variables controlling the rendering of the content to the HTML document.
#     """
#     def __init__(self, body_variable, body_element, html_template_file, output_file, additional_files=None, **context_args):
#         # Initialise the RenderToFile mixin
#         RenderToFileMixin.__init__(self, output_file, additional_files)
#         # Initialise the templated vis element
#         FileTemplateVisElement.__init__(self, html_template_file, **context_args)
#         # Inject the body variable explicitly to ensure that it will be there during rendering
#         self.context[body_variable] = body_element
# 
# 
# class SimpleAssociativeMappingDisplay(StringTemplateVisElement):
#     """
#     Renders a key-value type of associative mapping. It requires certain styles (mappingvis,keyvalue,key,value,mappingvistitle) to already have been defined.
#     """
#     def __init__(self, a_dict, a_title=""):
#         super().__init__("<div class=""mappingvis"">\n\t<div class=""mappingvistitle"">\n\t\t{{a_title}}\n\t</div>\n\t{% for item in items.items() %}\n\t<div class=""keyvalue"">\n\t\t<div class=""key"">{{item[0]}}</div>\n\t\t<div class=""value"">{{item[1]}}</div>\n\t</div>{% endfor %}\n</div>", items=a_dict, a_title=a_title)
# 

