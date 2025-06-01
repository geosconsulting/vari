import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from expansion_prova import gen_listof_int, square_list

def test_gen_listof_int_type():
    """
    Verifies that the generated list is of type list.
    """
    result = gen_listof_int(1, 10, 1)
    assert isinstance(result, list)

def test_gen_listof_int_values():
    """
    Verifies that the generated list contains expected values.
    """
    result = gen_listof_int(1, 11, 1)
    assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]