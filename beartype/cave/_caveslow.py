#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype slow cave** (i.e., private subset of the public :mod:`beartype.cave`
subpackage profiled to be inefficiently importable at :mod:`beartype` startup
and thus *not* safely importable throughout the internal :mod:`beartype`
codebase).

See Also
--------
:mod:`beartype._cave._cavefast`
    Further details.
'''

# ....................{ TODO                               }....................
#FIXME: *VESTIGIAL*. The main "beartype" codebase itself no longer imports *ANY*
#of the frankly ad-hoc types or tuple unions defined below. Please deprecate
#these from the public "beartype.cave.__init__" submodule. *sigh*

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import numbers as _numbers
from beartype.cave._caveabc import BoolType
from beartype._cave._cavefast import (
    IterableType,
    NumberType,
    RegexCompiledType,
    SequenceType,
    StrType,
)

# ....................{ TYPES ~ scalar : number            }....................
NumberRealType = IntOrFloatType = _numbers.Real
'''
Type of all **real numbers** (i.e., concrete instances of the abstract
:class:`numbers.Real` base class; numbers expressible as linear values on the
real number line).

This type matches all numbers matched by :class:`NumberType` *except* complex
numbers with non-zero imaginary components, which (as the name implies) are
non-real.

Equivalently, this type matches all integers (e.g., :class:`int`,
:class:`numpy.int_`), floating-point numbers (e.g., :class:`float`,
:class:`numpy.single`), rational numbers (e.g., :class:`fractions.Fraction`,
:class:`sympy.core.numbers.Rational`), and irrational numbers. However,
rational and irrational numbers are rarely used in comparison to integers and
floating-point numbers. This type thus reduces to matching all integer and
floating-point types in practice and is thus also accessible under the alias
:class:`IntOrFloatType` -- a less accurate but more readable name than
:class:`NumberRealType`.

See Also
----------
:class:`NumberType`
    Further details.
'''


IntType = _numbers.Integral
'''
Type of all **integers** (i.e., concrete instances of the abstract
:class:`numbers.Integral` base class; real numbers expressible without
fractional components).

This type matches all numbers matched by the :class:`NumberType` *except*
complex numbers with non-zero imaginary components, rational numbers with
denominators not equal to one, and irrational numbers.

Equivalently, this type matches all integers (e.g., :class:`int`,
:class:`numpy.int_`).

See Also
----------
:class:`NumberType`
    Further details.
'''

# ....................{ TUPLES ~ container : abc           }....................
# Tuples of types assuming the above initialization to have been performed.

NumberOrIterableTypes = (NumberType, IterableType,)
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Iterable`
API.
'''


NumberOrSequenceTypes = (NumberType, SequenceType,)
'''
Tuple of all numeric types *and* all container base classes conforming to (but
*not* necessarily subclassing) the canonical :class:`collections.abc.Sequence`
API.
'''

# ....................{ TUPLES ~ scalar                    }....................
BoolOrNumberTypes = (BoolType, NumberType,)
'''
Tuple of all **boolean** and **number types** (i.e., classes whose instances
are either numbers or types trivially convertible into numbers).

This tuple matches booleans, integers, rational numbers, irrational numbers,
real numbers, and complex numbers.

Booleans are trivially convertible into integers. While details differ by
implementation, common implementations in lower-level languages (e.g., C, C++,
Perl) typically implicitly convert:

* ``False`` to ``0`` and vice versa.
* ``True`` to ``1`` and vice versa.
'''


ScalarTypes = BoolOrNumberTypes + (StrType,)
'''
Tuple of all **scalar types** (i.e., classes whose instances are atomic scalar
primitives).

This tuple matches all:

* **Boolean types** (i.e., types satisfying the :class:`BoolType` protocol).
* **Numeric types** (i.e., types satisfying the :class:`NumberType` protocol).
* **Textual types** (i.e., types contained in the :class:`StrTypes` tuple).
'''


RegexTypes = (RegexCompiledType, StrType)
'''
Tuple of all **regular expression-like types** (i.e., types either defining
regular expressions or losslessly convertible to such types).

This tuple matches:

* The **compiled regular expression type** (i.e., type of all objects created
  and returned by the stdlib :func:`re.compile` function).
* All **textual types** (i.e., types contained in the :class:`StrTypes`
  tuple).
'''
