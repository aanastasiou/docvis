"""
RepVis

Elements that produce an intermediate format (i.e. Markdown), of complex
visualisation elements which are then all brought together in one top level 
element and can also be saved to disk as standalone documents.

Since markdown will not be rendered if inside block level HTML, the elements 
that produce markdown should be nested within the elements that produce HTML (If any)

:author: Athanasios Anastasiou
:date: Mar 2023
"""

#import exception
import collections
import jinja2
import os
import shutil
import json

# TODO: MED, Elements also need a way of determining any additional dependencies they might have
# e.g. Javascript scripts that much be included before the component can be used succesfully.

class VisElement:
    """
    Transform data to output.

    Note: Usually, the output is a simple string. **BUT** there might be other forms of output that can be returned
    If the output is a simple string then return the string, if the output is more complex then return a dict

    Notes on the construction and use of VisElement:
        * A VisElement renders to an intermediate form which is then used by a final rendering element to compose the final document
        * A VisElement's fundamental parameters (what it is composed of) should be given at construction time (for example, which parameter is to be visualised)
        * A VisElement's visual style can be determined at runtime via args, kwargs (for example, plot a histogram using a specific colour)
    """
   
    def __init__(self, **context_args):
        """
        Initialises a VisElement with all the information that is required to generate the final visualisation.

        :param context_args: key value combinations of all the necessary context arguments that are required to render the component
        """
        self.context = context_args

    def _descend_context(self, a_context):
        """
        Recursively calls rendering of the context variables.
        :param a_context:
        :return:
        """
        # TODO: MED, Cache the results to avoid re-evaluation in the case a component is re-used within the same page.
        if issubclass(type(a_context), (dict, collections.OrderedDict)):
            visual_reps = collections.OrderedDict()
            a_context_items = a_context.items()
            for an_item in a_context_items:
                rendered_value = an_item[1]
                if issubclass(type(rendered_value), VisElement):
                    rendered_value = an_item[1].render()
                if issubclass(type(rendered_value),(list,dict, collections.OrderedDict)):
                    rendered_value = self._descend_context(an_item[1])
                visual_reps[an_item[0]] = rendered_value
            return visual_reps
        else:
            visual_reps = []
            for an_item in a_context:
                rendered_value = an_item
                if issubclass(type(an_item), VisElement):
                    rendered_value = an_item.render()
                if issubclass(type(an_item),(list,dict, collections.OrderedDict)):
                    rendered_value = self._descend_context(an_item)
                visual_reps.append(rendered_value)
            return visual_reps

    def _before_render(self):
        """
        Sets up the element for rendering.
        :return: An object with any temporary variables that might be required during rendering. This is then passed to
                 _main_render()
        """
        return None

    def _main_render(self, init_object):
        """
        Processes the data context that is passed at __init__ .
        The visual output must be a string

        :param init_object: The object that was returned by _before_render()
        :return: A string
        """
        visual_reps = self._descend_context(self.context)
        return visual_reps

    def _after_render(self, init_object, visual_reps):
        """
        Finalises the rendered object and returns it
        :param init_object:
        :param main_object:
        :return:
        """
        return visual_reps

    def _clear(self):
        """
        Clears any resources that the element may have used during render time (e.g. temporary files).
        :return:
        """
        pass

    def render(self):
        """
        Kickstarts the whole rendering process and returns the string representation of the data
        :param args:
        :param kwargs:
        :return:
        """
        # Clear any temporary resources that may have been created
        self._clear()
        # Initialise the object
        init_object = self._before_render()
        # Produce the visual representations
        visual_reps = self._main_render(init_object)
        # Render the visual representations to a concrete form
        return self._after_render(init_object, visual_reps)


class StringTemplateVisElement(VisElement):
    """
    Render a Jinja2 Template defined by a string.
    """
    def __init__(self, template_string, **context_args):
        """
        Automates the rendering of a very simple Jinja2 Template.

        :param template_string: A Jinja2 template string
        :param context_args: Any variables that are used by the template
        """
        super().__init__(**context_args)
        self._template_string = template_string

    def _after_render(self, init_object, visual_reps):
        """
        Finalises the rendering of this element down to its final form.

        :param init_object:
        :param visual_reps:
        :return:
        """
        return jinja2.Template(self._template_string).render(**visual_reps)


class FileTemplateVisElement(StringTemplateVisElement):
    """
    Renders a Jinja2 Template defined by a file.
    """
    def __init__(self, template_file, **context_args):
        with open(template_file, "rt", encoding = "utf-8") as fd:
            super().__init__(fd.read(), **context_args)


class RenderToFileMixin(VisElement):
    """
    Handles saving the rendered output of an element on disk

    NOTE: This is a mixin. Its job is to render the document and then take the rendered form and store it in a file.
    Therefore, it is entirely agnostic about what it is mixed in with.
    """
    def __init__(self, to_file, additional_files = None):
        self._rendertofilemixin_additional_files = additional_files
        self._rendertofilemixin_to_file = to_file
        self._rendertofilemixin_destination_dir = None

    def render(self):
        # Check if the destination directory exists and create it if not
        if self._rendertofilemixin_destination_dir is None:
            self._rendertofilemixin_destination_dir, _ = os.path.split(self._rendertofilemixin_to_file)

        if not os.path.exists(self._rendertofilemixin_destination_dir) and not self._rendertofilemixin_destination_dir=="":
            os.makedirs(self._rendertofilemixin_destination_dir)

        # Render the document
        if not self._rendertofilemixin_destination_dir == "":
            current_dir = os.getcwd()
            os.chdir(self._rendertofilemixin_destination_dir)

        document_content = super().render()

        if not self._rendertofilemixin_destination_dir == "":
            os.chdir(current_dir)

    # Save it to the file
        with open(self._rendertofilemixin_to_file, "w", encoding="utf-8") as fd:
            fd.write(document_content)
        # Copy across any additional files that may be required for this file to be depicted properly
        # (e.g. scripts / other)
        if self._rendertofilemixin_additional_files:
            for a_file in self._rendertofilemixin_additional_files:
                source_dir, source_file = os.path.split(a_file)
                destination_file_name = f"{self._rendertofilemixin_destination_dir}/{source_file}"
                if not os.path.exists(destination_file_name):
                    shutil.copy(a_file, destination_file_name)
        return document_content


class VisElementStyle(dict):
    """
    Determines common styles across different visual components.

    A component that is used to structure a report might make use of different technologies and toolkits. These
    components, although they might have similar capabilities, do not necessarily use the same colours, fonts,
    line thicknesses, text alignments and so on.

    A VisElementStyle's purpose is similar to a CSS class. It captures a set of properties that can be used to
    enforce a consistent style across document components.

    A VisElementStyle is basically a python dictionary with additional functionality to save and load that dictionary
    in the form of a JSON object.
    """
    def save(self, filename):
        with open(filename, "wt", encoding = "utf-8") as fd:
            json.dump(self, fd)

    def load(self, filename):
        self.clear()
        with open(filename, "rt", encoding = "utf-8") as fd:
            self.update(json.load(fd))

    def get_style_attributes(self, style_attributes):
        """
        Returns a subset of style attributes as a dictionary.

        :param style_attributes: A list of attribute names to extract from the VisElementStyle
        :return: dict
        """
        style_subset = dict.fromkeys(style_attributes)
        for an_attribute in style_attributes:
            if an_attribute in self:
                style_subset[an_attribute] = self[an_attribute]
            else:
                del style_subset[an_attribute]
        #style_subset = dict(zip(style_attributes, map(lambda x: self[x] if x in self else None, style_attributes)))
        return style_subset


class StyledVisElement(VisElement):
    """
    A VisElement with common style parameters.
    """
    def __init__(self, style=None, **context_args):
        super().__init__(**context_args)
        if style is not None:
            self._style = style
        else:
            self._style = VisElementStyle()

# TODO: LOW, Now something can derive from this and represent one report with all of its data
class HTMLTemplatedDocument(RenderToFileMixin, FileTemplateVisElement):
    """
    Represents a templated HTML document.

    The thinking behind this was to have an HTML template that includes the preamble and the closing of the document
    with a small number of context variables controlling the rendering of the content to the HTML document.
    """
    def __init__(self, body_variable, body_element, html_template_file, output_file, additional_files=None, **context_args):
        # Initialise the RenderToFile mixin
        RenderToFileMixin.__init__(self, output_file, additional_files)
        # Initialise the templated vis element
        FileTemplateVisElement.__init__(self, html_template_file, **context_args)
        # Inject the body variable explicitly to ensure that it will be there during rendering
        self.context[body_variable] = body_element


class SimpleAssociativeMappingDisplay(StringTemplateVisElement):
    """
    Renders a key-value type of associative mapping. It requires certain styles (mappingvis,keyvalue,key,value,mappingvistitle) to already have been defined.
    """
    def __init__(self, a_dict, a_title=""):
        super().__init__("<div class=""mappingvis"">\n\t<div class=""mappingvistitle"">\n\t\t{{a_title}}\n\t</div>\n\t{% for item in items.items() %}\n\t<div class=""keyvalue"">\n\t\t<div class=""key"">{{item[0]}}</div>\n\t\t<div class=""value"">{{item[1]}}</div>\n\t</div>{% endfor %}\n</div>", items=a_dict, a_title=a_title)


