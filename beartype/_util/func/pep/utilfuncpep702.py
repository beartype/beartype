#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`702`-compliant **callable utilities** (i.e., callables
specifically applicable to :pep:`702`-compliant decorators used to decorate
user-defined callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._data.typing.datatyping import TypeException
from beartype._util.func.utilfunccodeobj import (
    get_codeobject_basename,
    get_func_codeobject_or_none,
)
from beartype._util.func.utilfuncscope import get_func_freevars
from beartype._util.kind.maplike.utilmapset import remove_mapping_keys_except
from beartype._util.module.utilmodimport import import_module_or_none
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_11,
    IS_PYTHON_AT_LEAST_3_13,
)
from collections.abc import Callable
from typing import Optional

# ....................{ TESTERS                            }....................
def is_func_pep702_deprecated(func: Callable) -> bool:
    '''
    :data:`True` only if the passed callable is a :pep:`702`-compliant
    :class:`warnings.deprecated`-based **isomorphic decorator closure** (i.e.,
    closure created and returned by the standard :func:`warnings.deprecated`
    decorator such that that closure isomorphically preserves both the number
    and types of all passed parameters and returns by accepting only a variadic
    positional argument and variadic keyword argument).

    This tester returning :data:`True` implies the passed callable to be a
    higher-level standard closure wrapping a lower-level user-defined callable
    originally decorated by the :pep:`702`-compliant :func:`warnings.deprecated`
    decorator, issuing one non-fatal deprecation warning on each call of that
    decorated callable.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    -------
    bool
        :data:`True` only if that callable was decorated by the
        :pep:`702`-compliant :func:`warnings.deprecated` decorator.

    See Also
    -------
    https://docs.python.org/3/library/warnings.html#warnings.deprecated
        Official Python documentation.
    '''

    # Note that this tester is highly non-trivial thanks entirely to the
    # obfuscatory @warnings.deprecated decorator. For unknown reasons, that
    # decorator ambiguously monkey-patches the PEP 702-compliant
    # "__deprecated__" dunder attribute into both:
    # * The isomorphic wrapper closure created and returned by that decorator.
    #   *THIS IS GOOD*.
    # * The user-defined callable decorated by that decorator. *THIS IS BAD*.
    #
    # Since that decorator ambiguously monkey-patches that dunder attribute into
    # both, there fails to exist a one-to-one mapping between the existence of
    # that dunder attribute and whether or not any given pure-Python function is
    # that isomorphic wrapper closure. The following logic that superficially
    # seems sensible thus fails to disambiguate between these two callables:
    #    # Dunder attribute hopefully *ONLY* declared on by the @warnings.deprecated
    #    # decorator if the passed callable is an isomorphic wrapper closure created
    #    # and returned by that decorator *OR* "None" otherwise (i.e., if the passed
    #    # callable is *NOT* such a closure).
    #    func_deprecated = getattr(func, '__deprecated__', None)
    #
    #    # Return true *ONLY* if the value of this attribute is a string, as mandated
    #    # by PEP 702.
    #    return isinstance(func_deprecated, str)
    #
    # Disambiguating between the above two callables thus requires considerably
    # more intricate logic. Only introspecting the C-based code object
    # underlying the passed callable suffices, sadly. We hardly sigh. *sigh*

    # Code object underlying this callable if this callable is pure-Python *OR*
    # "None" otherwise (e.g., if this callable is C-based).
    func_codeobj = get_func_codeobject_or_none(func)

    # If this callable is *NOT* pure-Python, this callable *CANNOT* be the
    # pure-Python isomorphic wrapper closure created and returned by the
    # @warnings.deprecated decorator. In this case, immediately return false.
    if func_codeobj is None:
        return False
    # Else, this callable is pure-Python and thus *COULD* be the
    # pure-Python isomorphic wrapper closure created and returned by the
    # @warnings.deprecated decorator. Further testing is warranted.

    # If the active Python interpreter targets Python >= 3.11 and thus defines
    # the "co_qualname" attribute on code objects effectively required by the
    # call to the get_codeobject_basename() getter below...
    if IS_PYTHON_AT_LEAST_3_11:
        # Unqualified basename of the physical lexical scope (i.e., module,
        # class, callable) of this code object if that object is executed inside
        # a scope that physically exists *OR* a string constant otherwise
        # (e.g., if that code object is executed outside such a scope).
        func_codeobj_basename = get_codeobject_basename(func_codeobj)

        # Return true only if this basename is that of the wrapper() closure
        # created and returned by the @warnings.deprecated decorator.
        return func_codeobj_basename == 'deprecated.__call__.<locals>.wrapper'
    # Else, the active Python interpreter targets Python 3.10 and thus fails to
    # define that "co_qualname" attribute on code objects effectively required
    # by the call to the get_codeobject_basename() getter above.

    # Fallback to slower and clumsier logic introspecting obscure code object
    # instance variables.
    return (
        func_codeobj.co_freevars ==
        #FIXME: Delete this global after dropping Python 3.10 support! \o/
        _FUNC_WARNINGS_DEPRECATED_CODEOBJECT_FREEVAR_NAMES
    )

# ....................{ GETTERS                            }....................
#FIXME: Reduce to "from warnings import deprecated" after dropping 3.12! \o/
#FIXME: Unit test us up, please. *sigh*
#FIXME: Actually call elsewhere, please. This includes:
#* make_func_pep702_deprecated() below.
#* beartype_func_warnings_deprecated() elsewhere.
#* test_is_func_pep702_deprecated() elsewhere.
#* test_decor_warnings_deprecated() elsewhere.
#FIXME: Docstring us up, please. *sigh*
def get_pep702_decorator_type_or_none() -> Optional[type]:
    '''
    '''

    #FIXME: Comment us up, please. *sigh*
    deprecated: Optional[type] = None

    # If the active Python interpreter targets Python >= 3.13, then:
    # * The standard PEP 702-compliant @warnings.deprecated decorator exists.
    # * The third-party @typing_extensions.deprecated decorator is actually just
    #   a trivial alias of the standard @warnings.deprecated decorator.
    #
    # In any case, the only @warnings.deprecated decorator that exists under
    # Python >= 3.13 is this decorator itself. Import this decorator directly.
    if IS_PYTHON_AT_LEAST_3_13:
        from warnings import deprecated  # type: ignore[attr-defined,no-redef]
    # Else, the active Python interpreter targets Python <= 3.12. In this case:
    # * The standard PEP 702-compliant @warnings.deprecated decorator does *NOT*
    #   exist.
    # * The third-party @typing_extensions.deprecated decorator exists if and
    #   only if the "typing_extensions" module itself is importable.
    else:
        # Third-party "typing_extensions" module if importable *OR* "None"
        # otherwise (i.e., if that module is unimportable).
        typing_extensions = import_module_or_none('typing_extensions')

        # If the "typing_extensions" module is importable, fallback to the
        # @typing_extensions_deprecated backport.
        #
        # I *think* this is okay? Prior to 3.13, the deprecated decorator lived
        # in typing_extensions, which means if you've encountered that decorator
        # and you're in (e.g.) Python 3.11, it has to have come from there,
        # right? Right? RIGHT!?!? *sigh*
        if typing_extensions:
            deprecated = typing_extensions.deprecated  # type: ignore[misc]
        # Else, the "typing_extensions" module is unimportable. In this case,
        # return "None" out of mere diabolical desperation.

    # Return this decorator type.
    return deprecated

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please. *sigh*
def make_func_pep702_deprecated(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> 'warnings.deprecated':  # type: ignore[name-defined]
    '''
    :pep:`702`-compliant :class:`warnings.deprecated` decorator initialized with
    all parameters originally passed to the passed
    :class:`warnings.deprecated`-based **isomorphic decorator closure** (i.e.,
    closure created and returned by the standard :func:`warnings.deprecated`
    decorator such that that closure isomorphically preserves both the number
    and types of all passed parameters and returns by accepting only a variadic
    positional argument and variadic keyword argument).

    This factory function recreates the :class:`warnings.deprecated` decorator
    originally decorating the lower-level user-defined callable wrapped by this
    isomorphic decorator closure.

    Parameters
    ----------
    func : Callable
        :func:`warnings.deprecated`-based isomorphic decorator to be inspected.
    exception_cls : type[Exception], default: _BeartypeUtilCallableException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    warnings.deprecated
        :class:`warnings.deprecated` decorator initialized with all parameters
        originally passed to the passed :class:`warnings.deprecated`-based
        isomorphic decorator closure.
    '''
    # print(f'Redecorating @warnings.deprecated-decorated {func}...')

    # ....................{ VALIDATE                       }....................
    # If this callable is *NOT* a closure created and returned by the
    # @warnings.deprecated decorator, raise an exception.
    if not is_func_pep702_deprecated(func):  # pragma: no cover
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not type.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Name of the package defining the @warnings.deprecated decorator type
        # called instantiated below to redecorate the passed callable. See also:
        # * Logic below for details on why this pretends to make sense.
        # * A similar approach in our sibling "decorstandard" submodule.
        decorator_package_name = (
            'warnings' if IS_PYTHON_AT_LEAST_3_13 else 'typing_extensions')

        # Raise a exception embedding this package name.
        raise exception_cls(
            f'{exception_prefix}'
            f'PEP 702 deprecated callable {repr(func)} not decorated by '
            f'@{decorator_package_name}.deprecated.'
        )
    # Else, this callable is a closure created and returned by the
    # @warnings.deprecated decorator.

    # ....................{ IMPORTS                        }....................
    # Defer Python version-specific imports.

    # If the active Python interpreter targets Python >= 3.13, then:
    # * The standard PEP 702-compliant @warnings.deprecated decorator exists.
    # * The third-party @typing_extensions.deprecated decorator is actually just
    #   a trivial alias of the standard @warnings.deprecated decorator.
    #
    # In any case, the only @warnings.deprecated decorator that exists under
    # Python >= 3.13 is this decorator itself. Import this decorator directly.
    if IS_PYTHON_AT_LEAST_3_13:
        from warnings import deprecated  # type: ignore[attr-defined]
    # Else, the active Python interpreter targets Python <= 3.12. In this case:
    # * The standard PEP 702-compliant @warnings.deprecated decorator does *NOT*
    #   exist.
    # * The third-party @typing_extensions.deprecated decorator exists if and
    #   only if the "typing_extensions" module itself is importable.
    else:
        # Third-party "typing_extensions" module if importable *OR* "None"
        # otherwise (i.e., if that module is unimportable).
        typing_extensions = import_module_or_none('typing_extensions')

        # If the "typing_extensions" module is importable, fallback to the
        # @typing_extensions_deprecated backport.
        #
        # I *think* this is okay? Prior to 3.13, the deprecated decorator lived
        # in typing_extensions, which means if you've encountered that decorator
        # and you're in (e.g.) Python 3.11, it has to have come from there,
        # right? Right? RIGHT!?!? *sigh*
        if typing_extensions:
            deprecated = typing_extensions.deprecated  # type: ignore[misc]
        # Else, the "typing_extensions" module is unimportable. In this case,
        # raise an exception.
        #
        # Note that this should *NEVER* be the case. Ergo, we invest *NO* effort
        # in raising a readable exception. Why? Because the caller only calls
        # this factory when the passed callable has already been validated to be
        # a PEP 702-compliant closure, in which case either:
        # * The active Python interpreter targets >= Python 3.13.
        # * The "typing_extensions" module is importable.
        else:  # pragma: no cover
            raise _BeartypeUtilCallableException(
                '"typing_extensions" unimportable.')

    # ....................{ LOCALS                         }....................
    # This closure's scope (i.e., dictionary mapping from the name to value of
    # each closure-scoped local attribute defined in the body of the parent
    # warnings.deprecated.__call__() dunder method also defining and returning
    # this closure).
    deprecated_kwargs = get_func_freevars(func)
    # print(f'deprecated_kwargs: {repr(deprecated_kwargs)}')

    # Tuple of all positional-only parameters accepted by the
    # warnings.deprecated.__init__() constructor (in the requisite order).
    deprecated_args = (deprecated_kwargs['msg'],)

    # ....................{ REDECORATE                     }....................
    # Reduce this scope to the proper subset of all key-value pairs explicitly
    # accepted by the warnings.deprecated.__init__() constructor as optional
    # keyword-only parameters.
    remove_mapping_keys_except(
        mapping=deprecated_kwargs,
        keys=_FUNC_WARNINGS_DEPRECATED_INIT_KWARG_NAMES,
    )

    # New @warnings.deprecated decorator recreated from these parameters.
    deprecated_new = deprecated(*deprecated_args, **deprecated_kwargs)

    # ....................{ RETURN                         }....................
    # Return this redecoration.
    return deprecated_new

# ....................{ PRIVATE ~ constants                }....................
_FUNC_WARNINGS_DEPRECATED_CODEOBJECT_FREEVAR_NAMES = (
    'arg', 'category', 'msg', 'stacklevel')
'''
Tuple of the names of all free variables required by the isomorphic wrapper
closure created and returned by the :class:`warnings.deprecated` decorator.
'''


_FUNC_WARNINGS_DEPRECATED_INIT_KWARG_NAMES = frozenset((
    'category',
    'stacklevel',
))
'''
Frozen set of the names of all keyword-only parameters accepted by the
:func:`warnings.deprecated.__init__` constructor.
'''
