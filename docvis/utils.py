"""
Utilities
=========

Helper functions and pre-configured elements making up the default functionality of DocVis.

:author: Athanasios Anastasiou
:date: July 2023
"""

from .bokeh import HTMLBokehLinePlot, HTMLBokehBarPlot
from .markdown import HTMLPreProcMarkdownDiv

def bokeh_line_plot(**kwargs):
    """
    A typical bokeh line plot
    """
    return HTMLBokehLinePlot(**kwargs).render()


def bokeh_bar_plot(**kwargs):
    """
    A typical bokeh bar plot
    """
    return HTMLBokehBarPlot(**kwargs).render()


class DefaultDocVisMarkdownDiv(HTMLPreProcMarkdownDiv):
    """
    A pre-configured ``HTMLMarkdownDiv`` with all the default 
    functionality of DocVis.

    :param markdown_template: A markdown template using ``{{}}`` to reference variables in
                              the context.
    :type markdown_template: str
    :param context: A dictionary mapping variables to their values.
    :type context: dict[str, any]
    :param fun_table_modifier: A function table that can add or override function definitions
    :type fun_table_modifier: list[str, callable]
    :param external_resources: A list of external resources required for the content of 
                               this ``div`` to be rendered correctly.
    :type external_resources: list[str]
    :param attributes: A dictionary of attribute to attribute value listing additional 
                       attributes to assign to the resulting ``div``.
    :type attributes: dict[str, any]
    """
    def __init__(self, markdown_template, context, fun_table_modifier={}, external_resources=[], attributes={}):
        docvis_function_table = {"line":bokeh_line_plot,
                                 "bar":bokeh_bar_plot}
        super().__init__(markdown_template, 
                         docvis_function_table|fun_table_modifier, 
                         "%\$ ",
                         " \$%",
                         context, 
                         external_resources,
                         attributes)

