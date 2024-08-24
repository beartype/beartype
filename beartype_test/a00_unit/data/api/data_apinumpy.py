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
    arrays : tuple[numpy.ndarray]
        Tuple of all NumPy arrays classified by this dataclass.

    This dataclass exposes *all* parameters passed to the :meth:`__init__`
    method as instance variables of the same names.
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(
        self,
        array_1d_boolean: 'numpy.typing.NDArray[numpy.bool_]',
        array_1d_complex_128: 'numpy.typing.NDArray[numpy.complex128]',
        array_1d_float_32: 'numpy.typing.NDArray[numpy.float32]',
        array_1d_float_64: 'numpy.typing.NDArray[numpy.float64]',
        array_1d_int_32: 'numpy.typing.NDArray[numpy.int32]',
        array_1d_int_64: 'numpy.typing.NDArray[numpy.int64]',
        array_1d_uint_32: 'numpy.typing.NDArray[numpy.uint32]',
        array_1d_uint_64: 'numpy.typing.NDArray[numpy.uint64]',
        array_1d_memory_view: 'numpy.typing.NDArray[numpy.void]',
        array_1d_string_byte: 'numpy.typing.NDArray[numpy.str_]',
        array_1d_string_char: 'numpy.typing.NDArray[numpy.bytes_]',
    ) -> None:
        '''
        Initialize this NumPy arrays dataclass.

        Parameters
        ----------
        array_1d_boolean : numpy.typing.NDArray[numpy.bool_]
            One-dimensional NumPy array containing only booleans.
        array_1d_complex_128 : numpy.typing.NDArray[numpy.complex128]
            One-dimensional NumPy array containing only 128-bit complex numbers.
        array_1d_float_32 : numpy.typing.NDArray[numpy.float32]
            One-dimensional NumPy array containing only 32-bit floating-point
            numbers.
        array_1d_float_64 : numpy.typing.NDArray[numpy.float64]
            One-dimensional NumPy array containing only 64-bit floating-point
            numbers.
        array_1d_int_32 : numpy.typing.NDArray[numpy.int32]
            One-dimensional NumPy array containing only 32-bit signed integers.
        array_1d_int_64 : numpy.typing.NDArray[numpy.int64]
            One-dimensional NumPy array containing only 64-bit signed integers.
        array_1d_uint_32 : numpy.typing.NDArray[numpy.uint32]
            One-dimensional NumPy array containing only 32-bit unsigned
            integers.
        array_1d_uint_64 : numpy.typing.NDArray[numpy.uint64]
            One-dimensional NumPy array containing only 64-bit unsigned
            integers.
        array_1d_memory_view : numpy.typing.NDArray[numpy.void]
            One-dimensional NumPy array serving as a memory view over arbitrary
            bytes all of the same length.
        array_1d_string_byte : numpy.typing.NDArray[numpy.str_]
            One-dimensional NumPy array containing only byte strings.
        array_1d_string_char : numpy.typing.NDArray[numpy.bytes_]
            One-dimensional NumPy array containing only Unicode strings.
        '''

        # Classify all passed parameters.
        self.array_1d_boolean = array_1d_boolean
        self.array_1d_complex_128 = array_1d_complex_128
        self.array_1d_float_32 = array_1d_float_32
        self.array_1d_float_64 = array_1d_float_64
        self.array_1d_int_32 = array_1d_int_32
        self.array_1d_int_64 = array_1d_int_64
        self.array_1d_uint_32 = array_1d_uint_32
        self.array_1d_uint_64 = array_1d_uint_64
        self.array_1d_memory_view = array_1d_memory_view
        self.array_1d_string_byte = array_1d_string_byte
        self.array_1d_string_char = array_1d_string_char

        # Tuple of *ALL* of the above NumPy arrays.
        self.arrays = (
            array_1d_boolean,
            array_1d_complex_128,
            array_1d_float_32,
            array_1d_float_64,
            array_1d_int_32,
            array_1d_int_64,
            array_1d_uint_32,
            array_1d_uint_64,
            array_1d_memory_view,
            array_1d_string_byte,
            array_1d_string_char,
        )

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

    See Also
    --------
    https://stackoverflow.com/a/46854903/2809027
        StackOverflow answer lightly inspiring this implementation.
    '''

    # ..................{ PREAMBLE                           }..................
    # Defer preamble-specific imports.
    from beartype_test._util.module.pytmodtest import is_package_numpy
    from pytest import skip

    # If NumPy is unimportable, raise the "pytest.Skipped" exception skipping
    # *ALL* tests transitively requiring this fixture.
    #
    # Note that explicitly calling "skip_unless_package('numpy')" here fails to
    # raise the expected exception, even when NumPy is unimportable. Why?
    # Because that call only behaves as expected in a decorator context. *sigh*
    if not is_package_numpy():
        skip('NumPy unimportable.')
    # Else, NumPy is importable.

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
        array_1d_boolean=asarray(
            (True, False, True, True, False, True, False, False,)),
        # NumPy array containing only 128-bit complex numbers.
        array_1d_complex_128=asarray(
            (1.3 + 8.23j, 70.222 + 726.2431j, 8294.28730 + 100776.357238j),
            dtype=complex128,
        ),
        # NumPy array containing only 32-bit floats.
        array_1d_float_32=asarray(
            (1.2, 2.4, 3.0, 3.6, 4.0, 4.5, 4.8, 5.6, 6.0, 6.3, 7.0,),
            dtype=float32,
        ),
        # NumPy array containing only 64-bit floats.
        array_1d_float_64=asarray(
            (3.2, 5, 1, 2, 1, 8, 2, 5, 1, 3, 1, 2.8, 1, 1.5, 1, 1, 4,),
            dtype=float64,
        ),
        # NumPy array containing only 32-bit signed integers.
        array_1d_int_32=asarray(
            (1, 0, -3, -5, 2, 6, -4, 9, -2, 3, 8, -4, 1, -3, -7, -7, 5, 0,),
            dtype=int32,
        ),
        # NumPy array containing only 64-bit signed integers.
        array_1d_int_64=asarray(
            (1, 7, -39, 211, 1168, -6728, -40561, -256297, 1696707,),
            dtype=int64,
        ),
        # NumPy array containing only 32-bit unsigned integers.
        array_1d_uint_32=asarray(
            (47, 49, 46, 38, 39, 61),
            dtype=uint32,
        ),
        # NumPy array containing only 64-bit unsigned uintegers.
        array_1d_uint_64=asarray(
            (4, 36, 624, 3744, 5108, 10200, 54912,),
            dtype=uint64,
        ),
        # NumPy array serving as a memory view over arbitrary bytes all of the
        # same length.
        array_1d_memory_view=asarray(
            (
                b'The fissured stones with its entwining arms,',
                b'And did embower with leaves for ever green, ',
                b'And berries dark, the smooth and even space ',
                b'Of its inviolated floor, and here the childr',
            ),
            dtype=void,
        ),
        # NumPy array containing only byte strings.
        array_1d_string_byte=asarray((
            b'It overlooked in its serenity',
            b'The dark earth, and the bending vault of stars.',
            b'It was a tranquil spot, that seemed to smile',
            b'Even in the lap of horror. Ivy clasped',
        )),
        # NumPy array containing only Unicode strings.
        array_1d_string_char=asarray((
            'Yet the grey precipice and solemn pine',
            'And torrent, were not all;—one silent nook',
            'Was there. Even on the edge of that vast mountain,',
            'Upheld by knotty roots and fallen rocks,',
        )),
    )
