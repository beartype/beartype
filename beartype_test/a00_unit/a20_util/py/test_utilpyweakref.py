#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
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

# ....................{ TESTS ~ factory                    }....................
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
    from weakref import ref as weakref_ref

    # ....................{ ASSERT                         }....................
    # Assert this factory when passed "None" returns the expected singleton.
    obj_weakref, obj_repr = make_obj_weakref_and_repr(None)
    assert isinstance(obj_repr, str)
    assert obj_weakref is _WEAKREF_NONE

    # Assert this factory when passed a mutable C-based container returns
    # "None".
    obj_weakref, obj_repr = make_obj_weakref_and_repr(_WINDS_CONTEND)
    assert isinstance(obj_repr, str)
    assert obj_weakref is None

    # Assert this factory when passed an immutable C-based container returns
    # "None".
    obj_weakref, obj_repr = make_obj_weakref_and_repr(_ITS_HOME)
    assert isinstance(obj_repr, str)
    assert obj_weakref is None

    # Assert this factory when passed any objects *OTHER* than "None" and
    # C-based containers returns a weak reference to those objects.
    #
    # Note that integers and strings are both immutable C-based containers.
    # Neither suffices here, sadly.
    obj_weakref, obj_repr = make_obj_weakref_and_repr(_IN_THESE_SOLITUDES)
    assert isinstance(obj_repr, str)
    assert isinstance(obj_weakref, weakref_ref)
    assert obj_weakref() is _IN_THESE_SOLITUDES

# ....................{ PRIVATE ~ classes                  }....................
class TheVoicelessLightning(object):
    '''
    Arbitrary pure-Python object.
    '''

# ....................{ PRIVATE ~ globals                  }....................
_WINDS_CONTEND = ['Silently there,' 'and heap the snow with breath']
'''
Mutable C-based container.
'''


_ITS_HOME = ('Rapid and strong,' 'but silently')
'''
Immutable C-based container.
'''


_IN_THESE_SOLITUDES = TheVoicelessLightning()
'''
Arbitrary pure-Python object.
'''
