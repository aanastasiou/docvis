from docvis.core import HTMLMeta, HTMLStylesheet, HTMLTitle, HTMLBody, HTMLPage, HTMLScript
from docvis.markdown import HTMLMarkdownDiv, HTMLPreProcMarkdownDiv
from docvis.bokeh import HTMLBokehLinePlot
import sys

if __name__ == "__main__":
    page_name = "Sample page"
    # Create a very simple HTML page
    the_page = HTMLPage(HTMLBody([
                                  HTMLPreProcMarkdownDiv("# Heading\n\nWelcome to this page. Its name is {{page_name}}\n\nAnd here it is \n\n{{my_plot}}", 
                                      {"page_name":page_name,
                                       "my_plot":HTMLBokehLinePlot(x=[0,1,2,3], y=[0,1,2,3])})
                                 ],["basic_style.css"]), 
                        [
                         HTMLMeta({"charset":"utf-8"}), 
                         HTMLTitle(page_name),
                        ])

    sys.stdout.write(the_page.render())
