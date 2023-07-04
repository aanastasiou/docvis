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


