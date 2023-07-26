"""
Tests common HTML components

:author: Athanasios Anastasiou
:date: Jun 2023
"""

from docvis.core import HTMLHead, HTMLMeta, HTMLStylesheet, HTMLPassthrough, HTMLScript, HTMLTitle, HTMLBody, HTMLDiv, HTMLParagraph


def test_HTMLHead():
    the_tag = HTMLHead([HTMLParagraph("Content"),]).render()

    the_tag.code == "<p>\nContent\n</p>"


def test_HTMLMeta():
    the_tag = HTMLMeta({"charset":"utf-8"}).render()

    assert the_tag.code == "<meta charset=\"utf-8\"/>"

def test_HTMLStylesheet():
    the_tag = HTMLStylesheet("some_style.css").render()

    assert the_tag.code == "<link rel=\"stylesheet\" href=\"some_style.css\"/>"

def test_HTMLPassthrough():
    the_tag = HTMLPassthrough("This is not valid HTML").render()

    assert the_tag.code == "This is not valid HTML"

def test_HTMLScript():
    the_tag = HTMLScript("my_script.js").render()

    assert the_tag.code == "<script src=\"my_script.js\" defer></script>"


def test_HTMLTitle():
    the_tag = HTMLTitle("My page").render()

    assert the_tag.code == "<title>My page</title>"

def test_HTMLBody():
    the_tag = HTMLBody([]).render()

    assert the_tag.code == "<body></body>"

def test_HTMLDiv():
    the_tag = HTMLDiv([]).render()

    assert the_tag.code == "<div></div>"

def test_HTMLParagraph():
    the_tag = HTMLParagraph("Hello world").render()

    assert the_tag.code == "<p>Hello world</p>"




