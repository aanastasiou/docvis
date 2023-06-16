from .core import DataToRenderable, StringTemplate
#, VisElement, RenderToFileMixin, FileTemplateVisElement
import markdown


class MarkdownParagraph(StringTemplate):
    """
    Renders a Markdown specific template defined by a string
    """
    pass

class MarkdownList(DataToRenderable):
    def __init__(self, list_data):
        self._list_data = list_data

    def _after_render(self, before_render_result, main_render_result, indent_level):
        rendered_data = [u.render() if issubclass(type(u), DataToRenderable) else u for u in self._list_data[1:]]
        first_list_item = f"{' ' * (2*indent_level)}{'* ' if indent_level==0 else ''}{self._list_data[0]}"
        rest_list_items = [f"{' ' * (2*(indent_level))}* {u}" for u in rendered_data]
        return "\n".join([first_list_item]+rest_list_items)


        


# class LinkDocument(MarkdownVisElement):
#     """
#     Represents a structural link between two MarkDown documents.
# 
#     If the link leads back to a report document, that document is first rendered before it is linked.
#     Otherwise, if the link is just a string, this element simply inserts a link to it.
# 
#     In this way it is possible to define hierarchical documents that get rendered from the top document.
#     """
#     # TODO: HIGH, add a status variable to stop recursive rendering.
#     def __init__(self, link_label, document_to_link):
#         self._document_to_link = document_to_link
# 
#         if issubclass(type(document_to_link), RenderToFileMixin):
#             super().__init__("[{{link_label}}]({{document_to_link}})", link_label=link_label, document_to_link=document_to_link._rendertofilemixin_to_file)
#         elif type(document_to_link) is str:
#             super().__init__("[{{link_label}}]({{document_to_link}})", link_label=link_label, document_to_link=document_to_link)
#         #else:
#         #    raise exception.DataStructureError(f"Linkdocument expected renderable to file received {type(document_to_link)}")
# 
#     def _after_render(self, init_object, visual_reps):
#         if issubclass(type(self._document_to_link), RenderToFileMixin):
#             self._document_to_link.render()
#         return super()._after_render(init_object, visual_reps)
# 
# 
# 
