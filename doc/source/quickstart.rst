.. _usage:

==========
Quickstart
==========

If you want to jump right into creating standalone documents that include interactive plots 
from data and markup, then feel free to skip to :ref:`markdown_and_data`.

Otherwise, stick with the normal flow of this section which starts from creating simple HTML
and builds up the layers one by one all the way to plots configurable from the markup.

This page might appear to be too long but this is because examples of the generated code are 
given along with Python code.

"Building up" HTML pages
========================

DocVis includes just enough functionality to build up very simple HTML pages.

Here is an example:

.. code-block:: python

   from docvis import HTMLPage, HTMLMeta, HTMLTitle, HTMLBody, HTMLParagraph

   if __name__ == "__main__":
       the_page = HTMLPage(HTMLBody([
                                     HTMLParagraph("Hello World")
                                    ]),
                           HTMLHead([
                                     HTMLTitle("My Title")
                                    ])
                          )
        rendered_page = the_page.render()

        print(rendered_page.code);

Unsurprisingly, this produces:

.. code-block:: html

   <!DOCTYPE html>
   <html>
       <head>
           <title>
               My Title
           </title>
       </head>
       
       <body>
           <p>
               Hello World
           </p>
       </body>
   </html>


Specifying attributes and adding external dependencies
------------------------------------------------------

But, now we want ``Hello World`` to print in white letters over a blue background [1]_

There are two ways to achieve this with DocVis:

1. Add inline style information to the paragraph element
2. Assign a CSS class from an external stylesheet [2]_

Adding inline style information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from docvis import HTMLPage, HTMLMeta, HTMLTitle, HTMLBody, HTMLParagraph

   if __name__ == "__main__":
       the_page = HTMLPage(HTMLBody([
                                     HTMLParagraph("Hello World", 
                                                   attributes={"style":"background-color:blue;color:white;"})
                                    ]),
                           HTMLHead([
                                     HTMLTitle("My Title")
                                    ])
                          )
        rendered_page = the_page.render()

        print(rendered_page.code);

Which produces:

.. code-block:: html

   <!DOCTYPE html>
   <html>
       <head>
           <title>
               My Title
           </title>
       </head>
       
       <body>
           <p style="background-color:blue; color:white;">
               Hello World
           </p>
       </body>
   </html>


Assigning a CSS class from an external stylesheet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from docvis import HTMLPage, HTMLMeta, HTMLTitle, HTMLBody, HTMLParagraph

   if __name__ == "__main__":
       the_page = HTMLPage(HTMLBody([
                                     HTMLParagraph("Hello World", 
                                                   attributes={"class":"highlighted"},
                                                   external_dependencies=["page_style.css"])
                                    ]),
                           HTMLHead([
                                     HTMLTitle("My Title")
                                    ])
                          )
        rendered_page = the_page.render()

        print(rendered_page.code);

The ``page_style.css`` file should be in the same working directory and is as follows:

.. code-block:: css

   .highlighted{
       background-color:blue;
       color:white;
   }

With these resources in place, the above code renders:

.. code-block:: html

   <!DOCTYPE html>
   <html>
       <head>
           <link rel="stylesheet" href="pagestyle.css"/>
           <title>
               My Title
           </title>
       </head>
       <body>
           <p class="highlighted">
               Hello World
           </p>
       </body>   
   </html>

Notice here how the paragraph's dependency has "bubbled up" all the way to the page's ``<head>`` 
element.

Web pages from Markdown
=======================

DocVis' HTML capability is there to support Markdown and more complex visualisation elements that 
eventually "render down" to HTML.

To create a page from Markdown:

.. code-block:: python

   from docvis import HTMLPage, HTMLMeta, HTMLTitle, HTMLBody, HTMLParagraph, HTMLMarkdownDiv

   if __name__ == "__main__":
       the_page = HTMLPage(HTMLBody([
                                     HTMLMarkdownDiv("# Welcome\n\n This content was created entirely in `Markdown`\n\n")
                                    ]),
                           HTMLHead([
                                     HTMLTitle("My Title"),
                                    ])
                          )
       rendered_page = the_page.render()
      
       print(rendered_page);

This would result in:

.. code-block:: html

   <!DOCTYPE html>
   <html>
       <head>
           <title>
               My Title
           </title>
       </head>
       
       <body>
           <div>
               <h1 id="welcome">Welcome</h1>
               <p>This content was created entirely in <code>Markdown</code></p>
           </div>
       </body>
   </html>

Adding dynamic content
----------------------

To have elements dynamically inserted in the content, add a context to ``HTMLMarkdownDiv`` 
and reference its contents in the template.

Only the modified line of the above listing will be shown here:

.. code-block:: python

   HTMLMarkdownDiv("# Welcome {{user_name}}\n\n This content was created entirely in `Markdown`\n\n",{"user_name":"Bill"})

Which results in:

.. code-block:: html

   <!DOCTYPE html>
   <html>
       <head>
           <title>
               My Title
           </title>
       </head>
       
       <body>
           <div>
               <h1 id="welcome-user_name">Welcome Bill</h1>
               <p>This content was created entirely in <code>Markdown</code></p>
           </div>
       </body>
   </html>


.. _markdown_and_data:

Web pages from Markdown with dynamic plots
==========================================

The easiest way to include all plots supported by a given DocVis release, is to use
the ``DefaultDocVisMarkdownDiv``.

At the current version, DocVis supports two plots: ``line, bar``, both of which are 
implemented via Bokeh.

To insert a line plot, try the following:

.. code-block:: python
   
   if __name__ == "__main__":
       the_page = HTMLPage(HTMLBody([
                                     DefaultDocVisMarkdownDiv("# Welcome {{user_name}}\n\n This content was created entirely in `Markdown`\n\n%$ line(x=x,y=y) $%",
                                                              {"x":[0,1,2,3],
                                                               "y":[0,1,0,1]})
                                    ]),
                           HTMLHead([
                                     HTMLTitle("My Title"),
                                    ])
                          )
       rendered_page = the_page.render()
    
       print(rendered_page);


Now, this would result in the following, certainly non-trivial (but nevertheless stand-alone and browsable) HTML:

.. code-block:: html

   <!DOCTYPE html>
   <html>
       <head>
           <script src="https://cdn.bokeh.org/bokeh/release/bokeh-gl-3.2.0.min.js" defer></script>       
           <script type="text/javascript">
               (function() {
         const fn = function() {
           Bokeh.safely(function() {
             (function(root) {
               function embed_document(root) {
               const docs_json = '{"5c2085e8-aa7d-4c1f-a533-9557482df52a":{"version":"3.2.0","title":"Bokeh Application","roots":[{"type":"object","name":"Figure","id":"p1039","attributes":{"width":200,"height":200,"x_range":{"type":"object","name":"DataRange1d","id":"p1040"},"y_range":{"type":"object","name":"DataRange1d","id":"p1041"},"x_scale":{"type":"object","name":"LinearScale","id":"p1049"},"y_scale":{"type":"object","name":"LinearScale","id":"p1050"},"title":{"type":"object","name":"Title","id":"p1042","attributes":{"text":"Title"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"p1074","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"p1068","attributes":{"selected":{"type":"object","name":"Selection","id":"p1069","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"p1070"},"data":{"type":"map","entries":[["x",[0,1,2,3]],["y",[0,1,0,1]]]}}},"view":{"type":"object","name":"CDSView","id":"p1075","attributes":{"filter":{"type":"object","name":"AllIndices","id":"p1076"}}},"glyph":{"type":"object","name":"Line","id":"p1071","attributes":{"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#1f77b4"}},"nonselection_glyph":{"type":"object","name":"Line","id":"p1072","attributes":{"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#1f77b4","line_alpha":0.1}},"muted_glyph":{"type":"object","name":"Line","id":"p1073","attributes":{"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#1f77b4","line_alpha":0.2}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"p1048","attributes":{"tools":[{"type":"object","name":"PanTool","id":"p1061"},{"type":"object","name":"WheelZoomTool","id":"p1062"},{"type":"object","name":"BoxZoomTool","id":"p1063","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"p1064","attributes":{"syncable":false,"level":"overlay","visible":false,"left_units":"canvas","right_units":"canvas","bottom_units":"canvas","top_units":"canvas","line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5}}}},{"type":"object","name":"SaveTool","id":"p1065"},{"type":"object","name":"ResetTool","id":"p1066"},{"type":"object","name":"HelpTool","id":"p1067"}]}},"left":[{"type":"object","name":"LinearAxis","id":"p1056","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"p1057","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"p1058"},"axis_label":"Y Axis","major_label_policy":{"type":"object","name":"AllLabels","id":"p1059"}}}],"below":[{"type":"object","name":"LinearAxis","id":"p1051","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"p1052","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"p1053"},"axis_label":"X Axis","major_label_policy":{"type":"object","name":"AllLabels","id":"p1054"}}}],"center":[{"type":"object","name":"Grid","id":"p1055","attributes":{"axis":{"id":"p1051"}}},{"type":"object","name":"Grid","id":"p1060","attributes":{"dimension":1,"axis":{"id":"p1056"}}}]}}]}}';
               const render_items = [{"docid":"5c2085e8-aa7d-4c1f-a533-9557482df52a","roots":{"p1039":"cb639da2-583e-4ecc-8dd6-b5a083a32de7"},"root_ids":["p1039"]}];
               root.Bokeh.embed.embed_items(docs_json, render_items);
               }
               if (root.Bokeh !== undefined) {
                 embed_document(root);
               } else {
                 let attempts = 0;
                 const timer = setInterval(function(root) {
                   if (root.Bokeh !== undefined) {
                     clearInterval(timer);
                     embed_document(root);
                   } else {
                     attempts++;
                     if (attempts > 100) {
                       clearInterval(timer);
                       console.log("Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing");
                     }
                   }
                 }, 10, root)
               }
             })(window);
           });
         };
         if (document.readyState != "loading") fn();
         else document.addEventListener("DOMContentLoaded", fn);
       })();
           </script>
       
           <script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.2.0.min.js" defer></script>   
           <script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.2.0.min.js" defer></script>
           <title>
              My Title
           </title>
           <script src="https://cdn.bokeh.org/bokeh/release/bokeh-mathjax-3.2.0.min.js" defer></script>
           <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.2.0.min.js" defer></script>
       </head>
   
       <body>
           <div>
               <h1 id="welcome-user_name">Welcome </h1>
               <p>This content was created entirely in <code>Markdown</code></p>
               <p>
               <div id="cb639da2-583e-4ecc-8dd6-b5a083a32de7" data-root-id="p1039" style="display: contents;"></div>
               </p>
           </div>
       </body>
   </html>

Notice here (again) that all external-dependencies have bubbled up to the ``<head>`` element of the page and that 
the line plot was defined by code in the Markdown and used data provided in the context.

.. note::
   Everything explained in earlier sections regarding adding external dependencies 
   and attributes to elements, also apply to all the "Markdown Divs" that are demonstrated here.

Standalone pages with plots from JSON and Markdown files
========================================================

DocVis was not written to produce output from static files, but it comes with a script 
(:ref:`temren <temren>`) that does exactly that and serves as a quick example of DocVis' functionality.

So, with DocVis installed, create two files: one JSON file with a set of data and a Markdown 
file specifying how these data are supposed to be rendered.

Here is an example:

``context.md`` could contain:

.. code-block:: json

   {
   	"x": [0,1,2,3,4,5,6,7],
   	"y": [0,1,2,3,2,1,0,1],
   }

``template.md`` could contain:

.. code-block:: markdown

   # Diagram showcase
   
   # Introduction
   
   This markdown document showcases the basic functionality of Docvis.
   
   In addition to markdown notation, this template file contains text segments 
   enclosed in `%$`, `$%` tags.
   
   These text-segments *resemble* a function call only in form, to capture the necessary 
   parameters required and resolve to embeddable interactive Bokeh graphs that are fully 
   parametrised via the text itself.
   
   This gives the opportunity to an **end-user** to customise both the content and appearance 
   of a document, from the text, to the diagrams included and embed a set of graphs that emerge 
   from computations within a specific analysis context, **without** changing any of the 
   underlying code.
   
   The following sections showcase elements that are available through Docvis right now (more
   are being added).
   
   Oh and its appearance is fully parametriseable by the adjacent css file.
   
   ## Line plot
   
   %$ line(x=x, y=y, 
           title='Line diagram', x_axis_label='n', y_axis_label='Amplitude', width=400) $%
   
   
   ## Bar plot
   
   %$ bar(x=["A","B","C"], y=[30,20,30], title='Bar diagram', x_axis_label='Quantity', y_axis_label='Category', width=400) $%
   
   ---

Then on your command line enter:

::

  > temren template.md context.json > htmlpage.html


This command will produce the HTML page that is presented on the cover of this documentation website.

In fact, it will be reproduced exactly, if in addition to the above you have a ``page_style.css`` along 
the following lines:

.. code-block:: css
   
   body{
       font-family:Raleway, Helvetica;
       margin-left:auto;
       margin-right:auto;
       width:80%;
   }



----

.. [1] Not the most impressive thing to do, but just an example.
.. [2] Yes, you could also add a ``<style>`` paragraph in the ``<head>``, but to date (July 2023) these
       are the two ways supported by DocVis.



