"""

:author: Athanasios Anastasiou
:date: Jul 2023
"""

import lark
import re

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
        # The first item is the recalled data structure, the rest of it are the fields
        current_value = cap[0]
        for a_field in cap[1:]:
            current_value = getattr(current_value, a_field)
        return current_value

    def value_idf_field_accessor(self, cap):
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
        if n.value in self._context:
            return self._context[n.value]
        else:
            raise Exception(f"Variable {n.value} not found in context")

    def IDF(self, n):
        return n

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


    def __function_call_grammar__(self):
        """
        Sets up the grammar that is used to recognise a "function call".
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
        Parses a string and evaluates the function_calls safely.
        """
        to_res = []
        errors = []    
            
        for seg_idx, a_segment in enumerate(re.compile(mark_start + " *(.*?) *" + mark_end).split(a_string)):
            # The splitting results in a string where the odd entries contain the 
            # function calls.
            if seg_idx % 2 != 0:
                # Parse the function call
                token_stream = self._fun_call_parser.parse(a_segment)
                # Turn the parsd segment into a computable data structure
                data_value = self._ast_transformer.transform(token_stream)
                try:
                   eval_result = self._function_table[data_value["function_name"]](**data_value["function_parameters"])
                   to_res += eval_result
                except Exception as e:
                    errors.append((e, a_segment))
    
        return to_res, errors


