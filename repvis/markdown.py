from .core import StringTemplateVisElement, VisElement, RenderToFileMixin, FileTemplateVisElement
import markdown


class MarkdownVisElement(StringTemplateVisElement):
    """
    Renders a Markdown specific template defined by a string
    """
    def _after_render(self, init_object, visual_reps):
        # return markdown.markdown(self._template_string.format(**visual_reps))
        return markdown.markdown(super()._after_render(init_object, visual_reps))


class LinkDocument(MarkdownVisElement):
    """
    Represents a structural link between two MarkDown documents.

    If the link leads back to a report document, that document is first rendered before it is linked.
    Otherwise, if the link is just a string, this element simply inserts a link to it.

    In this way it is possible to define hierarchical documents that get rendered from the top document.
    """
    # TODO: HIGH, add a status variable to stop recursive rendering.
    def __init__(self, link_label, document_to_link):
        self._document_to_link = document_to_link

        if issubclass(type(document_to_link), RenderToFileMixin):
            super().__init__("[{{link_label}}]({{document_to_link}})", link_label=link_label, document_to_link=document_to_link._rendertofilemixin_to_file)
        elif type(document_to_link) is str:
            super().__init__("[{{link_label}}]({{document_to_link}})", link_label=link_label, document_to_link=document_to_link)
        #else:
        #    raise exception.DataStructureError(f"Linkdocument expected renderable to file received {type(document_to_link)}")

    def _after_render(self, init_object, visual_reps):
        if issubclass(type(self._document_to_link), RenderToFileMixin):
            self._document_to_link.render()
        return super()._after_render(init_object, visual_reps)



