#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **named tuple utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant named tuples -- which
is to say, instances of concrete subclasses of the standard
:attr:`typing.NamedTuple` superclass).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.cls.utilclstest import is_type_subclass_proper
# from beartype.roar import BeartypeDecorHintPep484Exception
# from beartype.typing import Any
# from beartype._data.hint.pep.sign.datapepsigns import HintSignNewType
# from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
# from types import FunctionType

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
#FIXME: Actually call us in the get_hint_pep_sign_or_none() getter, please.
def is_hint_pep484_namedtuple_subclass(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a :pep:`484`-compliant **named tuple
    subclass** (i.e., concrete subclass of the standard
    :attr:`typing.NamedTuple` superclass).

    Note that the :attr:`typing.NamedTuple` attribute is *not* actually a
    superclass; that attribute only superficially masquerades (through
    inscrutable metaclass trickery) as a superclass. As one might imagine,
    detecting "subclasses" of a non-existent superclass is non-trivial.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`484`-compliant named tuple
        subclass.
    '''

    # Return true only if...
    return (
        # This hint is a proper tuple subclass (i.e., subclass of the builtin
        # "tuple" type but *NOT* that type itself) *AND*...
        is_type_subclass_proper(hint, tuple) and
        #FIXME: Implement us up, please. To do so efficiently, we'll probably
        #want to:
        #* Declare a private global frozenset of the names of all uniquely
        #  identifying "typing.NamedTuple" attributes: e.g.,
        #  _NAMEDTUPLE_UNIQUE_ATTR_NAMES = frozenset((
        #      # "typing.NamedTuple"-specific quasi-public attributes.
        #      '__annotations__',
        #
        #      # "collections.namedtuple"-specific quasi-public attributes.
        #      '_asdict',
        #      '_field_defaults',
        #      '_fields',
        #      '_make',
        #      '_replace',
        #  ))
        #* Efficiently take the set intersection of that frozenset and
        #  "dir(tuple)". If that intersection is non-empty, then this type is
        #  *PROBABLY* a "typing.NamedTuple" subclass.
        #
        #Note that there does exist an alternative. Sadly, that alternative
        #requires an O(n) test and is thus non-ideal. Nonetheless:
        #    typing.NamedTuple in getattr(hint, '__orig_bases__', ())
        #
        #That *DOES* have the advantage of being deterministic. But the above
        #set intersection test is mostly deterministic and considerably
        #faster... we think. Actually, is it? We have *NO* idea. Perhaps we
        #should simply opt for the simplistic and deterministic O(n) approach.
        True
    )
