#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`589` **utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep589` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_is_hint_pep589() -> None:
    '''
    Test the
    :beartype._util.hint.pep.proposal.utilpep589.is_hint_pep589` tester.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.utilpep589 import is_hint_pep589
    from beartype_test._util.module.pytmodtyping import (
        import_typing_attr_or_none_safe)

    # ....................{ CLASSES                        }....................
    class NonTypedDict(dict):
        '''
        :class:`dict` subclass defining only one of the requisite three dunder
        attributes necessarily defined by the :class:`typing.TypedDict`
        superclass.
        '''

        # Note that:
        # * The "__annotations__" dunder attribute is intentionally omitted;
        #   that is the *ONLY* dunder attribute guaranteed to be declared by
        #   Python 3.8.
        # * The "__required_keys__" dunder attribute is also intentionally
        #   omitted; for unknown reasons, Python >= 3.8 implicitly adds an
        #   unwanted "__annotations__" dunder attribute to *ALL* "dict"
        #   subclasses -- including "dict" subclasses annotating *NO* class or
        #   instance variables. Defining both the "__required_keys__" and
        #   "__optional_keys__" dunder attributes here would thus suffice for
        #   this subclass to be erroneously detected as a typed dictionary under
        #   Python >= 3.8. And we will sleep now. This has spiralled into
        #   insanity, folks.
        __optional_keys__ = ()
        __total__ = True

    # "typing.TypedDict" superclass imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    TypedDict = import_typing_attr_or_none_safe('TypedDict')

    # If this superclass exists...
    if TypedDict is not None:
        class ThouArtThePath(TypedDict):
            '''
            Arbitrary non-empty typed dictionary annotated to require arbitrary
            key-value pairs.
            '''

            of_that: str
            unresting_sound: int

        # Assert this tester returns true when passed a typed dictionary.
        assert is_hint_pep589(ThouArtThePath) is True

    # ....................{ PASS                           }....................
    # Assert this tester returns false when passed a non-class.
    assert is_hint_pep589(
        'Thou art pervaded with that ceaseless motion,') is False

    # Assert this tester returns false when passed a class *NOT* subclassing
    # the builtin "dict" type.
    assert is_hint_pep589(str) is False

    # Assert this tester returns false when passed the builtin "dict" type.
    assert is_hint_pep589(dict) is False

    # Assert this tester returns false when passed a "dict" subclass defining
    # only two of the requisite three dunder attributes necessarily defined by
    # the "typing.TypedDict" superclass.
    assert is_hint_pep589(NonTypedDict) is False
