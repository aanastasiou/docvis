"""
Tests the markdown related components

:author: Athanasios Anastasiou
:date: July 2023
"""

from docvis.markdown import HTMLMarkdownDiv

def test_HTMLMarkdownDiv():
    the_tag = HTMLMarkdownDiv("# Heading\n\nSome text",{}).render()

    assert the_tag.code == "<div><h1 id=\"heading\">Heading</h1>\n<p>Some text</p></div>"


