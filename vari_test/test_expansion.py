from expansion_prova import gen_listof_int, square_list

def test_gen_listof_int():
    """
    Verifies that the generated list is of type list.
    """
    assert gen_listof_int(1, 10, 1) == [1,2] #type