#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
:mod:`os`-specific **PEP-noncompliant type hints** (i.e., unofficial type hints
published by the standard :mod:`os` package) test data.

These hints include subscriptions of:

* The :class:`os.PathLike` type hint factory.

Caveats
-------
Although :mod:`os`-specific type hints are technically PEP-noncompliant, the
:mod:`beartype` codebase currently treats these hints as PEP-compliant to
dramatically simplify code generation for these hints. Ergo, so we do.
'''

# ....................{ FIXTURES                           }....................
def hints_pep_meta_os() -> 'List[HintPepMetadata]':
    '''
    List of :mod:`os`-specific **type hint metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances describing test-specific sample :mod:`os`-specific type hints with
    metadata generically leveraged by various PEP-agnostic unit tests).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer version-specific imports.
    from beartype.typing import (
        Any,
        AnyStr,
    )
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignPep585BuiltinSubscriptedUnknown)
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from os import PathLike
    from pathlib import Path

    # ..................{ CLASSES                            }..................
    class PathBytes(object):  # <-- get it? "Path" bytes? BITES? *har har*
        '''
        **Bytestring path** (i.e., object satisfying the
        class:`os.PathLike[bytes]` protocol by defining the :meth:`__fspath__`
        dunder method to return a bytestring rather than string).
        '''

        def __init__(self, path: bytes) -> None:
            '''
            Initialize this bytestring path against the passed low-level
            bytestring.
            '''

            assert isinstance(path, bytes)
            self._path = path


        def __fspath__(self) -> bytes:
            '''
            Low-level bytestring coerced from this bytestring path.
            '''

            return self._path

    # ..................{ LOCALS                             }..................
    # Arbitrary string path unlikely to exist anywhere, thankfully.
    this_path_strings = Path('/home/alexis/runs/before/she/crawls/')

    # Arbitrary bytestring path unlikely to exist anywhere, also thankfully.
    this_path_bytes = PathBytes(b'/home/leycec/cackles/while/laying/low/')

    # ..................{ LISTS                              }..................
    # List of all module-specific type hint metadata to be returned.
    hints_pep_meta = [
        # ................{ PATHLIKE                           }................
        # Object whose __fspath__() dunder method returns a string.
        HintPepMetadata(
            hint=PathLike[str],
            pep_sign=HintSignPep585BuiltinSubscriptedUnknown,
            isinstanceable_type=PathLike,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Platform-agnostic path encapsulating a string pathname.
                HintPithSatisfiedMetadata(this_path_strings),

                #FIXME: Uncomment *AFTER* deeply type-checking "PathLike[...]".
                # # Platform-agnostic path encapsulating a bytestring pathname.
                # HintPithUnsatisfiedMetadata(this_path_bytes),

                # String constant.
                HintPithUnsatisfiedMetadata(
                    'There came, a dream of hopes that never yet'),
            ),
        ),

        # Object whose __fspath__() dunder method returns a bytestring.
        HintPepMetadata(
            hint=PathLike[bytes],
            pep_sign=HintSignPep585BuiltinSubscriptedUnknown,
            isinstanceable_type=PathLike,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Platform-agnostic path encapsulating a bytestring pathname.
                HintPithSatisfiedMetadata(this_path_bytes),

                #FIXME: Uncomment *AFTER* deeply type-checking "PathLike[...]".
                # # Platform-agnostic path encapsulating a string pathname.
                # HintPithUnsatisfiedMetadata(this_path_strings),

                # Bytestring constant.
                HintPithUnsatisfiedMetadata(
                    b'Had flushed his cheek. He dreamed a veiled maid'),
            ),
        ),

        # ................{ PATHLIKE ~ any                     }................
        # Objects whose __fspath__() dunder methods return either a string *OR*
        # bytestring.
        HintPepMetadata(
            hint=PathLike[Any],
            pep_sign=HintSignPep585BuiltinSubscriptedUnknown,
            isinstanceable_type=PathLike,
            is_pep585_builtin_subscripted=True,
            piths_meta=(
                # Platform-agnostic path encapsulating a bytestring pathname.
                HintPithSatisfiedMetadata(this_path_bytes),
                # Platform-agnostic path encapsulating a string pathname.
                HintPithSatisfiedMetadata(this_path_bytes),
                # String constant.
                HintPithUnsatisfiedMetadata(
                    'Sate near him, talking in low solemn tones.'),
            ),
        ),
        HintPepMetadata(
            hint=PathLike[AnyStr],
            pep_sign=HintSignPep585BuiltinSubscriptedUnknown,
            isinstanceable_type=PathLike,
            is_pep585_builtin_subscripted=True,
            is_typevars=True,
            piths_meta=(
                # Platform-agnostic path encapsulating a bytestring pathname.
                HintPithSatisfiedMetadata(this_path_bytes),
                # Platform-agnostic path encapsulating a string pathname.
                HintPithSatisfiedMetadata(this_path_bytes),
                # Bytestring constant.
                HintPithUnsatisfiedMetadata(
                    b'Her voice was like the voice of his own soul'),
            ),
        ),
    ]

    # ..................{ RETURN                             }..................
    # Return this list of all PEP-specific type hint metadata.
    return hints_pep_meta
