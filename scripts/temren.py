#!/usr/bin/env python
"""
``temren.py``
=============

A simple script to demonstrate the use of the ``HTMLPreprocMarkdown`` component.


:author: Athanasios Anastasiou
:date: Jul 2023
"""
from docvis.core import HTMLMeta, HTMLStylesheet, HTMLTitle, HTMLBody, HTMLPage, HTMLScript
from docvis.markdown import HTMLMarkdownDiv, HTMLPreProcMarkdownDiv
from docvis.bokeh import HTMLBokehLinePlot, HTMLBokehBarPlot
import sys
import click
import json


def line(**kwargs):
    return HTMLBokehLinePlot(**kwargs).render()

def bar(**kwargs):
    return HTMLBokehBarPlot(**kwargs).render()


@click.command()
@click.argument("template", type=click.Path(exists=True))
@click.argument("context", type=click.Path(exists=True))
def temren(template, context):
    """
    Renders an html file from a text description and a memory context
    """
    with open(template, "rt") as fd:
        template_data = fd.read()

    with open(context, "rt") as fd:
        context_data = json.load(fd)

    # Create a very simple HTML page
    the_page = HTMLPage(HTMLBody([
                                  HTMLPreProcMarkdownDiv(template_data, 
                                                         {"line":line,
                                                          "bar":bar},
                                                         "%\$",
                                                         "\$%",
                                                         context_data)],["basic_style.css"]),
                        [
                         HTMLMeta({"charset":"utf-8"}), 
                         HTMLTitle("Temren"),
                        ])

    sys.stdout.write(the_page.render())


if __name__ == "__main__":
    temren()


