#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`589`-compliant **typed dictionary** (i.e.,
:class:`typing.TypedDict` subclass) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.cls.utilclstest import is_type_subclass

# ....................{ TESTERS                            }....................
def is_hint_pep589(hint: object) -> bool:
    '''
    :data:`True` only if the passed object is a :pep:`589`-compliant **typed
    dictionary** (i.e., :class:`typing.TypedDict` subclass).

    This getter is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to a
    one-liner. Moreover, callers are *not* expected to call this tester
    directly. Instead, callers are expected to (in order):

    #. Call the memoized
       :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign_or_none`
       getter, which internally calls this unmemoized tester.
    #. Compare the object returned by that getter against the
       :attr:`beartype._util.data.hint.pep.sign.datapepsigns.HintSignTypedDict`
       sign.

    Motivation
    ----------
    The implementation of the :obj:`typing.TypedDict` attribute substantially
    varies across Python interpreter *and* :mod:`typing` implementation.
    Notably, the :obj:`typing.TypedDict` attribute under Python >= 3.9 is *not*
    actually a superclass but instead a factory function masquerading as a
    superclass by setting the subversive ``__mro_entries__`` dunder attribute to
    a tuple containing a private :obj:`typing._TypedDict` superclass. This
    superclass defines various requisite dunder attributes. Passing the passed
    hint and that superclass to the :func:`issubclass` builtin fails, as the
    metaclass of that superclass prohibits :func:`issubclass` checks. I am
    throwing up in my mouth as I write this.

    Unfortunately, all of the above complications are further complicated by the
    :class:`dict` type under Python >= 3.10. For unknown reasons, Python >= 3.10
    adds spurious ``__annotations__`` dunder attributes to :class:`dict`
    subclasses -- even if those subclasses annotate *no* class or instance
    variables. While a likely bug, we have little choice but to at least
    temporarily support this insanity.

    Parameters
    ----------
    hint : object
        Object to be tested.

    Returns
    -------
    bool
        :data:`True` only if this object is a typed dictionary.
    '''

    # Return true only...
    #
    # Note that this detection scheme is technically susceptible to false
    # positives in unlikely edge cases. Specifically, this test queries for
    # dunder attributes and thus erroneously returns true for user-defined
    # "dict" subclasses *NOT* subclassing the "typing.TypedDict" superclass but
    # nonetheless declaring the same dunder attributes declared by that
    # superclass. Since the likelihood of any user-defined "dict" subclass
    # accidentally defining these attributes is vanishingly small *AND* since
    # "typing.TypedDict" usage is sorta discouraged in the typing community,
    # this error is unlikely to meaningfully arise in real-world use cases.
    # Ergo, it is preferable to implement this test portably, safely, and
    # efficiently rather than accommodate this error.
    #
    # In short, the current approach is strongly preferable.
    return (
        # This hint is a "dict" subclass *AND*...
        #
        # If this hint is *NOT* a "dict" subclass, this hint *CANNOT* be a typed
        # dictionary. By definition, typed dictionaries are "dict" subclasses.
        # Note that PEP 589 actually lies about the type of typed dictionaries:
        #     Methods are not allowed, since the runtime type of a TypedDict
        #     object will always be just dict (it is never a subclass of dict).
        #
        # This is *ABSOLUTELY* untrue. PEP 589 authors plainly forgot to
        # implement this constraint. Contrary to the above:
        # * All typed dictionaries are subclasses of "dict".
        # * The type of typed dictionaries is the private
        #   "typing._TypedDictMeta" metaclass across all Python versions (as of
        #   this comment). Although this metaclass *COULD* currently be used to
        #   detect "TypedDict" subclasses, doing so would increase the fragility
        #   of this fragile codebase by unnecessarily violating privacy
        #   encapsulation.
        #
        # This is where we generously and repeatedly facepalm ourselves.
        is_type_subclass(hint, dict) and
        # The set intersection of the set of the names of all class attributes
        # of this "dict" subclass with the frozen set of the names of all class
        # attributes unique to all "TypedDict" subclasses produces a new set
        # whose length is exactly that of the latter frozen set. Although
        # cumbersome to cognitively parse, this test is *REALLY* fast.
        len(hint.__dict__.keys() & _TYPED_DICT_UNIQUE_ATTR_NAMES) == (
            _TYPED_DICT_UNIQUE_ATTR_NAMES_LEN)
    )

# ....................{ PRIVATE ~ globals                  }....................
_TYPED_DICT_UNIQUE_ATTR_NAMES = frozenset((
    '__annotations__',
    '__total__',
    '__required_keys__',
    '__optional_keys__',
))
'''
Frozen set of the names of all class attributes universally unique to *all*
:class:`typing.TypedDict` subclasses and thus suitable for differentiating
:class:`typing.TypedDict` subclasses from unrelated :class:`dict` subclasses.
'''


_TYPED_DICT_UNIQUE_ATTR_NAMES_LEN = len(_TYPED_DICT_UNIQUE_ATTR_NAMES)
'''
Number of class attributes unique to *all* :class:`typing.TypedDict` subclasses.
'''
