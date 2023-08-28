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

from .core import HTMLPage, HTMLBody, HTMLTitle, HTMLStylesheet, HTMLMeta, HTMLHead
from .utils import DefaultDocVisMarkdownDiv
import pathlib
import os

class Document:
    """
    :param doc_name: A logical name for the document
    :type doc_name: str
    :param index_page: A docvis.Page that references content pages.
    :type index_page: docvis.docs.Page
    :param content_pages: A list of docvis.docs.Page that represent each content page in the document
    :type content_pages: List[docvis.docs.Page]
    :param dir_name: The directory name if it has to be set explicitly.
    :type dir_name: str
    """
    def __init__(self, doc_name, index_page, content_pages, dir_name = None):
        self._doc_name = doc_name 
        self._index_page = index_page
        self._content_pages = content_pages
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
        # Build all content pages first
        for a_page in self._content_pages:
            a_page.render()
        # Build the index
        self._index_page.render()
        # Restore the cwd
        os.chdir(cwd)

        pass


class Page:
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
        self._page_name = page_name 
        self._template = template
        self._data_context = data_context
        self._extra_resources = extra_resources
        # TODO: HIGH, file_name needs to be regexp checked that it can be used as a path.
        self._file_name  = file_name if file_name is not None else f"{page_name}.html"

    def render(self):
        # Build the page that will be rendered
        html_pg = HTMLPage(HTMLBody([
                                     DefaultDocVisMarkdownDiv(self._template, 
                                                              self._data_context,
                                                              external_resources=self._extra_resources)
                                    ]), 
                           HTMLHead([HTMLTitle(self._page_name),
                                     HTMLMeta({"charset":"utf-8"}),
                                    ])
                          )
        with open(self._file_name,"wt") as fd:
            fd.write(html_pg.render())


