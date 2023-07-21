#!/usr/bin/env python
"""
``temren.py``
=============

A simple script to demonstrate the use of the ``HTMLPreprocMarkdown`` component.


:author: Athanasios Anastasiou
:date: Jul 2023
"""
from ..core import HTMLMeta, HTMLTitle, HTMLBody, HTMLPage, HTMLHead
from ..utils import DefaultDocVisMarkdownDiv, HTMLPreProcMarkdownDiv, bokeh_line_plot, bokeh_bar_plot
from ..exceptions import TemplatePreprocError
import sys
import click
import json


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
                                  DefaultDocVisMarkdownDiv(template_data, 
                                                           context_data)],
                                ["page_style.css"]),
                        HTMLHead([
                                  HTMLMeta({"charset":"utf-8"}), 
                                  HTMLTitle("Temren"),
                                  ])
                        )
    
    try:
        sys.stdout.write(the_page.render())
    except TemplatePreprocError as e:
        for an_error in e._errors:
            click.echo(an_error)



if __name__ == "__main__":
    temren()


