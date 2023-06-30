"""
Tests the basic HTML components

:author: Athanasios Anastasiou
:date: Jun 2023
"""

from docvis.core import HTMLTag, HTMLRenderedElement


def test_HTMLTag_render():
    the_tag = HTMLTag("div", "").render()

    assert type(the_tag) is HTMLRenderedElement

def test_HTMLTag_init_empty_tag():
    the_tag = HTMLTag("div", "", is_empty=True).render()

    assert the_tag.code == "<div/>"
    assert the_tag.extra_resources == []

def test_HTMLTag_init_tag():
    the_tag = HTMLTag("div", "").render()

    assert the_tag.code == "<div></div>"
    assert the_tag.extra_resources == []

def test_HTMLTag_init_tag_with_deps():
    the_tag = HTMLTag("div", "", ["some_script.js"]).render()

    assert the_tag.code == "<div></div>"
    assert the_tag.extra_resources == ["some_script.js"]

def test_HTMLTag_init_tag_with_attributes():
    the_tag = HTMLTag("div", "", attributes={"name":"myname"}).render()

    assert the_tag.code == "<div name=\"myname\"></div>"
    assert the_tag.extra_resources == []

def test_HTMLTag_init_tag_with_bool_attribute():
    the_tag = HTMLTag("div", "", attributes={"something":""}).render()

    assert the_tag.code == "<div something></div>"
    assert the_tag.extra_resources == []


