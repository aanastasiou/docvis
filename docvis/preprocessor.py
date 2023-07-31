"""
``fun-dsl`` Preprocessor
========================


:author: Athanasios Anastasiou
:date: Jul 2023
"""

import lark
import re
import collections
import uuid

from .exceptions import VariableNotFoundError, FunDSLSyntaxError

# Holds information about a fun-dsl evaluated segment
EvaluatedSegment = collections.namedtuple("EvaluatedSegment",["result", "original_string", "substituted_string"])


class AstToValue(lark.Transformer):
    """
    Transforms the tree of tokens at the output of the parser to a computable value.

    :param context: A dictionary that maps variable names to variables that are accessible 
                    for variable substitution
    :type context: dict
    """

    def __init__(self, context=None):
        self._context = context

    def function_call(self, cap):
        return {"function_name":cap[0],
                "function_parameters":cap[1]}

    def keyword_params(self, cap):
        return dict([u for u in cap])

    def keyword_param(self, cap):
        return (cap[0], cap[1])

    def keyword_key(self, cap):
        return cap[0].value

    def keyword_value(self, cap):
        return cap[0]

    def dict_keyvalue(self, cap):
        return (cap[0], cap[1])

    def value_idf_accessor(self, cap):
        """
        Return the value of an object at any depth
        """
        # The first item is the recalled data structure, the rest of it are the fields
        current_value = cap[0]
        for a_field in cap[1:]:
            current_value = getattr(current_value, a_field)
        return current_value

    def value_idf_field_accessor(self, cap):
        """
        Return the value of a dictionary at any depth
        """
        # TODO: HIGH, add expcetions for the obvious errors that can emerge here
        # The first item is the recalled data structure, the rest of it are the fields
        current_value = cap[0]
        for a_field in cap[1:]:
            current_value = current_value.get(a_field)
        return current_value

    def dict_key_accessor(self, cap):
        return cap[0]

    def value_dict(self, cap):
        return dict(cap)

    def value_tuple(self, cap):
        return tuple(cap)

    def value_list(self, cap):
        return cap 

    def list_atom(self, cap):
        return cap[0]

    def tuple_atom(self, cap):
        return cap[0]

    def VALUE_STR(self, s):
        return s.value[1:-1]

    def VALUE_INT(self, n):
        return int(n.value)

    def VALUE_FLOAT(self, n):
        return float(n.value)

    def VALUE_IDF(self, n):
        """
        Return the value of an identified that should exist in the context.
        """
        if n.value in self._context:
            return self._context[n.value]
        else:
            raise VariableNotFoundError(f"Variable {n.value} not found in context")

    def IDF(self, n):
        # An identifier is returned verbatim
        return n

    # Drop the delimiting tokens as they do not participate in transforming a value to 
    # its computable form.
    def COMMA(self, item):
        return lark.Discard

    def DBL_QUOTE(self, item):
        return lark.Discard

    def SGL_QUOTE(self, item):
        return lark.Discard

    def SB_OPEN(self, item):
        return lark.Discard

    def SB_CLOSE(self, item):
        return lark.Discard

    def RB_OPEN(self, item):
        return lark.Discard

    def RB_CLOSE(self, item):
        return lark.Discard

    def CB_OPEN(self, item):
        return lark.Discard

    def CB_CLOSE(self, item):
        return lark.Discard

    def COLON(self, item):
        return lark.Discard

    def MARK_START(self, item):
        return lark.Discard

    def MARK_END(self, item):
        return lark.Discard

    def DOT(self, item):
        return lark.Discard


class TemplatePreprocessor:
    """
    Preprocesses a string template and substitutes specific string patterns

    :param function_table: A mapping from the name of a function to a callable that implements the call.
    :type function_table: dict
    :param context: A mapping from the name of a variable to its value.
    :type context: dict
    :param mark_start: The opening paragraph marker (e.g. ``%\$``)

                       .. note::

                          The start and end marker are embedded in a regular expression to track and 
                          extract the fun-dsl paragraphs. Therefore, if ``mark_start, mark_end``
                          contains special (for regexp) characters, such as ``$``, these have to be 
                          escaped.
    :type mark_start: str
    :param mark_end: The closing paragraph marker (e.g. ``\$%``)
    :type mark_end: str
    """

    def __init__(self, function_table, context, mark_start, mark_end):
        self._function_table = function_table
        self._context = context
        self._mark_start = mark_start
        self._mark_end = mark_end
        self._fun_call_parser = lark.Lark(self.__function_call_grammar__(), 
                                          propagate_positions=True, 
                                          start="function_call")
        self._ast_transformer = AstToValue(self._context)

    @staticmethod
    def __function_call_grammar__():
        """
        Set up the Lark grammar that is used to recognise a "function call".
        """
        return r"""
        DBL_QUOTE: "\""
        SGL_QUOTE: "'"
        SB_OPEN:"["
        SB_CLOSE:"]"
        RB_OPEN:"("
        RB_CLOSE:")"
        CB_OPEN:"{"
        CB_CLOSE:"}"
        DOT:"."
        COMMA : ","
        COLON: ":"

        VALUE_INT: /-?[0-9]+/
        VALUE_FLOAT: /-?[0-9]*\.[0-9]+/
        VALUE_STR: (DBL_QUOTE /.*?/ DBL_QUOTE ) | (SGL_QUOTE /.*?/ SGL_QUOTE)
        VALUE_IDF: /[a-zA-Z_][a-zA-Z0-9_]*/
        value_idf_field_accessor: VALUE_IDF dict_key_accessor+
        value_idf_accessor:VALUE_IDF (DOT IDF)+
        IDF: /[a-zA-Z_][a-zA-Z0-9_]*/

        list_atom: VALUE_IDF | VALUE_INT | VALUE_FLOAT | VALUE_STR | value_list | value_tuple | value_dict | value_idf_field_accessor | value_idf_accessor
        value_list: SB_OPEN (list_atom | list_atom COMMA)* SB_CLOSE

        tuple_atom: VALUE_IDF | VALUE_INT | VALUE_FLOAT | VALUE_STR | value_tuple | value_idf_field_accessor | value_idf_accessor 
        value_tuple: RB_OPEN (tuple_atom|tuple_atom COMMA)* RB_CLOSE


        dict_keyvalue: (VALUE_INT | VALUE_FLOAT | VALUE_STR | value_tuple) COLON (VALUE_IDF | VALUE_INT | VALUE_FLOAT | VALUE_STR | value_list | value_tuple | value_dict | value_idf_field_accessor | value_idf_accessor)
        dict_key_accessor:SB_OPEN (VALUE_INT | VALUE_FLOAT | VALUE_STR | value_tuple) SB_CLOSE
        value_dict: CB_OPEN (dict_keyvalue | dict_keyvalue COMMA)* CB_CLOSE

        keyword_key:IDF
        keyword_value:VALUE_IDF | VALUE_INT | VALUE_FLOAT | VALUE_STR | value_tuple | value_list | value_dict | value_idf_field_accessor | value_idf_accessor
        keyword_param: keyword_key "=" keyword_value 
        keyword_params: (keyword_param | keyword_param COMMA)*
        function_call:IDF RB_OPEN keyword_params RB_CLOSE
        
        %import common.ESCAPED_STRING
        %import common.WS
        %ignore WS
        """
    
    def __call__(self, a_string): 
        """
        Parse a string and evaluate the function_calls safely.
        """
        processed_string = ""
        evaluation_results = []
        errors = []    

        delimited_segments = re.compile("(?s)" + self._mark_start + "(.*?)" + self._mark_end).split(a_string)

        for seg_idx, a_segment in enumerate(delimited_segments):
            # The splitting results in a string where the odd entries contain the 
            # function calls.
            if seg_idx % 2 == 0:
                processed_string += a_segment
            else:
                try:
                   # Parse the function call
                   token_stream = self._fun_call_parser.parse(a_segment)
                   # Turn the parsed segment into a computable data structure
                   data_value = self._ast_transformer.transform(token_stream)
                   # Evaluate the string
                   eval_result = self._function_table[data_value["function_name"]](**data_value["function_parameters"])
                   # Get a tag to substitute
                   subst_tag = f"element_{str(uuid.uuid4()).replace('-', '')}"
                   evaluation_results.append(EvaluatedSegment(result = eval_result,
                                                              original_string = a_segment,
                                                              substituted_string = subst_tag))
                   # If everything has gone well, append the tag that will render this 
                   # segment.
                   processed_string += f"{{{{{subst_tag}}}}}"
                # TODO: HIGH, Known errors should be returned as string messages, unknown as their original exception.    
                except lark.visitors.VisitError as e:
                    # See https://lark-parser.readthedocs.io/en/latest/recipes.html#unwinding-visiterror-after-a-transformer-visitor-exception
                    errors.append((e.orig_exc, a_segment))
                except lark.exceptions.UnexpectedCharacters as e:
                    # TODO: HIGH, Make this syntax error more specific
                    errors.append((FunDSLSyntaxError("Syntax Error"), a_segment))
                except Exception as e:
                    # If evaluation run into problems, record the segment where the 
                    # problem occured in as well as the error
                    errors.append((e, a_segment))
    
        return processed_string, evaluation_results, errors


