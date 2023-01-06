#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **weak reference** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.py.utilpyweakref` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_make_obj_weakref_and_repr() -> None:
    '''
    Test the :func:`beartype._util.py.utilpyweakref.make_obj_weakref_and_repr`
    factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.py.utilpyweakref import (
        _WEAKREF_NONE,
        make_obj_weakref_and_repr,
    )
    from beartype._util.text.utiltextrepr import represent_object
    from weakref import ref as weakref_ref

    # ....................{ ASSERT                         }....................
    # Assert this factory when passed "None" returns the expected singleton.
    obj_weakref, obj_repr = make_obj_weakref_and_repr(None)
    assert obj_repr == represent_object(None, max_len=999999)
    assert obj_weakref is _WEAKREF_NONE

    # Assert this factory when passed a mutable C-based container returns
    # "None".
    obj_weakref, obj_repr = make_obj_weakref_and_repr(_WINDS_CONTEND)
    assert obj_repr == represent_object(_WINDS_CONTEND, max_len=999999)
    assert obj_weakref is None

    # Assert this factory when passed an immutable C-based container returns
    # "None".
    obj_weakref, obj_repr = make_obj_weakref_and_repr(_ITS_HOME)
    assert obj_repr == represent_object(_ITS_HOME, max_len=999999)
    assert obj_weakref is None

    # Assert this factory when passed any objects *OTHER* than "None" and
    # C-based containers returns a weak reference to those objects.
    #
    # Note that integers and strings are both immutable C-based containers.
    # Neither suffices here, sadly.
    obj_weakref, obj_repr = make_obj_weakref_and_repr(_IN_THESE_SOLITUDES)
    assert obj_repr == represent_object(_IN_THESE_SOLITUDES, max_len=999999)
    assert isinstance(obj_weakref, weakref_ref)
    assert obj_weakref() is _IN_THESE_SOLITUDES


def test_get_weakref_obj_or_repr() -> None:
    '''
    Test the :func:`beartype._util.py.utilpyweakref.get_weakref_obj_or_repr`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilPythonWeakrefException
    from beartype._util.py.utilpyweakref import (
        get_weakref_obj_or_repr,
        make_obj_weakref_and_repr,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Iterable of objects that *CAN* be weakly referenced (e.g., due to *NOT*
    # being C-based containers).
    _WEAKREFABLES = (None, _IN_THESE_SOLITUDES)

    # Iterable of objects that *CANNOT* be weakly referenced (e.g., due to being
    # C-based containers).
    _NON_WEAKREFABLES = (_WINDS_CONTEND, _ITS_HOME)

    # ....................{ PASS                           }....................
    # For each object that *CAN* be weakly referenced...
    for weakrefable in _WEAKREFABLES:
        # Weak reference to and representation of this object.
        weakrefable_weakref, weakrefable_repr = make_obj_weakref_and_repr(
            weakrefable)

        # Strong reference to the same object accessed via this weak reference.
        weakrefable_new = get_weakref_obj_or_repr(
            weakrefable_weakref, weakrefable_repr)

        # Assert that these objects are, in fact, the same object.
        assert weakrefable_new is weakrefable

    # For each object that *CANNOT* be weakly referenced...
    for non_weakrefable in _NON_WEAKREFABLES:
        # Fake weak reference to and representation of this object.
        non_weakrefable_weakref, non_weakrefable_repr = (
            make_obj_weakref_and_repr(non_weakrefable))

        # Fake strong reference to this same object accessed via this fake weak
        # reference.
        non_weakrefable_new = get_weakref_obj_or_repr(
            non_weakrefable_weakref, non_weakrefable_repr)

        # Assert that this fake strong reference is actually just the
        # representation of this object.
        assert non_weakrefable_new is non_weakrefable_repr

    # ....................{ FAIL                           }....................
    # Assert that calling this getter with a valid representation but invalid
    # weak reference raises the expected exception.
    with raises(_BeartypeUtilPythonWeakrefException):
        get_weakref_obj_or_repr(
            'Rapid and strong, but silently!', '"Its home"')

# ....................{ PRIVATE ~ classes                  }....................
class _TheVoicelessLightning(object):
    '''
    Arbitrary pure-Python object.
    '''

# ....................{ PRIVATE ~ classes                  }....................
class _TheVoicelessLightning(object):
    '''
    Arbitrary pure-Python object.
    '''

# ....................{ PRIVATE ~ globals                  }....................
_WINDS_CONTEND = ['Silently there', 'and heap the snow with breath']
'''
Mutable C-based container.
'''


_ITS_HOME = ('Rapid and strong', 'but silently')
'''
Immutable C-based container.
'''


_IN_THESE_SOLITUDES = _TheVoicelessLightning()
'''
Arbitrary pure-Python object.
'''
