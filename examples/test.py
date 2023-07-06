from docvis.core import HTMLMeta, HTMLStylesheet, HTMLTitle, HTMLBody, HTMLPage, HTMLScript
from docvis.markdown import HTMLMarkdownDiv, HTMLPreProcMarkdownDiv
from docvis.bokeh import HTMLBokehLinePlot, HTMLBokehBarPlot
import sys

def line(**kwargs):
    return HTMLBokehLinePlot(**kwargs).render()

def bar(**kwargs):
    return HTMLBokehBarPlot(**kwargs).render()


if __name__ == "__main__":
    page_name = "Sample page"
    # Create a very simple HTML page
    the_page = HTMLPage(HTMLBody([
                                  HTMLPreProcMarkdownDiv("# Heading\n\nWelcome to this page. Its name is {{page_name}}\n\n## Some subheading\n\n{{P1}}\n\n## Some other subheading\n\n{{P2}}\n%$ line(x=x, y=y, title='Boing', width=400) $%\n", 
                                                         {"line":line,
                                                          "bar":bar},
                                                         {"page_name":page_name,
                                                          "P1":"Something was here before",
                                                          "P2":"Something else was here before",
                                                          "x":[0,1,2,3,4,5,6,7],
                                                          "y":[0,1,2,3,2,1,0,1],
                                                         })],["basic_style.css"]),
                        [
                         HTMLMeta({"charset":"utf-8"}), 
                         HTMLTitle(page_name),
                        ])

    sys.stdout.write(the_page.render())
