#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Unmemoized beartype decorator.**

This private submodule defines all core high-level logic underlying the
:func:`beartype.beartype` decorator, whose implementation in the parent
:mod:`beartype._decor.main` submodule is a thin wrapper efficiently memoizing
closures internally created and returned by that decorator. In turn, those
closures directly defer to this submodule.

This private submodule is effectively the :func:`beartype.beartype` decorator
despite *not* actually being that decorator (due to being unmemoized).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
)
from beartype._data.cls.datacls import (
    TYPES_BUILTIN_DECORATOR_DESCRIPTOR_FACTORY)
from beartype._data.datatyping import BeartypeableT
from beartype._decor.conf import BeartypeConf
from beartype._decor._code.codemain import generate_code
from beartype._decor._call import BeartypeCall
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed,
    release_object_typed,
)
from beartype._util.cls.pep.utilpep557 import is_type_pep557
from beartype._util.func.lib.utilbeartypefunc import (
    is_func_unbeartypeable,
    set_func_beartyped,
)
from beartype._util.func.utilfuncmake import make_func

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ DECORATORS                        }....................
def beartype_args_mandatory(
    obj: BeartypeableT, conf: BeartypeConf) -> BeartypeableT:
    '''
    Decorate the passed **beartypeable** (i.e., pure-Python callable or class)
    with optimal type-checking dynamically generated unique to that
    beartypeable.

    Parameters
    ----------
    obj : BeartypeableT
        **Beartypeable** (i.e., pure-Python callable or class) to be decorated.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable or class).

    Returns
    ----------
    BeartypeableT
        Either:

        * If the passed object is a class, this existing class embellished with
          dynamically generated type-checking.
        * If the passed object is a callable, a new callable wrapping that
          callable with dynamically generated type-checking.

    See Also
    ----------
    :func:`beartype._decor.main.beartype`
        Memoized parent decorator wrapping this unmemoized child decorator.
    '''

    # Validate the type of the decorated object *BEFORE* performing any work
    # assuming this object to define attributes (e.g., "func.__name__").
    #
    # If this object is an unusable descriptor created by a builtin type
    # masquerading as a decorator (e.g., @property), @beartype was erroneously
    # listed above rather than below this decorator in the chain of decorators
    # decorating an underlying callable. @beartype typically *MUST* decorate a
    # callable directly. In this case, raise a human-readable exception
    # instructing the end user to reverse the order of decoration.
    #
    # Note that most but *NOT* all of these objects are uncallable. Regardless,
    # *ALL* of these objects are unsuitable for decoration. Specifically:
    # * Under Python < 3.10, *ALL* of these objects are uncallable.
    # * Under Python >= 3.10:
    #   * Descriptors created by @classmethod and @property are uncallable.
    #   * Descriptors created by @staticmethod are technically callable but
    #     C-based and thus unsuitable for decoration.
    if isinstance(obj, TYPES_BUILTIN_DECORATOR_DESCRIPTOR_FACTORY):
        # Human-readable name of this type masquerading as a decorator.
        DECORATOR_NAME = f'@{obj.__class__.__name__}'

        # Raise an exception embedding this name.
        raise BeartypeDecorWrappeeException(
            f'Uncallable descriptor created by builtin decorator '
            f'{DECORATOR_NAME} not decoratable by @beartype. '
            f'Consider listing @beartype below rather than above '
            f'{DECORATOR_NAME} in the decorator chain for this method: '
            f'e.g.,\n'
            f'\t{DECORATOR_NAME}\n'
            f'\t@beartype      # <-- this is the Way of the Bear\n'
            f'\tdef ...'
        )
    # Else, this is object is *NOT* such an unusable descriptor.
    #
    # If this object is a class, return this class decorated with
    # type-checking.
    elif isinstance(obj, type):
        #FIXME: Mypy currently erroneously emits a false negative resembling
        #the following if the "# type: ignore..." pragma is omitted below:
        #    beartype/_decor/main.py:246: error: Incompatible return value type
        #    (got "type", expected "BeartypeableT")  [return-value]
        #This is almost certainly a mypy issue, as _beartype_type() is
        #explicitly annotated as both accepting and returning "BeartypeableT". Until
        #upstream resolves this, we squelch mypy with regret in our hearts.
        return _beartype_type(cls=obj, conf=conf)  # type: ignore[return-value]
    # Else, this object is a non-class.
    #
    # If this object is uncallable, raise an exception.
    elif not callable(obj):
        raise BeartypeDecorWrappeeException(
            f'Uncallable {repr(obj)} not decoratable by @beartype.')
    # Else, this object is callable.
    #
    # If that callable is unbeartypeable (i.e., if this decorator should
    # preserve that callable as is rather than wrap that callable with
    # constant-time type-checking), silently reduce to the identity decorator.
    elif is_func_unbeartypeable(obj):
        return obj
    # Else, that callable is beartypeable. Let's do this, folks.

    # Return a new callable decorating that callable with type-checking.
    return _beartype_func(func=obj, conf=conf)

# ....................{ PRIVATE ~ beartypers              }....................
def _beartype_func(func: BeartypeableT, conf: BeartypeConf) -> BeartypeableT:
    '''
    Decorate the passed callable with dynamically generated type-checking.

    Parameters
    ----------
    func : BeartypeableT
        Callable to be decorated by :func:`beartype.beartype`.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this callable.

    Returns
    ----------
    BeartypeableT
        New pure-Python callable wrapping this callable with type-checking.
    '''
    assert callable(func), f'{repr(func)} uncallable.'
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    #FIXME: Uncomment to display all annotations in "pytest" tracebacks.
    # func_hints = func.__annotations__

    # Previously cached callable metadata reinitialized from this callable.
    func_data = acquire_object_typed(BeartypeCall)
    func_data.reinit(func, conf)

    # Generate the raw string of Python statements implementing this wrapper.
    func_wrapper_code = generate_code(func_data)

    # If this callable requires *NO* type-checking, silently reduce to a noop
    # and thus the identity decorator by returning this callable as is.
    if not func_wrapper_code:
        return func

    #FIXME: Uncomment after uncommenting the corresponding logic below.
    # Fully-qualified name of this undecorated callable to be decorated.
    # func_name_qualified = get_object_name(func)

    #FIXME: Once this is working, use the commented code example starting with
    #"func_code_compiled = compile" given below to associate this filename with
    #this wrapper function.
    #FIXME: Unit test this to externally be the case for function wrappers
    #generated by @beartype, please.

    # Fake filename of the in-memory fake module file masquerading as declaring
    # this wrapper function. This filename guarantees the uniqueness of the
    # 3-tuple ``({func_filename}, {func_file_line_number}, {func_name})``
    # containing this filenames commonly leveraged by profilers (e.g.,
    # "cProfile") to identify arbitrary callables, where:
    # * `{func_filename}` is this filename (e.g.,
    #   `"</home/leycec/py/betse/betse/lib/libs.py:beartype({func_name})>"`).
    # * `{func_file_line_number}`, is *ALWAYS* 0 and thus *NEVER* unique.
    # * `{func_name}`, is identical to that of the decorated callable and also
    #   thus *NEVER* unique.
    #
    # Ergo, uniquifying this filename is the *ONLY* means of uniquifying
    # metadata identifying this wrapper function via runtime inspection.
    #
    # Note this filename is intentionally *NOT* prefixed and suffixed by the
    # "<" and ">" delimiters. Why? Because the stdlib linecache.lazycache()
    # function called below explicitly ignores filenames matching that
    # syntactic format, presumably due to the standard fake module filename
    # "<string>" applied by default to Python code dynamically generated by
    # the eval() and exec() builtins. Since Python occasionally emits in-memory
    # fake filenames resembling "memory:0x7f2ea8589810", we adopt a similar
    # syntax here to generate beartype-specific fake module filenames.
    # func_wrapper_filename = f'beartype_wrapper:{func_name_qualified}'

    #FIXME: Actually, we absolutely *DO* want to leverage the example
    #documented below of leveraging the compile() builtin. We want to do so
    #explicitly to pass something other than "<string>" here -- ideally,
    #"func.__code__.co_filename", ensuring that this wrapper function shares
    #the same absolute filename as that of the original function. To do so:
    #
    #* Implement the
    #  beartype._util.utilcallable.get_callable_filename_or_placeholder()
    #  getter.
    #* Call that function here to obtain that filename.
    #
    #Note that a similar example (also leveraging the exec() builtin, which
    #frankly seems excessive) is also given by:
    #    https://stackoverflow.com/a/42478041/2809027
    #
    #Failure to do so reduces tracebacks induced by exceptions raised by
    #this wrapper to non-human-readability, which is less than ideal: e.g.,
    #
    #    ModuleNotFoundError: No module named 'betsee.util.widget.abc.guiwdgabc'
    #
    #    Traceback (most recent call last):
    #      File "/home/leycec/py/betsee/betsee/gui/simconf/stack/widget/mixin/guisimconfwdgeditscalar.py", line 313, in _set_alias_to_widget_value_if_sim_conf_open
    #        widget=self, value_old=self._widget_value_last)
    #      File "<string>", line 25, in func_beartyped
    #      File "/home/leycec/py/betsee/betsee/gui/simconf/stack/widget/mixin/guisimconfwdgeditscalar.py", line 409, in __init__
    #        *args, widget=widget, synopsis=widget.undo_synopsis, **kwargs)
    #      File "<string>", line 13, in func_beartyped
    #
    #Note the final traceback line, which is effectively useless.
    #FIXME: Note that the existing third-party "makefun" package replacing the
    #stdlib @functools.wraps() decorator is probably the optimal solution for
    #preserving metadata on the original callable into our wrapper callable.
    #While we absolutely should *NOT* depend on that or any other third-party
    #package, that package's implementation should lend us useful insight.
    #Indeed, see the _make() function of the "makefun.main" submodule:
    #    https://github.com/smarie/python-makefun/blob/master/makefun/main.py

    # Function wrapping this callable with type-checking to be returned.
    #
    # For efficiency, this wrapper accesses *ONLY* local rather than global
    # attributes. The latter incur a minor performance penalty, since local
    # attributes take precedence over global attributes, implying all global
    # attributes are *ALWAYS* first looked up as local attributes before
    # falling back to being looked up as global attributes.
    func_wrapper = make_func(
        func_name=func_data.func_wrapper_name,
        func_code=func_wrapper_code,
        func_locals=func_data.func_wrapper_locals,
        func_label=f'@beartyped {func.__name__}() wrapper',
        func_wrapped=func,
        is_debug=conf.is_debug,
        exception_cls=BeartypeDecorWrapperException,
    )

    # Declare this wrapper to be generated by @beartype, which tests for the
    # existence of this attribute above to avoid re-decorating callables
    # already decorated by @beartype by efficiently reducing to a noop.
    set_func_beartyped(func_wrapper)

    # Release this callable metadata back to its object pool.
    release_object_typed(func_data)

    # Return this wrapper.
    return func_wrapper  # type: ignore[return-value]


def _beartype_type(cls: BeartypeableT, conf: BeartypeConf) -> BeartypeableT:
    '''
    Decorate the passed class with dynamically generated type-checking.

    Parameters
    ----------
    cls : BeartypeableT
        Class to be decorated by :func:`beartype.beartype`.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this class.

    Returns
    ----------
    BeartypeableT
        This class decorated by :func:`beartype.beartype`.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    #FIXME: Unit test us up, please.
    # If this class is a dataclass...
    if is_type_pep557(cls):  # type: ignore[arg-type]
        # Wrap the implicit __init__() method generated by the @dataclass
        # decorator with a wrapper function type-checking all dataclass fields
        # annotated by PEP-compliant type hints implicitly passed as parameters
        # of the same name to this method by that decorator. Phew!
        cls.__init__ = _beartype_func(  # type: ignore[misc]
            func=cls.__init__, conf=conf)  # type: ignore[misc]
        return cls  # type: ignore[return-value]

    #FIXME: Generalize to support non-dataclass classes, please.
    # Else, this class is *NOT* a dataclass. In this case, raise an
    # exception.
    raise BeartypeDecorWrappeeException(
        f'{repr(cls)} not decoratable by @beartype, as '
        f'non-dataclasses (i.e., types not decorated by '
        f'@dataclasses.dataclass) currently unsupported by @beartype.'
    )
