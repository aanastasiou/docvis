from .core import StyledVisElement, StringTemplateVisElement
from .markdown import MarkdownVisElement
import networkx
import bokeh.plotting
import bokeh.embed
import bokeh.core.properties
import bokeh.models
#import bokeh.plotting.helpers
import uuid
import networkx
#import neoads

class BokehStyledVisElement(StyledVisElement):
    """
    Base class for all Bokeh Visualisation Elements.
    """
    def _before_render(self):
        """
        Initialises a Figure for the Bokeh element to render its graph on.

        Bokeh vis elements create a figure at _before_render, render on it at _main_render and return the standard
        response expected by VisElement at _after_render. In the case of Bokeh elements, these are rendered down to
        script tags as per Bokeh's specification.

        :return:
        """
        # Filter the style parameters for specific figure parameters honored by this element
        # TODO: LOW, Maybe an element should publish the style parameters it supports.
        figure_params = self._style.get_style_attributes(["plot_width", "plot_height", "x_axis_label", "y_axis_label", "title", "toolbar_location", "tools"])
        return bokeh.plotting.figure(**figure_params)

    def _after_render(self, init_object, figure_object):
        script, div = bokeh.embed.components(figure_object)
        return f"{div}\n{script}"


class BokehLinePlot(BokehStyledVisElement):
    """
    Produces a simple line plot
    """
    def _main_render(self, figure_object):
        line_params = self._style.get_style_attributes(["line_width", "line_dash"])
        if not "x" in self.context:
            self.context["x"] = list(range(0,len(self.context["y"])))
        figure_object.line(x=self.context["x"], y=self.context["y"], **line_params)
        return figure_object


class BokehStackPlot(BokehStyledVisElement):
    """
    Creates a stack plot from tag count data.
    Tag count data are usually provided by an iterable of "objects" that provide the raw column type data that are later
    organised into a pivot table.
    """
    def str2hex(self,a_str):
        """
        Converts a string to a hex number
        :param a_str: A string
        :return: An integer representing the string's hash value
        """
        hash = 0
        for i in range(0,len(a_str)):
            hash = ord(a_str[i]) + ((hash << 5) - hash)
        return hash

    def int2RGB(self,an_int):
        """
        Converts a hash value to an RGB colour
        :param an_int: An integer representing a string's hash value
        :return: A string representing the RGB colour value associated with the hash
        """
        c = str(hex(an_int & 0x00FFFFFF)).upper()[2:]
        return "#"+"00000"[0:6-len(c)] + c

    def __init__(self, a_query_object, query_parameters, time_variable, descriptor_variable, counts_variable, style=None, **context_args):
        super().__init__(style, **context_args)
        self.query_object = a_query_object
        self.query_parameters = query_parameters
        self.time_variable = time_variable
        self.descriptor_variable = descriptor_variable
        self.counts_variable = counts_variable

        # The query must be a pseudo data frame
        #if type(self.query_object) is not neoads.CompositeArrayObjectDataFrame:
        #    raise exception.DataStructureError(f"BokehStyledStackPlot received query object {type(self.query_object)}, expected compositeArrayObjectDataFrame")

    def _before_render(self):
        M = self.query_object.execute(params=self.query_parameters).pivot(index=self.descriptor_variable, columns=self.time_variable, values=self.counts_variable)
        F = (M.T).fillna(0.0)
        source = bokeh.models.ColumnDataSource.from_df(F)
        # The datestep MUST be string
        source[self.time_variable] = [str(x) for x in source[self.time_variable]]
        time_vector = source[self.time_variable]

        figure_params = self._style.get_style_attributes(["plot_width", "plot_height", "x_axis_label", "y_axis_label", "title", "toolbar_location", "tools"])
        figure_object = bokeh.plotting.figure(x_range=time_vector, **figure_params)
        return figure_object, source

    def _main_render(self, figure_object):

        # TODO: MEDIUM, Control normalisation with a flag
        # Normalise M
        # for an_index in M.keys():
        #     M.loc[:,an_index] = M.loc[:,an_index] / M.loc[:,an_index].sum()

        # M is now indexed by descriptors and its columns are associated with the time variable.
        # This is alright conceptually, but this is NOT how the ColumnDataSource expects variables.
        # Turn the data to a COLUMN data source (i.e., one column per descriptor rather than one column per time instance as it is now)
        # Also, if you leave nans in the dataset they are interperted as SKIP rather than EMPTY and the diagram gets all mangled up

        source = figure_object[1]
        # Render
        # Now we have all that we need to render the diagram
        # Helper variables
        descriptors = sorted(list(set(source.keys())-set([self.time_variable])))
        colors = [self.int2RGB(self.str2hex(an_item)) for an_item in descriptors]

        renderers = figure_object[0].vbar_stack(descriptors, x=self.time_variable, color=colors, width=1.0, source=source, legend=[bokeh.core.properties.value(x) for x in descriptors], name=descriptors)

        # TODO: HIGH, review this hover tool
        for r in renderers:
            year = r.name
            hover = bokeh.models.HoverTool(tooltips=[
                ("%s" % year, "@%s" % year),
                ("index", "$index")
            ], renderers=[r])
            figure_object[0].add_tools(hover)

        figure_object[0].y_range.start = 0
        figure_object[0].y_range.end = 1.0
        figure_object[0].xgrid.grid_line_color = None
        figure_object[0].axis.minor_tick_line_color = None
        figure_object[0].outline_line_color = None
        figure_object[0].legend.location = "top_left"
        figure_object[0].legend.orientation = "horizontal"

        return figure_object[0]


class BokehBarPlot(BokehStyledVisElement):
    """
    Visualises categorical count data (i.e. MeSH terms and number of articles they appear in)
    """
    # TODO: MED, query_parameters can have a default of None. Need to find a way to sort this out without violating the order of parameters
    def __init__(self, a_query, query_parameters, categories_variable, count_variable, is_vertical = False, **context_args):
        """
        A horizontal bar plot

        :param a_query:
        :param categories_variable:
        :param count_variable:
        """
        super().__init__(**context_args)
        self.query_parameters = query_parameters
        self.query_object = a_query
        self.categories_variable = categories_variable
        self.count_variable = count_variable
        self._is_vertical = is_vertical

        # The query must be a pseudo data frame
        #if type(self.query_object) is not neoads.CompositeArrayObjectDataFrame:
        #    raise exception.DataStructureError(f"BokehStyledBarPlot received query object {type(self.query_object)}, expected compositeArrayObjectDataFrame")

    def _before_render(self):
        source = bokeh.models.ColumnDataSource.from_df(self.query_object.execute(params=self.query_parameters))
        descriptors = source[self.categories_variable]

        figure_params = dict(filter(lambda x:x[0] in ["plot_width", "plot_height", "x_axis_label", "y_axis_label", "title", "toolbar_location", "tools"],self.context.items()))

        if self._is_vertical:
            figure_object = bokeh.plotting.figure(x_range = descriptors, **figure_params)
        else:
            figure_object = bokeh.plotting.figure(y_range = descriptors, **figure_params)

        return figure_object, source

    def _main_render(self, figure_object):
        if self._is_vertical:
            figure_object[0].vbar(x=self.categories_variable, top=self.count_variable, source=figure_object[1], width=1.0)
        else:
            figure_object[0].hbar(y=self.categories_variable, right=self.count_variable, source=figure_object[1], height=1.0)

        return figure_object[0]


class NetworkxPyGraphVizImagePlot(MarkdownVisElement):
    """

    """
    def __init__(self, network_query, query_parameters, u_id, v_id, u_label=None, v_label=None, uv_weight=None, viz_parameters = None, **kwargs):
        self._network_query = network_query
        self._network_query_parameters = query_parameters
        self._viz_parameters = viz_parameters
        self._u_id = u_id
        self._v_id = v_id
        self._u_label = u_label
        self._v_label = v_label
        self._uv_weight = uv_weight
        self._image_url = f"{uuid.uuid4()}.png"
        super().__init__("![alt-text]({image_url})", image_url=self._image_url, **kwargs)

    def _before_render(self):
        query_data = self._network_query.execute(self._network_query_parameters)
        G = networkx.Graph()
        for an_edge in range(0,len(query_data)):
            G.add_node(query_data.iloc[an_edge][self._u_id], label=query_data.iloc[an_edge][self._u_label])
            G.add_node(query_data.iloc[an_edge][self._v_id], label=query_data.iloc[an_edge][self._v_label])
            G.add_edge(query_data.iloc[an_edge][self._u_id], query_data.iloc[an_edge][self._v_id], weight = query_data.iloc[an_edge][self._uv_weight])

        G = networkx.minimum_spanning_tree(G)

        G.graph["graph"]={"overlap":"yes", "splines":"no"}
        G.graph["node"]={"fontsize":"10"}
        return G

    def _main_render(self, init_object):
        A = networkx.drawing.nx_agraph.to_agraph(init_object)
        A.draw(self._image_url, prog="neato")
        return super()._main_render(init_object)


class SimpleAssociativeMappingDisplay(StringTemplateVisElement):
    """
    Renders a key-value type of associative mapping. It requires certain styles (mappingvis,keyvalue,key,value,mappingvistitle) to already have been defined.
    """
    def __init__(self, a_dict, a_title=""):
        super().__init__("<div class=""mappingvis"">\n\t<div class=""mappingvistitle"">\n\t\t{{a_title}}\n\t</div>\n\t{% for item in items.items() %}\n\t<div class=""keyvalue"">\n\t\t<div class=""key"">{{item[0]}}</div>\n\t\t<div class=""value"">{{item[1]}}</div>\n\t</div>{% endfor %}\n</div>", items=a_dict, a_title=a_title)

