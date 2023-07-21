.. _usage:

============
Using Docvis
============

"Building up" HTML pages
========================

DocVis includes just enough functionality to build up very simple HTML pages.

Here is an example:

.. code-block:: python

   from docvis import HTMLPage, HTMLMeta, HTMLTitle, HTMLBody, HTMLParagraph

   if __name__ == "__main__":
       the_page = HTMLPage(HTMLBody


DocVis was not written to render static files, but it comes with a script (:ref:`temren <temren>`) that does exactly that 
and serves as a quick example of DocVis' functionality.

The whole script is approximately 20 lines of code, one of which does all the initialisation
of the key component. This line is as follows:

.. code-block:: python





----

.. [1] dfdf



