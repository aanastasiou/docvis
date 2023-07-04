import bokeh.plotting
import bokeh.embed
import bokeh.core.properties
import bokeh.models
import bokeh.resources

from .core import HTMLTag, HTMLRenderedElement


class HTMLBokehElement(HTMLTag):
    def __init__(self, **figure_params):
        super().__init__("", "")
        self._figure_params = {"width":200,
                               "height":200,
                               "x_axis_label":"X Axis",
                               "y_axis_label":"Y Axis",
                               "title":"Title",
                               "toolbar_location":"right",}
                               #"tools":[]}
        self._figure_params|=figure_params
        self._figure_object = bokeh.plotting.figure(**self._figure_params)
        self._external_resources = bokeh.resources.CDN.js_files

    def render(self,):
        script, div = bokeh.embed.components(self._figure_object)
        self._content = div
        return HTMLRenderedElement(extra_resources=self._external_resources + [script],
                                   code=super().render().code)


class HTMLBokehBarPlot(HTMLBokehElement):
    """
    Visualises categorical count data (i.e. MeSH terms and number of articles they appear in)
    """
    def __init__(self, 
                 x,
                 y,
                 is_vertical = False, 
                 **figure_params):
        """
        A horizontal bar plot

        :param a_query:
        :param categories_variable:
        :param count_variable:
        """
        super().__init__()
        self._x = x
        self._y = y
        self._is_vertical = is_vertical
        if self._is_vertical:
            self._figure_object = bokeh.plotting.figure(x_range = self._x, **self._figure_params)
        else:
            self._figure_object = bokeh.plotting.figure(y_range = self._x, **self._figure_params)

    def render(self):
        if self._is_vertical:
            self._figure_object.vbar(x = list(map(lambda x:x+0.5,range(0,len(self._x)))),
                                     top=self._y, 
                                     width=1.0)
        else:
            self._figure_object.hbar(y = list(map(lambda x:x+0.5, range(0, len(self._x)))),
                                     right=self._y, 
                                     height=1.0)
        return super().render()



class HTMLBokehLinePlot(HTMLBokehElement):
    def __init__(self, x, y, **figure_params):
        super().__init__()
        self._x = x
        self._y = y
        default_line_params = {"line_width":1, "line_dash":"solid"}
        self._line_params = {"line_width": figure_params.get("line_width", default_line_params["line_width"]),
                             "line_dash" : figure_params.get("line_dash", default_line_params["line_dash"])}


    def render(self):
        x_data = self._x
        y_data = self._y
        if self._x is None:
            x_data = list(range(0,len(self._y)))
        self._figure_object.line(x=x_data, y=y_data, **self._line_params)
        return super().render()


