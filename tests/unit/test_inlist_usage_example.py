"""Usage examples for InListParameter"""
import pytest
from databricks.sql.parameters import InListParameter
from databricks.sql.utils import ParamEscaper


class TestInListUsageExamples:
    """Real-world usage examples for InListParameter"""

    def test_basic_in_clause_example(self):
        """Example: Using InListParameter for IN clause"""
        escaper = ParamEscaper()

        ref_ids = InListParameter(['a', 'b'])
        result = escaper.escape_item(ref_ids)

        assert result == "('a','b')"

    def test_sql_in_clause_with_dict_params(self):
        """Example: Using InListParameter in parameter dictionary for SQL query"""
        escaper = ParamEscaper()

        sql_template = "SELECT * FROM foo WHERE bar IN %(ref_ids)s"
        params = {
            "ref_ids": InListParameter(['a', 'b'])
        }

        escaped_params = escaper.escape_args(params)

        assert escaped_params['ref_ids'] == "('a','b')"

        rendered_sql = sql_template % escaped_params
        assert rendered_sql == "SELECT * FROM foo WHERE bar IN ('a','b')"

    def test_numeric_in_clause(self):
        """Example: Using InListParameter with numeric IDs"""
        escaper = ParamEscaper()

        id_list = InListParameter([1, 2, 3, 4, 5])
        result = escaper.escape_item(id_list)

        assert result == "(1,2,3,4,5)"

    def test_large_in_clause(self):
        """Example: Using InListParameter with many values"""
        escaper = ParamEscaper()

        large_id_list = InListParameter(list(range(1, 101)))
        result = escaper.escape_item(large_id_list)

        assert len(result.split(',')) == 100
        assert result.startswith('(')
        assert result.endswith(')')

    def test_mixed_types_in_clause(self):
        """Example: Using InListParameter with mixed data types"""
        escaper = ParamEscaper()

        mixed_list = InListParameter([1, 2, 3, 4])
        result = escaper.escape_item(mixed_list)

        assert result == "(1,2,3,4)"

    def test_single_value_in_clause(self):
        """Example: Using InListParameter with single value"""
        escaper = ParamEscaper()

        single_value = InListParameter([42])
        result = escaper.escape_item(single_value)

        assert result == "(42)"

    def test_string_values_with_spaces(self):
        """Example: Using InListParameter with string values containing spaces"""
        escaper = ParamEscaper()

        string_list = InListParameter(['John Smith', 'Jane Doe', 'Bob Johnson'])
        result = escaper.escape_item(string_list)

        assert result == "('John Smith','Jane Doe','Bob Johnson')"

    def test_backward_compatibility_note(self):
        """Note: How the old way still works"""
        escaper = ParamEscaper()
        from databricks.sql.parameters import ArrayParameter

        array_param = ArrayParameter(['a', 'b', 'c'])
        array_result = escaper.escape_item(array_param)
        assert array_result == "ARRAY('a','b','c')"

        inlist_param = InListParameter(['a', 'b', 'c'])
        inlist_result = escaper.escape_item(inlist_param)
        assert inlist_result == "('a','b','c')"
