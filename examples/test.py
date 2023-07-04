from docvis.core import HTMLMeta, HTMLStylesheet, HTMLTitle, HTMLBody, HTMLPage, HTMLScript
from docvis.markdown import HTMLMarkdownDiv, HTMLPreProcMarkdownDiv
from docvis.bokeh import HTMLBokehLinePlot, HTMLBokehBarPlot
import sys

if __name__ == "__main__":
    page_name = "Sample page"
    # Create a very simple HTML page
    the_page = HTMLPage(HTMLBody([
                                  HTMLPreProcMarkdownDiv("# Heading\n\nWelcome to this page. Its name is {{page_name}}\n\n## Some subheading\n\n{{P1}}\n\n## Some other subheading\n\n{{P2}}\n", 
                                      {
                                       "page_name":page_name,
                                       "P1":HTMLBokehLinePlot(x=[0,1,2,3], y=[0,1,2,3]),
                                       "P2":HTMLBokehBarPlot(x=["A", "B", "C"], y=[10,20,10])})
                                 ],["basic_style.css"]), 
                        [
                         HTMLMeta({"charset":"utf-8"}), 
                         HTMLTitle(page_name),
                        ])

    sys.stdout.write(the_page.render())
