"""Tests for InListParameter class"""
import pytest
from databricks.sql.parameters import InListParameter, ArrayParameter
from databricks.sql.utils import ParamEscaper


class TestInListParameterConstruction:
    """Test InListParameter construction and basic properties"""

    def test_inlist_with_strings(self):
        """Test creating InListParameter with string values"""
        param = InListParameter(['a', 'b', 'c'])
        assert param.name is None
        assert len(param.value) == 3

    def test_inlist_with_integers(self):
        """Test creating InListParameter with integer values"""
        param = InListParameter([1, 2, 3])
        assert param.name is None
        assert len(param.value) == 3

    def test_inlist_with_mixed_types(self):
        """Test creating InListParameter with mixed types"""
        param = InListParameter([1, 'a', 2.5])
        assert param.name is None
        assert len(param.value) == 3

    def test_inlist_with_name(self):
        """Test creating InListParameter with a named parameter"""
        param = InListParameter([1, 2, 3], name='ids')
        assert param.name == 'ids'
        assert len(param.value) == 3

    def test_inlist_empty_list(self):
        """Test creating InListParameter with empty list"""
        param = InListParameter([])
        assert len(param.value) == 0


class TestInListParameterNativeMode:
    """Test InListParameter in native mode (as_tspark_param)"""

    def test_inlist_as_tspark_param_positional(self):
        """Test as_tspark_param for positional parameters"""
        param = InListParameter([1, 2, 3])
        tsp = param.as_tspark_param(named=False)

        assert tsp.type == 'ARRAY'
        assert tsp.ordinal is True
        assert tsp.name is None
        assert len(tsp.arguments) == 3

    def test_inlist_as_tspark_param_named(self):
        """Test as_tspark_param for named parameters"""
        param = InListParameter([1, 2, 3], name='ids')
        tsp = param.as_tspark_param(named=True)

        assert tsp.type == 'ARRAY'
        assert tsp.ordinal is False
        assert tsp.name == 'ids'
        assert len(tsp.arguments) == 3

    def test_inlist_tspark_value_arg(self):
        """Test _tspark_value_arg method"""
        param = InListParameter([1, 2, 3])
        arg = param._tspark_value_arg()

        assert arg.type == 'ARRAY'
        assert len(arg.arguments) == 3


class TestInListParameterInlineMode:
    """Test InListParameter inline escaping"""

    def test_inlist_escape_strings(self):
        """Test escaping InListParameter with strings"""
        escaper = ParamEscaper()
        param = InListParameter(['a', 'b', 'c'])
        result = escaper.escape_item(param)

        assert result == "('a','b','c')"

    def test_inlist_escape_integers(self):
        """Test escaping InListParameter with integers"""
        escaper = ParamEscaper()
        param = InListParameter([1, 2, 3])
        result = escaper.escape_item(param)

        assert result == "(1,2,3)"

    def test_inlist_escape_floats(self):
        """Test escaping InListParameter with floats"""
        escaper = ParamEscaper()
        param = InListParameter([1.1, 2.2, 3.3])
        result = escaper.escape_item(param)

        assert result == "(1.1,2.2,3.3)"

    def test_inlist_escape_mixed(self):
        """Test escaping InListParameter with mixed types"""
        escaper = ParamEscaper()
        param = InListParameter([1, 'a', 2.5])
        result = escaper.escape_item(param)

        assert result == "(1,'a',2.5)"

    def test_inlist_escape_single_value(self):
        """Test escaping InListParameter with single value"""
        escaper = ParamEscaper()
        param = InListParameter(['a'])
        result = escaper.escape_item(param)

        assert result == "('a')"

    def test_inlist_escape_special_chars_in_strings(self):
        """Test escaping InListParameter with strings containing special chars"""
        escaper = ParamEscaper()
        param = InListParameter(["it's", 'quote"'])
        result = escaper.escape_item(param)

        assert "it\\'s" in result
        assert 'quote"' in result

    def test_inlist_escape_method_exists(self):
        """Test that escape_inlist method exists"""
        escaper = ParamEscaper()
        assert hasattr(escaper, 'escape_inlist')

        result = escaper.escape_inlist([1, 2, 3])
        assert result == "(1,2,3)"


class TestInListVsArrayParameter:
    """Test differences between InListParameter and ArrayParameter"""

    def test_inlist_renders_as_tuple_inline(self):
        """Test that InListParameter renders as (val1,val2,...) in inline mode"""
        escaper = ParamEscaper()
        param = InListParameter(['a', 'b', 'c'])
        result = escaper.escape_item(param)

        assert result == "('a','b','c')"
        assert not result.startswith('ARRAY')

    def test_array_renders_as_array_inline(self):
        """Test that ArrayParameter still renders as ARRAY(...) in inline mode"""
        escaper = ParamEscaper()
        param = ArrayParameter(['a', 'b', 'c'])
        result = escaper.escape_item(param)

        assert result == "ARRAY('a','b','c')"
        assert result.startswith('ARRAY')

    def test_inlist_vs_array_comparison(self):
        """Test side-by-side comparison of InListParameter vs ArrayParameter"""
        escaper = ParamEscaper()

        inlist_result = escaper.escape_item(InListParameter([1, 2, 3]))
        array_result = escaper.escape_item(ArrayParameter([1, 2, 3]))

        assert inlist_result == "(1,2,3)"
        assert array_result == "ARRAY(1,2,3)"
        assert inlist_result != array_result

    def test_both_use_array_cast_expr_native_mode(self):
        """Test that both use ARRAY type in native mode"""
        inlist_param = InListParameter([1, 2, 3])
        array_param = ArrayParameter([1, 2, 3])

        inlist_tsp = inlist_param.as_tspark_param(named=False)
        array_tsp = array_param.as_tspark_param(named=False)

        assert inlist_tsp.type == 'ARRAY'
        assert array_tsp.type == 'ARRAY'


class TestInListParameterWithParameterDict:
    """Test InListParameter in parameter dictionaries"""

    def test_inlist_in_param_dict_escape(self):
        """Test escaping a parameter dict containing InListParameter"""
        escaper = ParamEscaper()
        params = {
            'ids': InListParameter([1, 2, 3]),
            'name': 'test'
        }
        result = escaper.escape_args(params)

        assert result['ids'] == "(1,2,3)"
        assert result['name'] == "'test'"

    def test_mixed_array_and_inlist_in_dict(self):
        """Test escaping a dict with both ArrayParameter and InListParameter"""
        escaper = ParamEscaper()
        params = {
            'ids': InListParameter([1, 2, 3]),
            'array_col': ArrayParameter(['a', 'b', 'c'])
        }
        result = escaper.escape_args(params)

        assert result['ids'] == "(1,2,3)"
        assert result['array_col'] == "ARRAY('a','b','c')"


class TestInListParameterEquality:
    """Test InListParameter equality"""

    def test_inlist_equality(self):
        """Test InListParameter equality"""
        param1 = InListParameter([1, 2, 3])
        param2 = InListParameter([1, 2, 3])

        assert param1 == param2

    def test_inlist_with_name_equality(self):
        """Test InListParameter with name equality"""
        param1 = InListParameter([1, 2, 3], name='ids')
        param2 = InListParameter([1, 2, 3], name='ids')

        assert param1 == param2
