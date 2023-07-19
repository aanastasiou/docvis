================
DocVis internals
================

Users of DocVis do not *have to* know the internal details of DocVis' design but
its awareness can help in understanding why the API looks like the way it does.

This section begins with a very brief introducion to the problem that DocVis deals with, 
followed by the design of DocVis.

What was DocVis designed to do?
===============================

DocVis was designed to create standalone HTML documents **with** interactive plots.

These are documents that allow a degree of data exploration, along with necessary text 
that is required to embed what the plots show to a specific context.

In its primary use-case, DocVis is used to take results from various analysis methods and 
add around them the text that is necessary to make sense of the results *in a specific scientific context*.


Here is a ficitious but realistic example:

* Suppose a database of categorical data.

  * For example:

    * ``Dataset1 : {A,B,F,B,A,F,F,A}``
    * ``Dataset2 : {1,2,3,3,2,3,1,1}``

* These data could be organised in to this database from various processes (e.g. financial, engineering and others).

* Suppose further that one of the most common operations across such datasets is to obtain
  a count of each category in the dataset.

  * For example, asking for a count on ``Dataset1`` would return something like:

    ``Dataset1_Count: {A:3, B:2, F:3}``

* A user has the ability to request the "counts" of a specific dataset and plot the results
  in the form of a histogram [1]_.

  * Note here that if we were to write this directly in Python, all we would have created 
    would be a diagram.

* Upon obtaining that histogram, they also want to be able to write some `prose <https://en.wikipedia.org/wiki/Prose>`_
  around that histogram and forward it to non-technical people who are interested on the 
  results and their impact on their field.

It is possible to do this by:

1. Having 4-5 documents open and copying and pasting between them; or
2. Some kind of bash script automation; or
3. Some kind of "dashboard application" and so on.

Each one of these solutions has pros and cons, but *none* of them would be as simple as 
a plain standalone HTML file that can be shared around in an email or easily be served
and updated dynamically if required.

This is what DocVis was designed to do.

.. note::

   Obviously, there are more details to DocVis' use case but for the moment,
   this is the most compact way of explaining the use case that gave birth to it.


Why not use a template engine?
==============================

It is difficult to answer this question without first considering the data structures that 
represent each entity, whether that is pure HTML, Markdown or plain text.

The key problem one might come across with a template engine is that:

*There is no way to customise the appearance of non-string elements*

Template engines assume, throughout their design, that all actions of the template language
are supposed to lead to a string representation which ends up in the output. This is true
whether the template languages does "complex" operations (such as iteration through a 
data structure), or less complex operations such as content filters and formatters.

Dynamic plots **are** represented as strings (e.g. HTML tags) but also carry another 
element that is essential for their proper rendering.

If that was sent through a template engine, it would attempt to render an object with 
two properties.

Therefore, a way was needed to "intercept" the templating process to create the dynamic 
plots on the fly.


So, how does it work?
=====================

Docvis recreates a subset of the HTML DOM, small enough to be able to generate 
simple HTML pages.

Each HTML element, accepts "content", attributes and "external dependencies" and when 
it is rendered it produces "HTML code" and "external dependencies".

.. graphviz::

    digraph foo{
            graph [rankdir=LR, splines="spline", nodesep="0.8", bgcolor="transparent"];
            node [shape="plaintext", width=1.5];
            edge [color="#283044"];
    
            node_content [label=<Content>, fontcolor="#D52941"];
            node_attributes [label=<Attributes>, fontcolor="#D52941"];
            node_external_deps [label=<External <br/>Dependencies>, fontcolor="#283044"];
    
            node_html_element [label=<HTML Element>, fontcolor="#2191FB"];
    
            node_html_code [label=<HTML Code>, fontcolor="#D52941"];
            node_html_deps [label=<External <br/>Dependencies>, fontcolor="#283044"];
    
            node_content:e -> node_html_element:w;
            node_attributes:e -> node_html_element:w;
            node_external_deps:e -> node_html_element:w;
            node_html_element:e -> node_html_code:w;
            node_html_element:e -> node_html_deps:w;
    
       }

Everything is self-explanatory in this diagram, except perhaps "External Dependencies".

"External Dependencies" are any resources that:

1. Do not participate in the rendering of the HTML element
2. Are absolutely required for the element to be rendered properly.

Here is an example for producing the following HTML snippet:

.. code-block:: html

  <div class="danger">
      Danger, Will Robinson!
  </div>


.. graphviz::

    digraph foo{
            graph [rankdir=LR, splines="spline", nodesep="0.8", bgcolor="transparent"];
            node [shape="plaintext", width=1.5];
            edge [color="#283044"];
    
            node_content [label=<Content <br/> Danger, Will Robinson!>, fontcolor="#D52941"];
            node_attributes [label=<Attributes <br/> class=&ldquo;danger &ldquo;>, fontcolor="#D52941"];
            node_external_deps [label=<External <br/>Dependencies <br/> [&ldquo;stylesheet.css &ldquo;]>, fontcolor="#283044"];
    
            node_html_element [label=<HTML Element <br/> div>, fontcolor="#2191FB"];
    
            node_html_code [label=<HTML Code <br/> &lt;div class=&ldquo;danger&ldquo;&gt; <br/> &nbsp;&nbsp;&nbsp;Danger, Will Robinson! <br/> &lt; /div &gt;>, fontcolor="#D52941"];
            node_html_deps [label=<External <br/>Dependencies <br/> [&ldquo;stylesheet.css &ldquo;]>, fontcolor="#283044"];
    
            node_content:e -> node_html_element:w;
            node_attributes:e -> node_html_element:w;
            node_external_deps:e -> node_html_element:w;
            node_html_element:e -> node_html_code:w;
            node_html_element:e -> node_html_deps:w;
    
       }

Although this is not a very interesting example, if we define a ``div`` ``HTMLElement``, 
we have all the necessary information to generate an HTML page that would render it 
properly.

Where it gets more interesting, is when we start nesting HTML elements as in the following:

.. code-block:: HTML

   <div class="danger">
      <p class="personalised">Danger, Will Robinson!</p>
   </div>

In this case, "Content" is an ``HTMLElement`` itself, resulting in:

.. graphviz::

    digraph foo{
            graph [rankdir=LR, splines="spline", nodesep="0.8", bgcolor="transparent"];
            node [shape="plaintext", width=1.5];
            edge [color="#283044"];
    
            node_content [label=<Content <br/>>, fontcolor="#D52941"];
            node_attributes [label=<Attributes <br/> class=&ldquo;danger &ldquo;>, fontcolor="#D52941"];
            node_external_deps [label=<External <br/>Dependencies <br/> [&ldquo;stylesheet.css &ldquo;]>, fontcolor="#283044"];
    
            node_html_element [label=<HTML Element <br/> div>, fontcolor="#2191FB"];
    
            node_html_code [label=<HTML Code <br/> &lt;div class=&ldquo;danger&ldquo;&gt; <br/> &nbsp;&nbsp;&nbsp; &lt;p class=&ldquo;personalised&ldquo;&gt; <br/> &nbsp;&nbsp;&nbsp;Danger, Will Robinson! <br/> &lt; /p &gt; >, fontcolor="#D52941"];
            node_html_deps [label=<External <br/>Dependencies <br/> [&ldquo;stylesheet.css &ldquo;, <br/>&ldquo;person_messages.css &ldquo;]>, fontcolor="#283044"];

            node_content_p [label=<Content <br/> Danger, Will Robinson!>, fontcolor="#D52941"];
            node_attributes_p [label=<Attributes <br/> class=&ldquo;personalised &ldquo;>, fontcolor="#D52941"];
            node_external_deps_p [label=<External <br/>Dependencies <br/> [&ldquo;person_messages.css &ldquo;, <br/>]>, fontcolor="#283044"];
    
            node_html_element_p [label=<HTML Element <br/> p>, fontcolor="#2191FB"];
    
            node_html_code_p [label=<HTML Code <br/> &lt;p class=&ldquo;personalised&ldquo;&gt; <br/> &nbsp;&nbsp;&nbsp;Danger, Will Robinson! <br/> &lt; /p &gt;>, fontcolor="#D52941"];
            node_html_deps_p [label=<External <br/>Dependencies <br/> [&ldquo;person_messages.css &ldquo;]>, fontcolor="#283044"];

    
            node_content:e -> node_html_element:w;
            node_attributes:e -> node_html_element:w;
            node_external_deps:e -> node_html_element:w;
            node_html_element:e -> node_html_code:w;
            node_html_element:e -> node_html_deps:w;

            node_content_p:e -> node_html_element_p:w;
            node_attributes_p:e -> node_html_element_p:w;
            node_external_deps_p:e -> node_html_element_p:w;
            node_html_element_p:e -> node_html_code_p:w;
            node_html_element_p:e -> node_html_deps_p:w;

            node_html_code_p:e -> node_content:w;
            node_html_deps_p:e -> node_content:w;

       }

Notice here how the External Dependencies of the ``div`` element have accumulated the 
external dependencies of its nested ``p`` element and how the ``div`` element's HTML code
has also absorbed (with indenting) the HTML Code of the (deeper) ``p`` element.

That is all.

With this framework established:

1. Markdown is handled as a ``div`` whose "Content" is first interpreted by ``python-markdown`` (with ``TOC`` and ``extras`` enabled).

   * This Markdown rendering is not only confined to text but given a dictionary of 
     variable names to values, it also allows for portions of the text to be entirely 
     dynamic.

2. Plots themselves generate their own HTML Code and External Dependencies [2]_

3. **Dynamic** plots, that are reconfigurable right from the markup, are 
   implemented as an extra interpreted layer *over* Markdown.


Dynamic Plots
=============

Dynamic Plots that are reconfigurable right from the markup are implemented 
as "function calls", delimited by a start marker and an end marker.

As per the introductory example:

.. code-block:: text

   %$ line(x=x, y=y
           title='Line diagram', x_axis_label='n', y_axis_label='Amplitude', width=400) $%

Within ``%$``, ``$%``, text that matches the profile of a "function call", is captured.

This includes the "name of the function" along with its parameters.

Ultimately, these "function calls" are looked up to a table of specific functions, 
called and their result is added to the rest of the rendering as an ``HTMLElement`` 
with its own "Content" and "External Dependencies"

.. note::

   These "function calls" are **not** towards any Python function but only to the 
   specific functions that implement the dynamic plots

Dynamic plots also have full access to the memory context and can substitute variables 
for their values.

In the above example, the parameters ``x, y`` of ``line`` take values from the variables
``x``, ``y`` of the context.

In this way, users can change the layout of their documents both in terms of 
prose as well as plots.

Putting it all together
=======================

.. image:: resources/figures/docvis_example.png

For more information on using DocVis, please :ref:`see here <usage>`


---

.. [1] A histogram would tell us how frequently each category appears in the categorical 
       dataset. For example, for the dataset {A, B, B, A, C, D, C}, the histogram would 
       return {A:2, B:2, C:2, D:1}. For more information please see `here <https://en.wikipedia.org/wiki/Histogram>`_

.. [2] For Bokeh, see ``components`` `here <https://docs.bokeh.org/en/latest/docs/reference/embed.html#bokeh.embed.components>`_, similar treatment applies for any other element.



