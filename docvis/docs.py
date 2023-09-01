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
    def __init__(self, logical_name, physical_name=None, parent=None):
        # TODO: HIGH, doc_name needs to be regexp checked that it can be used as a path.
        self._logical_name = logical_name
        self._physical_name = physical_name if physical_name is not None else logical_name
        self._parent = parent
        
    @property
    def logical_name(self):
        return self._logical_name

    @property
    def physical_name(self):
        return self._physical_name

    @property
    def parent(self):
        return self._parent

    def get_disk_path(self):
        if self.parent is not None:
            prefix = self.parent.get_disk_path()

            return f"{prefix}{'/' if len(prefix)>0 else ''}{self.physical_name}"
        else:
            return ""


    def get_root(self):
        if self.parent is not None:
            return self.parent.get_root()
        else:
            return self

    def collect_parents(self):
        if self._parent is not None:
            return {self._parent} | self._parent.collect_parents()
        else:
            return set()



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
        # Check that no circular references are added
        prohibited_elements = map(id, self.collect_parents())
        for an_element in content_elements:
            if id(an_element) in prohibited_elements:
                raise Exception(f"Element {an_element.logical_name}({an_elemen.physical_name} is causing a circular reference")

        # Content elements should not have already been parented
        for an_element in content_elements:
            if an_element.parent is not None:
                raise Exception(f"{an_element} already belongs to a document hierarchy")

        # Content elements should not contain a page whose logical name is "index"
        for an_element in content_elements:
            if an_element.logical_name == "index":
                raise Exception("No content page should be named 'index'")
        
        # Add the index page
        index_page._logical_name = "index"
        self._content_elements = {}
        self._content_elements |= {"index":index_page}
        self._content_elements |= dict([(c_key, c_el) for c_key, c_el in map(lambda x:(x.logical_name, x), content_elements)])

        # All elements are parented to the current element
        # This works because all elements are copies of the originals and can have 
        # different parents
        for an_element in self._content_elements.values():
            an_element._parent = self

    def render(self):
        doc_path = pathlib.Path(self.physical_name)
        # If the directory does not exist in the CWD, create it
        if not doc_path.exists():
            doc_path.mkdir(parents=True)
        # Save the CWD
        cwd = os.getcwd()
        # Switch to the doc working dir
        os.chdir(doc_path)
        # Get the index page
        index_page = list(filter(lambda x:x.logical_name == "index", self._content_elements.values()))
        # If an index page has been provided then render it
        if len(index_page) > 0:
            index_page[0].render()
        # Build all content 
        for a_content_el in list(filter(lambda x:x.logical_name != "index",self._content_elements.values())):
            a_content_el.render()
        # Restore the cwd
        os.chdir(cwd)

    def element_by_path(self, path):
        path_elements = path.split("/")
        root_logical_name = self.get_root().logical_name 
        import pdb
        pdb.set_trace()
        if path_elements[0] != root_logical_name:
            raise Exception(f"{path} is not contained within the {root_logical_name} document")
        path_elements = path_elements[1:]
        try:
            target_element = self._content_elements[path_elements[0]]
        except KeyError:
            raise Exception(f"{path_elements[0]} does not exist")
        if isinstance(target_element, Page) and len(path_elements) > 1:
            raise Exception(f"{path_elements[0]} does not exist")
        if isinstance(target_element, Document) and len(path_elements) > 1:
            return target_element.element_by_path("/".join(path_elements[1:]))
        return target_element


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
        self._physical_name  = file_name if file_name is not None else f"{page_name}.html"

    def with_respect(self, from_path, to_path):
        # Find their common root
        pc_from = from_path.split("/")
        pc_to = to_path.split("/")
        u = 0
        for k in range(0, max(len(pc_from), len(pc_to))):
            pc_from_v = pc_from[k] if k < len(pc_from) else None
            pc_to_v = pc_to[k] if k < len(pc_to) else None
            if pc_from_v == pc_to_v:
                u += 1
        if u==0:
            return to_path
        else:
            return ("/".join([".."] * (len(pc_from)-u))) + "/" + "/".join(pc_to[u:])


    def _link_to_element(self, desc, path):
        uu = self.with_respect(self.get_disk_path(), self.get_root().element_by_path(path).get_disk_path())
        #import pdb
        #pdb.set_trace()
        #return f"<a href=\"{self.get_root().element_by_path(path).get_disk_path()}\">{desc}</a>"
        return f"<a href=\"{uu}\">{desc}</a>"

    def render(self):
        # Build the page that will be rendered
        html_pg = HTMLPage(HTMLBody([
                                     DefaultDocVisMarkdownDiv(self._template, 
                                                              self._data_context|{"link_to_element":self._link_to_element},
                                                              external_resources=self._extra_resources)
                                    ]), 
                           HTMLHead([HTMLTitle(self.logical_name),
                                     HTMLMeta({"charset":"utf-8"}),
                                    ])
                          )
        with open(self.physical_name,"wt") as fd:
            fd.write(html_pg.render())

    
