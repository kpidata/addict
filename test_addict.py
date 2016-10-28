import json
import copy
import pickle
import pytest

from addict import Dict

TEST_VAL = [1, 2, 3]
TEST_DICT = {'a': {'b': {'c': TEST_VAL}}}
TEST_DICT_STR = str(TEST_DICT)


def test_set_one_level_item():
    some_dict = {'a': TEST_VAL}
    prop = Dict()
    prop['a'] = TEST_VAL
    assert prop == some_dict


def test_set_two_level_items():
    some_dict = {'a': {'b': TEST_VAL}}
    prop = Dict()
    prop['a']['b'] = TEST_VAL
    assert prop == some_dict


def test_set_three_level_items():
    prop = Dict()
    prop['a']['b']['c'] = TEST_VAL
    assert prop == TEST_DICT


def test_set_one_level_property():
    prop = Dict()
    prop.a = TEST_VAL
    assert prop == {'a': TEST_VAL}


def test_set_two_level_properties():
    prop = Dict()
    prop.a.b = TEST_VAL
    assert prop == {'a': {'b': TEST_VAL}}


def test_set_three_level_properties():
    prop = Dict()
    prop.a.b.c = TEST_VAL
    assert prop == TEST_DICT


def test_init_with_dict():
    assert TEST_DICT == Dict(TEST_DICT)


def test_init_with_kws():
    prop = Dict(a=2, b={'a': 2}, c=[{'a': 2}])
    assert prop == {'a': 2, 'b': {'a': 2}, 'c': [{'a': 2}]}


def test_init_with_tuples():
    prop = Dict((0, 1), (1, 2), (2, 3))
    assert prop == {0: 1, 1: 2, 2: 3}


def test_init_with_list():
    prop = Dict([(0, 1), (1, 2), (2, 3)])
    assert prop == {0: 1, 1: 2, 2: 3}


def test_init_with_generator():
    prop = Dict(((i, i + 1) for i in range(3)))
    assert prop == {0: 1, 1: 2, 2: 3}


def test_init_with_tuples_and_empty_list():
    prop = Dict((0, 1), [], (2, 3))
    assert prop == {0: 1, 2: 3}


def test_init_raises():
    def init():
        Dict(5)

    def init2():
        Dict('a')
    pytest.raises(TypeError, init)
    pytest.raises(ValueError, init2)


def test_init_with_empty_stuff():
    a = Dict({})
    b = Dict([])
    assert a == {}
    assert b == {}


def test_init_with_list_of_dicts():
    a = Dict({'a': [{'b': 2}]})
    assert isinstance(a.a[0], Dict)
    assert a.a[0].b == 2


def test_getitem():
    prop = Dict(TEST_DICT)
    assert prop['a']['b']['c'] == TEST_VAL


def test_getattr():
    prop = Dict(TEST_DICT)
    assert prop.a.b.c == TEST_VAL


def test_isinstance():
    assert isinstance(Dict(), dict)


def test_str():
    prop = Dict(TEST_DICT)
    assert str(prop) == str(TEST_DICT)


def test_json():
    some_dict = TEST_DICT
    some_json = json.dumps(some_dict)
    prop = Dict()
    prop.a.b.c = TEST_VAL
    prop_json = json.dumps(prop)
    assert some_json == prop_json


def test_delitem():
    prop = Dict({'a': 2})
    del prop['a']
    assert prop == {}


def test_delitem_nested():
    prop = Dict(TEST_DICT)
    del prop['a']['b']['c']
    assert prop == {'a': {'b': {}}}


def test_delattr():
    prop = Dict({'a': 2})
    del prop.a
    assert prop == {}


def test_delattr_nested():
    prop = Dict(TEST_DICT)
    del prop.a.b.c
    assert prop == {'a': {'b': {}}}


def test_delitem_delattr():
    prop = Dict(TEST_DICT)
    del prop.a['b']
    assert prop == {'a': {}}


def test_prune():
    prop = Dict()
    prop.a.b.c.d
    prop.b
    prop.c = 2
    prop.prune()
    assert prop == {'c': 2}


def test_prune_nested():
    prop = Dict(TEST_DICT)
    prop.b.c.d
    prop.d
    prop.prune()
    assert prop == TEST_DICT


def test_prune_empty_list():
    prop = Dict(TEST_DICT)
    prop.b.c = []
    prop.prune()
    assert prop == TEST_DICT


def test_prune_shared_key():
    prop = Dict(TEST_DICT)
    prop.a.b.d
    prop.prune()
    assert prop == TEST_DICT


def test_prune_dont_remove_zero():
    prop = Dict()
    prop.a = 0
    prop.b.c
    prop.prune()
    assert prop == {'a': 0}


def test_prune_with_list():
    prop = Dict()
    prop.a = [Dict(), Dict(), Dict()]
    prop.a[0].b.c = 2
    prop.prune()
    assert prop == {'a': [{'b': {'c': 2}}]}


def test_prune_with_tuple():
    prop = Dict()
    prop.a = (Dict(), Dict(), Dict())
    prop.a[0].b.c = 2
    prop.prune()
    assert prop == {'a': ({'b': {'c': 2}}, )}


def test_prune_list():
    l = [Dict(), Dict(), Dict()]
    l[0].a.b = 2
    l1 = Dict._prune_iter(l)
    assert l1 == [{'a': {'b': 2}}]


def test_prune_tuple():
    l = (Dict(), Dict(), Dict())
    l[0].a.b = 2
    l1 = Dict._prune_iter(l)
    assert l1 == [{'a': {'b': 2}}]


def test_prune_not_new_list():
    prop = Dict()
    prop.a.b = []
    prop.b = 2
    prop.prune()
    assert prop == {'b': 2}


def test_iter_reduce_with_list():
    prop = Dict()
    prop.a = [Dict(), 1, 2]
    prop.a[0].b.c
    prop.prune()
    assert prop == {'a': [1, 2]}


def test_iter_reduce_with_tuple():
    prop = Dict()
    prop.a = (Dict(), 1, 2)
    prop.a[0].b.c
    prop.prune()
    assert prop == {'a': (1, 2)}


def test_prune_nested_list():
    prop = Dict()
    prop.a = [Dict(), [[]], [1, 2, 3]]
    prop.prune()
    assert prop == {'a': [[1, 2, 3]]}


def test_complex_nested_structure():
    prop = Dict()
    prop.a = [(Dict(), 2), [[]], [1, (2, 3), 0]]
    prop.prune(prune_zero=True)
    assert prop == {'a': [(2,), [1, (2, 3)]]}


def test_tuple_key():
    prop = Dict()
    prop[(1, 2)] = 2
    assert prop == {(1, 2): 2}
    assert prop[(1, 2)] == 2


def test_repr_html():
    prop = Dict()
    prop.a.b.c = TEST_VAL
    assert prop._repr_html_() == TEST_DICT_STR


def test_set_prop_invalid():
    prop = Dict()

    def set_keys():
        prop.keys = 2

    def set_items():
        prop.items = 3

    pytest.raises(AttributeError, set_keys)
    pytest.raises(AttributeError, set_items)

    assert prop == {}


def test_dir():
    key = 'a'
    prop = Dict({key: 1})
    dir_prop = dir(prop)

    dir_dict = dir(Dict)
    for d in dir_dict:
        assert d in dir_prop, d

    assert key in dir_prop

    assert '__methods__' not in dir_prop
    assert '__members__' not in dir_prop


def test_dir_with_members():
    prop = Dict({'__members__': 1})
    dir(prop)
    assert '__members__' in prop.keys()


def test_prune_zero():
    prop = Dict({'a': 1, 'c': 0})
    prop.prune(prune_zero=True)
    assert prop == {'a': 1}


def test_prune_zero_nested():
    prop = Dict({'a': 1, 'c': {'d': 0}})
    prop.prune(prune_zero=True)
    assert prop == {'a': 1}


def test_prune_zero_in_tuple():
    prop = Dict({'a': 1, 'c': (1, 0)})
    prop.prune(prune_zero=True)
    assert prop == {'a': 1, 'c': (1, )}


def test_prune_empty_list_nested():
    prop = Dict({'a': 1, 'c': {'d': []}})
    prop.prune()
    assert prop == {'a': 1}


def test_not_prune_empty_list_nested():
    prop = Dict({'a': 1, 'c': ([], )})
    prop.prune(prune_empty_list=False)
    assert prop == {'a': 1, 'c': ([], )}


def test_do_not_prune_empty_list_nested():
    prop = Dict({'a': 1, 'c': {'d': []}})
    prop.prune(prune_empty_list=False)
    assert prop == {'a': 1, 'c': {'d': []}}


def test_to_dict():
    nested = {'a': [{'a': 0}, 2], 'b': {}, 'c': 2}
    prop = Dict(nested)
    regular = prop.to_dict()
    assert regular == prop
    assert regular == nested
    assert not isinstance(regular, Dict)

    def get_attr():
        regular.a = 2
    pytest.raises(AttributeError, get_attr)

    def get_attr_deep():
        regular['a'][0].a = 1
    pytest.raises(AttributeError, get_attr_deep)


def test_to_dict_with_tuple():
    nested = {'a': ({'a': 0}, {2: 0})}
    prop = Dict(nested)
    regular = prop.to_dict()
    assert regular == prop
    assert regular == nested
    assert isinstance(regular['a'], tuple)
    assert not isinstance(regular['a'][0], Dict)


def test_update():
    old = Dict()
    old.child.a = 'a'
    old.child.b = 'b'
    old.foo = 'c'

    new = Dict()
    new.child.b = 'b2'
    new.child.c = 'c'
    new.foo.bar = True

    old.update(new)

    reference = {
        'foo': {'bar': True},
        'child': {'a': 'a', 'c': 'c', 'b': 'b2'}
    }

    assert old == reference


def test_update_with_lists():
    org = Dict()
    org.a = [1, 2, {'a': 'superman'}]
    someother = Dict()
    someother.b = [{'b': 123}]
    org.update(someother)

    correct = {'a': [1, 2, {'a': 'superman'}],
               'b': [{'b': 123}]}

    org.update(someother)
    assert org == correct
    assert isinstance(org.b[0], dict)


def test_update_with_kws():
    org = Dict(one=1, two=2)
    someother = Dict(one=3)
    someother.update(one=1, two=2)
    assert org == someother


def test_update_with_args_and_kwargs():
    expected = {'a': 1, 'b': 2}
    org = Dict()
    org.update({'a': 3, 'b': 2}, a=1)
    assert org == expected


def test_update_with_multiple_args():
    org = Dict()
    def update():
        org.update({'a': 2}, {'a': 1})

    pytest.raises(TypeError, update)


def test_hook_in_constructor():
    a_dict = Dict(TEST_DICT)
    assert isinstance(a_dict['a'], Dict)


def test_copy():
    class MyMutableObject(object):

        def __init__(self):
            self.attribute = None

    foo = MyMutableObject()
    foo.attribute = True

    a = Dict()
    a.child.immutable = 42
    a.child.mutable = foo

    b = a.copy()

    # immutable object should not change
    b.child.immutable = 21
    assert a.child.immutable == 42

    # mutable object should change
    b.child.mutable.attribute = False
    assert a.child.mutable.attribute == b.child.mutable.attribute

    # changing child of b should not affect a
    b.child = "new stuff"
    assert isinstance(a.child, Dict)


def test_deepcopy():
    class MyMutableObject(object):
        def __init__(self):
            self.attribute = None

    foo = MyMutableObject()
    foo.attribute = True

    a = Dict()
    a.child.immutable = 42
    a.child.mutable = foo

    b = copy.deepcopy(a)

    # immutable object should not change
    b.child.immutable = 21
    assert a.child.immutable == 42

    # mutable object should not change
    b.child.mutable.attribute = False
    assert a.child.mutable.attribute

    # changing child of b should not affect a
    b.child = "new stuff"
    assert isinstance(a.child, Dict)


def test_pickle():
    a = Dict(TEST_DICT)
    assert a == pickle.loads(pickle.dumps(a))


def test_add_on_empty_dict():
    d = Dict()
    d.x.y += 1

    assert d.x.y == 1


def test_add_on_non_empty_dict():
    d = Dict()
    d.x.y = 'defined'

    with pytest.raises(TypeError):
        d.x += 1


def test_add_on_non_empty_value():
    d = Dict()
    d.x.y = 1
    d.x.y += 1

    assert d.x.y == 2


def test_add_on_unsupported_type():
    d = Dict()
    d.x.y = 'str'

    with pytest.raises(TypeError):
        d.x.y += 1


def test_init_from_zip():
    keys = ['a']
    values = [42]
    items = zip(keys, values)
    d = Dict(items)
    assert d.a == 42


if __name__ == '__main__':
    """
    Allow for these test cases to be run from the command line
    via `python test_addict.py`
    """
    pytest.main(['-sv', __file__])
