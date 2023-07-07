# Diagram showcase

# Introduction

This markdown document showcases the basic functionality of `fun-dsl`.

In addition to markdown notation, this template file contains "function calls" that are
enclosed in `%$`, `$%` tags.

These function calls resolve to embeddable interactive Bokeh graphs that are fully parametrised
via the markup.

In this way, and **end user** can embed a set of graphs that emerge from computations within a specific 
analysis context.

The following sections showcase the two elements that are available through Docvis right now (more
are being added).

Oh and its appearance is fully parametriseable by the adjacent css file.

## Line plot

%$ line(x=x, y=y, title='Line diagram', x_axis_label='n', y_axis_label='Amplitude', width=400) $%

## Bar plot

%$ bar(x=["A","B","C"], y=[30,20,30], title='Bar diagram', x_axis_label='Quantity', y_axis_label='Category', width=400) $%

