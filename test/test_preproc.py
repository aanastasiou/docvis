from docvis.preprocessor import TemplatePreprocessor, AstToValue
import lark
import pytest

# TODO: MID, Add test cases for field and attribute accessor cases
@pytest.mark.parametrize("specific_rule, parsed_str, result",
                         [
                             ("list_atom", "10", 10),
                             ("list_atom", "-10", -10),
                             ("list_atom", "3.14", 3.14),
                             ("list_atom", "-3.14", -3.14),
                             ("list_atom", "\"alpha\"", "alpha"),
                             ("list_atom", "'alpha'", "alpha"),
                             ("list_atom", "q", 1),
                             ("list_atom", "[1,2,3]", [1, 2, 3]),
                             ("list_atom", "(1,2,3)", (1, 2, 3)),
                             ("dict_keyvalue", "1:q",(1, 1)),
                             ("dict_keyvalue", "1:2",(1, 2)),
                             ("dict_keyvalue", "1:3.14",(1, 3.14)),
                             ("dict_keyvalue", "1:\"one\"",(1, "one")),
                             ("dict_keyvalue", "1:[1,2,3]",(1, [1, 2, 3])),
                             ("dict_keyvalue", "1:(1,2,3)",(1, (1, 2, 3))),
                             ("dict_keyvalue", "1:{1:2,3:4}",(1, {1:2,3:4})),
                             ("dict_keyvalue", "1:{1:q}",(1, {1:1})),
                             ("list_atom", "{1:2,3:4}",{1:2,3:4}),
                             ("keyword_param", "alpha=q",("alpha",1)),
                             ("keyword_param", "alpha=1",("alpha",1)),
                             ("keyword_param", "alpha=3.14",("alpha",3.14)),
                             ("keyword_param", "alpha=\"alpha\"",("alpha","alpha")),
                             ("keyword_param", "alpha=(1,2,3)",("alpha",(1,2,3))),
                             ("keyword_param", "alpha=[1,2,3]",("alpha",[1,2,3])),
                             ("keyword_param", "alpha={1:2,3:4}",("alpha",{1:2,3:4})),
                             ("function_call", "blah(alpha=1,beta=2)",{"function_name":"blah",
                                                                       "function_parameters":{"alpha":1, "beta":2}}),

                         ])
def test_preprocessor_rule_success(specific_rule, parsed_str, result):
    """
    Tests parsing rules based on their return results
    """
    assert AstToValue({"q":1}).transform(lark.Lark(TemplatePreprocessor.__function_call_grammar__(),
                                       start=specific_rule).parse(parsed_str)) == result


@pytest.mark.parametrize("specific_rule, parsed_str, expected_exception",
                         [
                             ("tuple_atom", "[1,2,3]", lark.exceptions.UnexpectedCharacters),
                         ])
def test_preprocessor_rule_fail(specific_rule, parsed_str, expected_exception):
    """
    Tests error cases for specific rules
    """
    with pytest.raises(expected_exception):
        AstToValue({"q":1}).transform(lark.Lark(TemplatePreprocessor.__function_call_grammar__(),
                                       start=specific_rule).parse(parsed_str))


