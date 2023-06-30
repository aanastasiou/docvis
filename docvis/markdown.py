import jinja2
from .core import HTMLTag, HTMLRenderedElement
import markdown

class HTMLMarkdownDiv(HTMLTag):
    def __init__(self, markdown_template, context, external_resources=[], attributes={}):
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
    Preprocesses the template and substitutes specific commands with "plots" over a context
    """
    def __init__(self, markdown_template, context, external_resources=[], attributes={}):
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


