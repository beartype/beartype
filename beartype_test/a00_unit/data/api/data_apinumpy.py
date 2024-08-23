#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **generic NumPy data** submodule.

This submodule defines high-level session-scoped fixtures exposing various
objects unique to the third-party :mod:`numpy` package, exercising known edge
cases on behalf of higher-level unit test submodules.
'''

# ....................{ IMPORTS                            }....................
from pytest import fixture

# ....................{ CLASSES                            }....................
class _NumpyArrays(object):
    '''
    **NumPy arrays dataclass** (i.e., well-typed and -described object
    comprising *all* third-party :mod:`numpy` arrays created by the
    session-scoped :func:`.numpy_arrays` fixture).

    Attributes
    ----------
    All parameters passed to the :meth:`__init__` method under the same names.
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(
        self,
        boolean: 'numpy.typing.NDArray[numpy.bool_]',
        complex_128: 'numpy.typing.NDArray[numpy.complex128]',
        float_32: 'numpy.typing.NDArray[numpy.float32]',
        float_64: 'numpy.typing.NDArray[numpy.float64]',
        int_32: 'numpy.typing.NDArray[numpy.int32]',
        int_64: 'numpy.typing.NDArray[numpy.int64]',
        uint_32: 'numpy.typing.NDArray[numpy.uint32]',
        uint_64: 'numpy.typing.NDArray[numpy.uint64]',
        memory_view: 'numpy.typing.NDArray[numpy.void]',
        string_byte: 'numpy.typing.NDArray[numpy.str_]',
        string_char: 'numpy.typing.NDArray[numpy.bytes_]',
    ) -> None:
        '''
        Initialize this NumPy arrays dataclass.

        Parameters
        ----------
        boolean : numpy.typing.NDArray[numpy.bool_]
            NumPy array containing only booleans.
        complex_128 : numpy.typing.NDArray[numpy.complex128]
            NumPy array containing only 128-bit complex numbers.
        float_32 : numpy.typing.NDArray[numpy.float32]
            NumPy array containing only 32-bit floating-point numbers.
        float_64 : numpy.typing.NDArray[numpy.float64]
            NumPy array containing only 64-bit floating-point numbers.
        int_32 : numpy.typing.NDArray[numpy.int32]
            NumPy array containing only 32-bit signed integers.
        int_64 : numpy.typing.NDArray[numpy.int64]
            NumPy array containing only 64-bit signed integers.
        uint_32 : numpy.typing.NDArray[numpy.uint32]
            NumPy array containing only 32-bit unsigned integers.
        uint_64 : numpy.typing.NDArray[numpy.uint64]
            NumPy array containing only 64-bit unsigned integers.
        memory_view : numpy.typing.NDArray[numpy.void]
            NumPy array serving as a memory view over arbitrary bytes all of the
            same length.
        string_byte : numpy.typing.NDArray[numpy.str_]
            NumPy array containing only byte strings.
        string_char : numpy.typing.NDArray[numpy.bytes_]
            NumPy array containing only Unicode strings.
        '''

        # Classify all passed parameters.
        self.boolean = boolean
        self.complex_128 = complex_128
        self.float_32 = float_32
        self.float_64 = float_64
        self.int_32 = int_32
        self.int_64 = int_64
        self.uint_32 = uint_32
        self.uint_64 = uint_64
        self.memory_view = memory_view
        self.string_byte = string_byte
        self.string_char = string_char

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def numpy_arrays() -> _NumpyArrays:
    '''
    Session-scoped fixture yielding a **NumPy arrays dataclass** (i.e.,
    well-typed and -described object comprising various third-party :mod:`numpy`
    arrays exercising edge cases of interest to higher-level unit tests).

    Raises
    ------
    :exc:`pytest.Skipped`
        If :mod:`numpy` is unimportable under the active Python interpreter, in
        which case *all* tests transitively requiring this fixture will be
        skipped as well. Praise be to :mod:`pytest`.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from numpy import (
        asarray,
        complex128,
        float32,
        float64,
        int32,
        int64,
        uint32,
        uint64,
        void,
    )

    # Yield the desired NumPy arrays dataclass.
    yield _NumpyArrays(
        # NumPy array containing only booleans.
        boolean=asarray((True, False, True, True, False, True, False, False,)),
        # NumPy array containing only 128-bit complex numbers.
        complex_128=asarray(
            (1.3 + 8.23j, 70.222 + 726.2431j, 8294.28730 + 100776.357238j),
            dtype=complex128,
        ),
        # NumPy array containing only 32-bit floats.
        float_32=asarray(
            (1.2, 2.4, 3.0, 3.6, 4.0, 4.5, 4.8, 5.6, 6.0, 6.3, 7.0,),
            dtype=float32,
        ),
        # NumPy array containing only 64-bit floats.
        float_64=asarray(
            (3.2, 5, 1, 2, 1, 8, 2, 5, 1, 3, 1, 2.8, 1, 1.5, 1, 1, 4,),
            dtype=float64,
        ),
        # NumPy array containing only 32-bit signed integers.
        int_32=asarray(
            (1, 0, -3, -5, 2, 6, -4, 9, -2, 3, 8, -4, 1, -3, -7, -7, 5, 0,),
            dtype=int32,
        ),
        # NumPy array containing only 64-bit signed integers.
        int_64=asarray(
            (1, 7, -39, 211, 1168, -6728, -40561, -256297, 1696707,),
            dtype=int64,
        ),
        # NumPy array containing only 32-bit unsigned integers.
        uint_32=asarray(
            (47, 49, 46, 38, 39, 61),
            dtype=uint32,
        ),
        # NumPy array containing only 64-bit unsigned uintegers.
        uint_64=asarray(
            (4, 36, 624, 3744, 5108, 10200, 54912,),
            dtype=uint64,
        ),
        # NumPy array serving as a memory view over arbitrary bytes all of the
        # same length.
        memory_view=asarray(
            (
                b'The fissured stones with its entwining arms,',
                b'And did embower with leaves for ever green, ',
                b'And berries dark, the smooth and even space ',
                b'Of its inviolated floor, and here the childr',
            ),
            dtype=void,
        ),
        # NumPy array containing only byte strings.
        string_byte=asarray((
            b'It overlooked in its serenity',
            b'The dark earth, and the bending vault of stars.',
            b'It was a tranquil spot, that seemed to smile',
            b'Even in the lap of horror. Ivy clasped',
        )),
        # NumPy array containing only Unicode strings.
        string_char=asarray((
            'Yet the grey precipice and solemn pine',
            'And torrent, were not all;—one silent nook',
            'Was there. Even on the edge of that vast mountain,',
            'Upheld by knotty roots and fallen rocks,',
        )),
    )
