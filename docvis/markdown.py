"""
Markdown rendering represents an additional layer *on top* of HTML.

There are two key entities in this sub module, ``HTMLMarkdownDiv`` and 
``HTMLPreProcMarkdownDiv``.

``HTMLMarkdownDiv``
-------------------

The first one is self-explanatory: It takes a markdown template, renders it to 
HTML and embeds that HTML into a ``div`` element. This can then be rendered 
within a document. The Markdown in that element can have dynamic components which 
will be rendered along. For example:

This...

::
  
  the_markdown = HTMLMarkdownDiv("# Heading\\nHello {{name}}", 
                                 {"name":"Flipper"})

...would render as:

::

    <div>
      <h1>Heading</h1>
      <p>Hello Flipper</p>
    </div>


``HTMLPreProcMarkdownDiv``
--------------------------

This element is similar to ``HTMLMarkdownDiv`` but it inserts another layer of
interpretation of a small DSL that can be used to parametrise an element from 
within the script in a safe way.

The DSL (fun-dsl) *captures* Python-like function calls with named keywords **only**.
So, something like ``myfunction(p1=value1, p2=value2)`` and so on.

The purpose of fun-dsl is to provide an easy way to parametrise a given element, especially
in the case that these elements do not have a string return value.


This was necessary because the undelying template engine 
(`jinja <https://jinja.palletsprojects.com/en/3.1.x/>`_), works under the assumption
that a given variable or function call will result into a string. In addition, it is 
difficult to "trap" the interpretation of a given tag in combination with a design 
that returns two results that serve different purposes.


Both elements operate with the ``extra`` and ``toc`` markdown extensions from the 
`Python markdown package <https://python-markdown.github.io/>`_.


:author: Athanasios Anastasiou
:date: Jun 2023
"""
import jinja2
from .core import HTMLTag, HTMLRenderedElement
import markdown
from .preprocessor import TemplatePreprocessor
from .exceptions import TemplatePreprocError

class HTMLMarkdownDiv(HTMLTag):
    """
    An HTML element that renders as a DIV and contains interpreted Markdown.

    :param markdown_template: Markdown interdispersed with variables and Jinja2 style tags that render variables from the context
    :type markdown_template: str
    :param context: A mapping of variable names to values
    :type context: dict
    :param external_resources: Any external resources required to render the content of this element.
    :type external_resources: list
    :param attributes: A mapping of attribute names to their values
    :type attributes: dict
    """
    def __init__(self, markdown_template, context={}, external_resources=[], attributes={}):
        super().__init__("div", "", external_resources, attributes)
        self._markdown_template = markdown_template
        self._context = context

    def render(self):
        # Go through the context and render anything that is a renderable
        html_context = {}
        ext_resources = []
        rendered_context = {}
        for u, v in self._context.items():
            if issubclass(type(v), HTMLTag):
                rendered_element = v.render()
                ext_resources += rendered_element.extra_resources
                v = rendered_element.code
            rendered_context[u] = v

        self._content = jinja2.Template(markdown.markdown(self._markdown_template, extensions=["extra", "toc"])).render(rendered_context)
        return HTMLRenderedElement(extra_resources=ext_resources+self._external_resources, 
                                   code=super().render().code)

class HTMLPreProcMarkdownDiv(HTMLTag):
    """
    Preprocesses the template and substitutes specific commands with their result over a context.

    :param markdown_template: A markdown template string interdispersed with other tags
    :type markdown_template: str
    :param function_table: A mapping from the name of a function call appearing in the
                           document and the computable name of the function. This ma,es
    :type function_table: dict
    :param context: A mapping from variable names to values. This is passed verbatim to jinja's render
    :type context: dict
    :param external_resources: A list of external resources required for this element (e.g. stylesheets, scripts)
    :type external_resources: list
    :param attributes: Attributes for the top level div element. Boolean attributes are rendered without a value.
    :type attributes: dict

    """
    def __init__(self, markdown_template, function_table, mark_start, mark_end, context, external_resources=[], attributes={}):
        super().__init__("div", "", external_resources, attributes)
        self._markdown_template = markdown_template
        self._context = context
        self._function_table = function_table
        self._template_preprocessor = TemplatePreprocessor(function_table, context, mark_start, mark_end)

    def render(self):
        # First pre-process the template to recover all function calls and render their
        # content
        pre_proc_string, pre_processed_elements, errors = self._template_preprocessor(self._markdown_template)
        
        if len(errors) > 0:
            # Otherwise raise an error exception
            raise TemplatePreprocError(errors)
                
        html_context = {}
        ext_resources = []
        rendered_context = {}

        for element in pre_processed_elements:
            ext_resources += element.result.extra_resources
            rendered_context[element.substituted_string] = element.result.code

        self._content = jinja2.Template(markdown.markdown(pre_proc_string, extensions=["extra", "toc"])).render(rendered_context|self._context)
        return HTMLRenderedElement(extra_resources=ext_resources+self._external_resources, 
                                   code=super().render().code)

