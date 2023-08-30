"""
==================
Complete Documents
==================

Docvis' document infrastructure is used to render complete documents simply by passing 
template and data information.

In the following overview, captialised names represent entities.

Specifically:

1.  A document:

    * Has a name

      * Its name resolves to a directory in the file system

    * Has an index Page
    * Has content Pages

    * Has a `render()` that renders all of its content and index pages within 
      a specific directory

2. A Page:

   * Has a name

     * Its name resolves to an HTML file in the file system

   * A string template that defines its content
   * Additional resources (such as scripts and CSS files)
   * DATA (from local variables)
"""

from .core import RenderableElement, HTMLPage, HTMLBody, HTMLTitle, HTMLStylesheet, HTMLMeta, HTMLHead
from .utils import DefaultDocVisMarkdownDiv
import pathlib
import os
import copy

class RenderableDocElement(RenderableElement):
    """
    Base class for all objects that can produce *hard-copies*.
    """
    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent


class Document(RenderableDocElement):
    """
    :param doc_name: A logical name for the document
    :type doc_name: str
    :param content_elements: A list of docvis.docs.Page that represent each content page in the document
    :type content_elements: List[docvis.docs.Page]
    :param dir_name: The directory name if it has to be set explicitly.
    :type dir_name: str
    """
    def __init__(self, doc_name, index_page, content_elements, dir_name = None):
        super().__init__(doc_name)
        # Add the index page
        index_page._name = "index"
        self._content_elements = {}
        self._content_elements |= {"index":index_page}
        self._content_elements |= dict([(c_key, c_el) for c_key, c_el in map(lambda x:(x.name, x), content_elements)])

        # All elements are parented to the current element
        # This works because all elements are copies of the originals and can have 
        # different parents
        for an_element in self._content_elements.values():
            an_element._parent = self

        # TODO: HIGH, doc_name needs to be regexp checked that it can be used as a path.
        self._dir_name = dir_name if dir_name is not None else doc_name

    def render(self):
        doc_path = pathlib.Path(self._dir_name)
        # If the directory does not exist in the CWD, create it
        if not doc_path.exists():
            doc_path.mkdir(parents=True)
        # Save the CWD, switch to the doc working dir
        cwd = os.getcwd()
        os.chdir(doc_path)
        # Build all content 
        for a_content_el in self._content_elements.values():
            a_content_el.render()
        # Restore the cwd
        os.chdir(cwd)

    def element_by_path(self, path):
        path_elements = path.split("/")
        try:
            target_element = self._content_elements[path_elements[0]]
        except KeyError:
            raise Exception(f"{path_elements[0]} does not exist")
        if isinstance(target_element, Page) and len(path_elements) > 1:
            raise Exception(f"{path_elements[0]} does not exist")
        if isinstance(target_element, Document) and len(path_elements) > 1:
            return target_element.element_by_path("/".join(path_elements[1:]))
        return target_element

    def get_root(self):
        if self.parent is not None:
            return self.parent.get_parent()
        else:
            return self

    def get_disk_path(self):
        if self.parent is not None:
            return f"{self.parent.get_disk_path()}/{self._dir_name}"
        else:
            return f"{self._dir_name}"


class Page(RenderableDocElement):
    """
    :param page_name: A logical name for the page
    :type page_name: str
    :param data_context: A mapping from variable names to values.
    :type data_context: dict
    :param external_resources: A list of external resources required for this element (e.g. stylesheets, scripts).
    :type external_resources: list[str]
    :param file_name: The filename for this page if it has to be set explicitly.
    :type file_name: str
    """
    def __init__(self, page_name, template, data_context, extra_resources=[], file_name=None):
        super().__init__(page_name)
        self._template = template
        self._data_context = data_context
        self._extra_resources = extra_resources
        # TODO: HIGH, file_name needs to be regexp checked that it can be used as a path.
        self._file_name  = file_name if file_name is not None else f"{page_name}.html"

    def _link_to_element(self, desc, path):
        return f"<a href=\"{self.get_root().element_by_path(path).get_disk_path()}\">{desc}</a>"

    def render(self):
        # Build the page that will be rendered
        html_pg = HTMLPage(HTMLBody([
                                     DefaultDocVisMarkdownDiv(self._template, 
                                                              self._data_context|{"link_to_element":self._link_to_element},
                                                              external_resources=self._extra_resources)
                                    ]), 
                           HTMLHead([HTMLTitle(self.name),
                                     HTMLMeta({"charset":"utf-8"}),
                                    ])
                          )
        with open(self._file_name,"wt") as fd:
            fd.write(html_pg.render())

    def get_disk_path(self):
        if self.parent is not None:
            return f"{self.parent.get_disk_path()}/{self._file_name}"
        else:
            return f"{self._file_name}"

    def get_root(self):
        if self.parent is not None:
            return self.parent.get_root()
        else:
            return self
