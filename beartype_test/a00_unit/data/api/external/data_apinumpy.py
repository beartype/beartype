#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **NumPy test data fixtures** (i.e., high-level session-scoped
:mod:`pytest` fixtures exposing various third-party :mod:`numpy` objects,
exercising edge cases in unit tests requiring these fixtures).
'''

# ....................{ IMPORTS                            }....................
from pytest import fixture

# ....................{ TODO                               }....................
#FIXME: Overly cumbersome design. Rather than have the numpy_arrays() fixture
#create arrays and then pass those arrays to the _NumpyArrays.__init__() method,
#just:
#* Reduce numpy_arrays() to a trivial one-liner: e.g.,
#      @fixture(scope='session')
#      def numpy_arrays() -> _NumpyArrays:
#          yield _NumpyArrays()
#* Refactor the _NumpyArrays.__init__() method to resemble:
#      def __init__(self) -> None:
#          # Defer fixture-specific imports.
#          from numpy import (
#              asarray,
#              complex128,
#              float32,
#              float64,
#              int32,
#              int64,
#              uint32,
#              uint64,
#              void,
#          )
#  
#          # Classify all attributes of this dataclass. 
#          self.array_1d_boolean = asarray(
#              (True, False, True, True, False, True, False, False,))
#          ...
#
#Trivial, honestly. No idea why we went overkill on the current design. *shrug*

# ....................{ CLASSES                            }....................
class _NumpyArrays(object):
    '''
    **NumPy arrays dataclass** (i.e., object yielded by the
    :func:`.numpy_arrays` fixture comprising various third-party :mod:`numpy`
    arrays of interest to downstream unit tests).

    Attributes
    ----------
    arrays : tuple[numpy.ndarray]
        Tuple of all NumPy arrays classified by this dataclass.
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

    # ....................{ INITIALIZERS                   }....................
    def __init__(self) -> None:
        '''
        Initialize this NumPy arrays dataclass.
        '''

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

        # NumPy array containing only booleans.
        self.array_1d_boolean = asarray(
            (True, False, True, True, False, True, False, False,))

        # NumPy array containing only 128-bit complex numbers.
        self.array_1d_complex_128 = asarray(
            (1.3 + 8.23j, 70.222 + 726.2431j, 8294.28730 + 100776.357238j),
            dtype=complex128,
        )

        # NumPy array containing only 32-bit floats.
        self.array_1d_float_32 = asarray(
            (1.2, 2.4, 3.0, 3.6, 4.0, 4.5, 4.8, 5.6, 6.0, 6.3, 7.0,),
            dtype=float32,
        )

        # NumPy array containing only 64-bit floats.
        self.array_1d_float_64 = asarray(
            (3.2, 5, 1, 2, 1, 8, 2, 5, 1, 3, 1, 2.8, 1, 1.5, 1, 1, 4,),
            dtype=float64,
        )

        # NumPy array containing only 32-bit signed integers.
        self.array_1d_int_32 = asarray(
            (1, 0, -3, -5, 2, 6, -4, 9, -2, 3, 8, -4, 1, -3, -7, -7, 5, 0,),
            dtype=int32,
        )

        # NumPy array containing only 64-bit signed integers.
        self.array_1d_int_64 = asarray(
            (1, 7, -39, 211, 1168, -6728, -40561, -256297, 1696707,),
            dtype=int64,
        )

        # NumPy array containing only 32-bit unsigned integers.
        self.array_1d_uint_32 = asarray(
            (47, 49, 46, 38, 39, 61),
            dtype=uint32,
        )

        # NumPy array containing only 64-bit unsigned uintegers.
        self.array_1d_uint_64 = asarray(
            (4, 36, 624, 3744, 5108, 10200, 54912,),
            dtype=uint64,
        )

        # NumPy array serving as a memory view over arbitrary bytes all of the
        # same length.
        self.array_1d_memory_view = asarray(
            (
                b'The fissured stones with its entwining arms,',
                b'And did embower with leaves for ever green, ',
                b'And berries dark, the smooth and even space ',
                b'Of its inviolated floor, and here the childr',
            ),
            dtype=void,
        )

        # NumPy array containing only byte strings.
        self.array_1d_string_byte = asarray((
            b'It overlooked in its serenity',
            b'The dark earth, and the bending vault of stars.',
            b'It was a tranquil spot, that seemed to smile',
            b'Even in the lap of horror. Ivy clasped',
        ))

        # NumPy array containing only Unicode strings.
        self.array_1d_string_char = asarray((
            'Yet the grey precipice and solemn pine',
            'And torrent, were not all;—one silent nook',
            'Was there. Even on the edge of that vast mountain,',
            'Upheld by knotty roots and fallen rocks,',
        ))

        # Tuple of *ALL* of the above NumPy arrays.
        self.arrays = (
            self.array_1d_boolean,
            self.array_1d_complex_128,
            self.array_1d_float_32,
            self.array_1d_float_64,
            self.array_1d_int_32,
            self.array_1d_int_64,
            self.array_1d_uint_32,
            self.array_1d_uint_64,
            self.array_1d_memory_view,
            self.array_1d_string_byte,
            self.array_1d_string_char,
        )

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def numpy_arrays() -> _NumpyArrays:
    '''
    Session-scoped fixture yielding a **NumPy arrays dataclass** (i.e.,
    object comprising various third-party :mod:`numpy` arrays of interest to
    higher-level unit tests).

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

    # ..................{ YIELD                              }..................
    # Yield a singleton instance of this NumPy array dataclass.
    yield _NumpyArrays()
