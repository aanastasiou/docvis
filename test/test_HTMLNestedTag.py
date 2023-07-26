"""
Tests basic HTML nested components

:author: Athanasios Anastasiou
:date: Jun 2023
"""

from docvis.core import HTMLNestedTag, HTMLRenderedElement


def test_HTMLTag_render():
    the_tag = HTMLNestedTag("div", []).render()

    assert type(the_tag) is HTMLRenderedElement

def test_HTMLTag_ext_res():
    the_tag = HTMLNestedTag("div", [], external_resources=["blue.js"]).render()

    assert type(the_tag) is HTMLRenderedElement
    assert len(the_tag.extra_resources) == 1
    assert the_tag.extra_resources[0] == "blue.js"
    assert the_tag.code == "<div></div>"

def test_HTMLTag_attrs():
    the_tag = HTMLNestedTag("div", [], attributes={"name":"alpha"}).render()

    assert type(the_tag) is HTMLRenderedElement
    assert len(the_tag.extra_resources) == 0
    assert the_tag.code == "<div name=\"alpha\"></div>"


