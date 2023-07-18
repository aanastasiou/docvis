.. docvis documentation master file, created by
   sphinx-quickstart on Wed Jun 14 13:05:22 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to docvis's documentation!
==================================

Docvis enables Python3 programs to produce standalone HTML documents with dynamically reconfigurable 
elements, right from the markup.

Markup languages provide great flexibility in creating documents with very little effort, compared to 
writing HTML directly. However, their "markings" are typically used to modify the appearance of a span 
of text and are not meant to accept parameters that modify the end result of the markup.

Docvis ammends that by providing an extra pre-processing layer that captures the equivalent of a "tag"
along with parameters that customise its appearance.

The motivating use-case for Docvis was to enable **end-users** to define the structure of a document
via Markdown **both** in terms of text and its appearance **as well as** diagrams and their apperance.

Here is an example:

.. image:: resources/figures/docvis_example.png


Docvis is largely based on `Bokeh <https://docs.bokeh.org/en/latest/index.html>`_ but can interoperate with 
many different plotting "backends".


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
