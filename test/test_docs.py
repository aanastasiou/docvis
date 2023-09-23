"""
Tests for the complete documents functionality

:author: Athanasios Anastasiou
:date: Sep 2023
"""

from docvis.docs import Document, Page

def test_init_page():
    """
    Pages are instantiated by a logical name, template content and data
    """

    q = Page("main",
             "Something",
             {})

    assert q._physical_name == "main.html"

def test_make_path_relative():
    """
    Tests the function that makes links relative
    """

    q = Page("alpha", "Something", {})

    # Test backwards
    assert q.make_path_relative("main/d1/p1", "main/p1") == "../p1"
    # Test forwards
    assert q.make_path_relative("main/d1/p1", "main/d1/p2/p2") == "p2/p2"

def test_init_document():
    """
    Documents are composed of other documents or pages
    """

    d2 = Document("subdoc",
                  [
                      Page("p", "Whatever", {}),
                      Page("d", "Something", {})
                  ])

    d1 = Document("main",
                  [
                      Page("index", "The index", {}),
                      d2
                  ])

    assert id(d1.element_by_path("main")) == id(d1)
    assert id(d1.element_by_path("main/subdoc")) == id(d2)

def test_init_document_multi_source():
    """
    If an already parented element (Document or Page) is added to a Document, it gets copied across
    """

    p1 = Page("p1", "Some page", {})
    p2 = Page("p2", "Some other page", {})

    d1 = Document("d1", [p1])
    d2 = Document("d2", [p1,p2])
 
    assert id(d1.element_by_path("d1/p1")) != id(d2.element_by_path("d2/p1"))

