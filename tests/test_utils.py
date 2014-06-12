from skipper.utils import (
    get_subset, find, contains_keys, get_index, extract_version)


def test_get_subset():
    foo = {'a': 1, 'b': 2, 'c': 3}
    subset = get_subset(foo, ['a'])
    assert subset == {'a': 1}
    subset = get_subset(foo, ['a', 'b'])
    assert subset == {'a': 1, 'b': 2}


def test_find():
    looking_for = {'a': 1, 'match': True}
    array = [looking_for, {'b': 1}, {'a': 2}]
    match = find(array, {'a': 1})
    assert match == looking_for
    match = find(array, {'c': 1})
    assert not match


def test_contains_keys():
    foo = {'b': 1}
    bar = {'b': 2, 'a': 1}
    boo = {'c': 1}
    assert contains_keys(foo, bar) is True
    assert contains_keys(foo, boo) is False


def test_get_index():
    example = [1, 2]
    assert get_index(example, 0) == 1
    assert get_index(example, 3) is None


def test_extract_version():
    version = extract_version("Docker version 0.11.1, build fb99f99")
    assert version == "0.11.1"
