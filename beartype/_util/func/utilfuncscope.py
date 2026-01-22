#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable scope** utilities (i.e., functions handling the
possibly nested lexical scopes enclosing arbitrary callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import (
    _BeartypeUtilCallableScopeException,
    _BeartypeUtilCallableScopeNotFoundException,
)
from beartype._util.utilobject import get_object_basename_scoped
from beartype._data.func.datafunccodeobj import FUNC_CODEOBJ_NAME_MODULE
from beartype._data.typing.datatyping import (
    LexicalScope,
    TypeException,
)
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from collections.abc import Callable

# ....................{ GETTERS ~ globals                  }....................
#FIXME: Unit test us up, please.
def get_func_globals(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableScopeException,
    exception_prefix: str = '',
) -> LexicalScope:
    '''
    **Global scope** (i.e., a dictionary mapping from the name to value of each
    globally scoped attribute declared by the module transitively declaring
    the passed pure-Python callable) for this callable.

    This getter transparently supports **wrapper callables** (i.e.,
    higher-level callables whose identifying metadata was propagated from other
    lowel-level callables at either decoration time via the
    :func:`functools.wraps` decorator *or* after declaration via the
    :func:`functools.update_wrapper` function).

    Note that the primary (and indeed only, at the moment) use case for this
    getter is :pep:`563`-compliant resolution of postponed annotations.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.
    ignore_frames : int, default: 0
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past), such that the next non-ignored frame following the
        last ignored frame is the parent callable or module directly declaring
        the passed callable. Defaults to 0.
    exception_cls : Type[Exception], default: _BeartypeUtilCallableScopeException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableScopeException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Dict[str, Any]
        Global scope for this callable.

    Raises
    ------
    exception_cls
        If this callable is a wrapper wrapping a C-based rather than
        pure-Python wrappee callable.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Avoid circular import dependencies.
    from beartype._util.func.utilfuncwrap import unwrap_func_all_isomorphic

    # Lowest-level wrappee callable wrapped by this wrapper callable.
    func_wrappee = unwrap_func_all_isomorphic(func)

    # Dictionary mapping from the name to value of each locally scoped attribute
    # accessible to this wrappee callable to be returned if any *OR* "None"
    # otherwise (i.e., if this wrappee callable fails to define the
    # "__globals__" dunder attribute).
    func_globals = getattr(func_wrappee, '__globals__', None)

    # If this wrappee callable fails to define the "__globals__" dunder
    # attribute, raise an exception.
    #
    # Note that this validation is intentionally implemented manually rather
    # than deferring to related validators such as:
    # * die_unless_func_codeobj(), as only a subset of code-objectables define
    #   the "__globals__" dunder attribute.
    # * die_unless_func_python(), as some callables that are *NOT* pure-Python
    #   actually *DO* define the "__globals__" dunder attribute. C-based bound
    #   method objects are the canonical example.
    if func_globals is None:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception type.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(func)} '
            f'"__globals__" dunder attribute not found, as neither:\n'
            f'* Pure-Python callable.\n'
            f'* C-based bound method object encapsulating a pure-Python method.'
        )
    # Else, this wrappee callable defines the "__globals__" dunder attribute.

    # Return this dictionary.
    #
    # Note that we intentionally do *NOT* return the global scope for this
    # wrapper callable, as wrappers are typically defined in different modules
    # (and thus different global scopes) by different module authors.
    return func_globals

# ....................{ GETTERS ~ locals                   }....................
def get_caller_external_locals(
    # Optional parameters.
    ignore_frames: int = 0,
    exception_cls: TypeException = _BeartypeUtilCallableScopeException,
    **kwargs
) -> LexicalScope:
    '''
    **Local scope** for the first **external lexical scope** on the call stack
    (i.e., originating from any module or package *except* those residing in
    the :mod:`beartype` package itself). Since CPython itself is unlikely to
    ever directly invoke :mod:`beartype`, this scope is (almost certainly) that
    of the third-party package or module that *did* directly invoke
    :mod:`beartype` by calling a public :mod:`beartype` function (e.g.,
    :func:`beartype.door.die_if_unbearable`, :func:`beartype.door.is_bearable`).

    Parameters
    ----------
    ignore_frames : int, default: 0
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past), such that the next non-ignored frame following the
        last ignored frame is the parent callable or module directly declaring
        the passed callable. Defaults to 0.
    exception_cls : Type[Exception], default: _BeartypeUtilCallableScopeException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableScopeException`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`beartype._util.func.utilfuncframe.iter_frames` generator.

    Returns
    -------
    LexicalScope
        Local scope for this callable.

    Raises
    ------
    exception_cls
        If the call stack contains either:

        * *Only* the stack frame encapsulating the current call to this getter.
          Although an extreme edge case, this could technically occur if the
          caller called this getter from a REPL.
        * *Only* two or more ignorable stack frames.

    See Also
    --------
    :func:`.get_func_caller_external_locals`
        Further details.
    '''
    assert isinstance(ignore_frames, int), f'{ignore_frames} not integer.'
    assert ignore_frames >= 0, f'{ignore_frames} negative.'

    # ..................{ IMPORTS                            }..................
    # Avoid circular import dependencies.
    from beartype._util.func.utilfuncframe import (
        get_frame_locals,
        iter_frames,
    )

    # ..................{ LOCALS                             }..................
    # Local scope of the passed callable to be returned.
    func_scope: LexicalScope = {}

    # ..................{ SEARCH                             }..................
    # While at least one frame remains on the call stack, iteratively search up
    # the call stack for the first unignorable frame, whereupon that frame's
    # local runtime scope is returned as is.
    #
    # Note that exactly what "unignorable" means depends on whether the caller
    # passed additional keyword arguments. By default, this getter ignores *ALL*
    # scopes that either:
    # * Do *NOT* derive from a pure-Python object.
    # * Originate inside the "beartype" package.
    # * Originate outside a module.
    for func_frame in iter_frames(
        # 0-based index of the first non-ignored frame following the last
        # ignored frame, ignoring an additional frame embodying the current call
        # to this getter.
        ignore_frames=ignore_frames + 1,
        **kwargs
    ):
    # Then this frame is the first unignorable frame to yield the local runtime
    # scope of to the caller. Why? Because the iter_frames() generator yielded
    # (rather than ignored) this frame. Assuming the caller passed *NO*
    # additional keyword parameters, this *MUST* be a frame encapsulating a
    # scope that:
    # * Derives from a pure-Python object.
    # * Originate outside the "beartype" package.
    # * Originate inside a module.
        # Local scope of this external caller.
        func_scope = get_frame_locals(func_frame)

        # Halt iteration.
        break
    # If the above "break" statement was *NOT* performed, the above call to the
    # iter_frames() generator failed to yield even a single unignorable frame.
    # Ergo, that generator either:
    # * Yielded one or more ignorable frames. This is the common case.
    # * Yielded *NO* frames. Although an extreme edge case, this could
    #   technically occur if the caller called this getter from a REPL.
    #
    # In either case, raise an exception.
    else:  # pragma: no cover
        raise exception_cls(
            'Call stack either empty or comprises only ignorable stack frames.')

    # Return the local scope of this external caller.
    return func_scope


def get_func_locals(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    ignore_frames: int = 0,
    ignore_func_scope_names: int = 0,
    exception_cls: TypeException = _BeartypeUtilCallableScopeException,
    **kwargs
) -> LexicalScope:
    '''
    **Local scope** for the passed callable.

    This getter returns either:

    * If that callable is **nested** (i.e., is a method *or* is a non-method
      callable declared in the body of another callable), a dictionary mapping
      from the name to value of each **locally scoped attribute** (i.e., local
      attribute declared by a parent callable transitively declaring that
      callable) accessible to that callable.
    * Else, the empty dictionary otherwise (i.e., if that callable is a
      function directly declared by a module).

    **This getter transparently supports methods.** In Python, methods are
    lexically nested in the scope encapsulating all previously declared **class
    variables** (i.e., variables declared from class scope and thus accessible
    as type hints when annotating the methods of that class). When declaring a
    class, Python creates a stack frame for the declaration of that class whose
    local scope is the set of all class-scoped attributes declared in the body
    of that class -- including class variables, class methods, static methods,
    and instance methods. When passed any method, this getter finds and returns
    that local scope. When passed the ``MuhClass.muh_method` method declared by
    the following example, for example, this getter returns the local scope
    containing the key ``'muh_class_var'`` with value ``int``:

    .. code-block:: pycon

       >>> from typing import ClassVar
       >>> class MuhClass(object):
       ...    # Class variable declared in class scope.
       ...    muh_class_var: ClassVar[type] = int
       ...    # Instance method annotated by this class variable.
       ...    def muh_method(self) -> muh_class_var: return 42

    However, note that this getter's transparent support for methods does *not*
    extend to methods of the currently decorated class. Why? Because that class
    has yet to be declared and thus added to the call stack.

    **This getter implicitly skips past all other decorators applied** *after*
    the :func:`beartype.beartype` decorator (and thus residing lexically above
    the :func:`beartype.beartype` decorator) in caller code to this callable if
    nested: e.g.,

    .. code-python::

       @the_way_of_kings   <--- skipped past
       @words_of_radiance  <--- skipped past
       @oathbringer        <--- skipped past
       @rhythm_of_war      <--- skipped past
       @beartype
       def the_stormlight_archive(bruh: str) -> str: return bruh

    By default, **this getter also implicitly skips past all lexical scopes**
    that either:

    * Do *not* derive from a **pure-Python object** (e.g., module, type,
      callable). Ergo, C-based objects are thus ignored rather than yielded.
    * Originate inside the :mod:`beartype` package. Ergo, :mod:`beartype`
      objects are thus ignored rather than yielded.
    * Originate outside a module. Ergo, objects only dynamically defined
      in-memory with *no* parent module are thus ignored rather than yielded.

    Caveats
    -------
    **This high-level getter requires the private low-level**
    :func:`sys._getframe` **getter.** If that getter is undefined, this getter
    unconditionally treats the passed callable as module-scoped by returning the
    empty dictionary rather than raising an exception. Since all standard
    Python implementations (e.g., CPython, PyPy) define that getter, this
    should typically *not* be a real-world concern.

    **This high-level getter is inefficient and should thus only be called if
    absolutely necessary.** Specifically, deciding the local scope for any
    callable exhibits worst-case linear time complexity :math:`O(k)` for the
    distance :math:`k` in call stack frames from the call of the current
    function to the call of the top-most parent scope transitively declaring the
    passed callable in its submodule. Ergo, this decision problem should be
    deferred as long as feasible to minimize space and time consumption.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.
    ignore_frames : int, default: 0
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past), such that the next non-ignored frame following the
        last ignored frame is the parent callable or module directly declaring
        the passed callable. Defaults to 0.
    ignore_func_scope_names : int, default: 0
        Number of parent lexical scopes in the fully-qualified name of that
        callable to be ignored (i.e., silently incremented past), such that the
        next non-ignored lexical scope preceding the first ignored lexical scope
        is that of the parent callable or module directly declaring the passed
        callable. This parameter is typically used to ignore the parent lexical
        scopes of parent classes lexically nesting that callable that have yet
        to be fully declared and thus encapsulated by stack frames on the call
        stack (e.g., due to being currently decorated by
        :func:`beartype.beartype`). See the :mod:`beartype._decor._pep.pep563`
        submodule for the standard use case. Defaults to 0.
    exception_cls : Type[Exception], default: _BeartypeUtilCallableScopeException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableScopeException`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`beartype._util.func.utilfuncframe.iter_frames` generator.

    Returns
    -------
    LexicalScope
        Local scope for this callable.

    Raises
    ------
    exception_cls
        If either:

        * The next non-ignored frame following the last ignored frame is *not*
          the parent callable or module directly declaring the passed callable.
        * This lexical scope cannot be found (i.e., if this getter found the
          lexical scope of the module declaring the passed callable *before*
          that of the parent callable or class declaring that callable),
          enabling callers to identify this common edge case.
    '''
    assert callable(func), f'{repr(func)} not callable.'
    assert isinstance(ignore_frames, int), f'{ignore_frames} not integer.'
    assert ignore_frames >= 0, f'{ignore_frames} negative.'
    assert isinstance(ignore_func_scope_names, int), (
        f'{ignore_func_scope_names} not integer.')
    assert ignore_func_scope_names >= 0, (
        f'{ignore_func_scope_names} negative.')
    # print(f'\n--------- Capturing nested {func.__qualname__}() local scope...')

    # ..................{ IMPORTS                            }..................
    # Avoid circular import dependencies.
    from beartype._util.func.utilfunccodeobj import get_func_codeobj
    from beartype._util.func.utilfuncframe import (
        get_frame_locals,
        get_frame_module_name_or_none,
        iter_frames,
    )
    from beartype._util.func.utilfunctest import is_func_nested
    from beartype._util.module.utilmodget import get_object_module_name_or_none

    # ..................{ NOOP                               }..................
    # Note that, if the passed callable is a higher-level wrapper encapsulating
    # a lower-level wrappee, we intentionally return the local scope for this
    # wrapper rather than that wrappee. Why? Because the local scope can *ONLY*
    # be obtained by dynamically inspecting local attributes bound to frames on
    # the current call stack. However, this wrapper was necessarily called by a
    # higher frame than that wrappee! All local attributes declared within the
    # body of this wrapper are irrelevant to that wrappee, as Python
    # syntactically parsed the latter at a later time than the former. If we
    # returned the local scope for that wrappee rather than this wrapper, we
    # would erroneously return local attributes that that wrappee originally had
    # no lexical access to. That's bad. So, we don't do that.

    # Fully-qualified name of the module declaring the passed callable if that
    # callable was physically declared by an on-disk module *OR* "None"
    # otherwise (i.e., if that callable was dynamically declared in-memory).
    func_module_name = get_object_module_name_or_none(func)

    # If either...
    if (
        # The passed callable is dynamically declared in-memory...
        func_module_name is None or
        # The passed callable is module-scoped rather than nested *OR*...
        not is_func_nested(func)
    # Then silently reduce to a noop by treating this nested callable as
    # module-scoped by preserving "func_locals" as the empty dictionary.
    ):
        return FROZENDICT_EMPTY
    # Else, all of the following constraints hold:
    # * The passed callable is physically declared on-disk.
    # * The passed callable is nested.

    # ..................{ LOCALS                             }..................
    # Local scope of the passed callable to be returned.
    func_scope: LexicalScope = {}

    # Unqualified basename of that nested callable.
    func_name_unqualified = func.__name__

    # Lexically scoped name of that nested callable, defined as the
    # "."-delimited concatenation of the unqualified basename of (in order):
    # * Each lexical scope encapsulating that nested callable.
    # * This nested callable itself.
    #
    # Note that this name intentionally omits the fully-qualified name of the
    # module transitively defining that nested callable: e.g.,
    #     >>> def muh_func():
    #     ...     def muh_closure(): pass
    #     ...     return muh_closure()
    #     >>> get_object_basename_scoped(muh_func)
    #     'muh_func'
    #     >>> get_object_basename_scoped(muh_func())
    #     'muh_func.muh_closure'
    func_name_qualified = get_object_basename_scoped(func)

    # Non-empty list of the unqualified names of all parent callables lexically
    # containing that nested callable (including that nested callable itself).
    #
    # Note that:
    # * The set of all callables embodied by the current runtime call stack is a
    #   (usually proper) superset of the set of all callables embodied by the
    #   lexical scopes encapsulating this nested callable. Ergo:
    #   * Some stack frames have no corresponding lexical scopes (e.g., stack
    #     frames embodying callables defined by different modules).
    #   * *ALL* lexical scopes have a corresponding stack frame.
    # * Stack frames are only efficiently accessible relative to the initial
    #   stack frame embodying this nested callable, which resides at the end of
    #   the call stack. This implies we *MUST* iteratively search up the call
    #   stack for frames with relevant lexical scopes and ignore intervening
    #   frames with irrelevant lexical scopes, starting at the stack top (end).
    func_scope_names = func_name_qualified.rsplit(sep='.')

    # Number of lexical scopes encapsulating that callable.
    func_scope_names_len = len(func_scope_names)

    # If that nested callable is *NOT* encapsulated by at least two lexical
    # scopes identifying at least that nested callable and the parent callable
    # or class declaring that nested callable, raise an exception.
    #
    # You are probably now contemplating to yourself in the special darkness of
    # your own personal computer cave: "But @leycec, isn't this condition
    # *ALWAYS* the case? The above `not is_func_nested()` check already ignored
    # non-nested callables."
    #
    # Allow me to now explicate. By the check above, that callable *IS* nested.
    # By the check below, however, only one lexical scope encapsulates that
    # callable. This is not a contradiction. This is just a malicious caller.
    # The get_object_basename_scoped() getter called above silently removed all
    # "<locals>." placeholders from this list of lexical scopes, because those
    # "<locals>." placeholders convey no meaningful semantics. But the
    # is_func_nested() tester detects nested callables by searching for those
    # "<locals>." placeholders. It follows that the caller triggered this
    # condition by maliciously renaming the "__qualname__" dunder attribute of
    # the passed callable to be erroneously prefixed by "<locals>". Curiously,
    # Python permits such manhandling: e.g.,
    #     # Python thinks this is fine.
    #     >>> def muh_func(): pass
    #     >>> muh_func.__qualname__ = '<locals>.muh_func'  # <-- curse ye!
    if func_scope_names_len < 2:
        raise exception_cls(
            f'{func_name_unqualified}() fully-qualified name '
            f'{func.__qualname__}() invalid (e.g., placeholder substring '
            f'"<locals>" not preceded by parent callable name).'
        )
    # Else, that nested callable is encapsulated by at least two lexical scopes
    # identifying at least that nested callable and the parent callable or class
    # declaring that nested callable.
    #
    # If the unqualified basename of the last parent callable lexically
    # containing the passed callable is *NOT* that callable itself, the caller
    # maliciously renamed one but *NOT* both of "__qualname__" and "__name__".
    # In this case, raise an exception. Again, Python permits this. *sigh*
    elif func_scope_names[-1] != func_name_unqualified:
        raise exception_cls(
            f'{func_name_unqualified}() fully-qualified name '
            f'{func.__qualname__}() invalid (i.e., last lexical scope '
            f'"{func_scope_names[-1]}" != unqualified basename '
            f'"{func_name_unqualified}").'
        )
    # Else, the unqualified basename of the last parent callable lexically
    # containing the passed callable is that callable itself.

    # 1-based negative index of the unqualified basename of the parent callable
    # or module directly lexically containing the passed callable in the list of
    # all unqualified basenames encapsulating that callable. By the above
    # validation, this index is guaranteed to begin at the second-to-last
    # basename in this list.
    func_scope_names_index = -2 - ignore_func_scope_names

    # Number of unignorable lexical scopes encapsulating that callable,
    # magically adding 1 to account for the fact that "func_scope_names_index"
    # is a 1-based negative index rather than 0-based positive index.
    func_scope_names_search_len = (
        func_scope_names_len + func_scope_names_index + 1)

    # If exactly *ZERO* unignorable lexical scopes encapsulate that callable,
    # all lexical scopes encapsulating that callable are exactly ignorable,
    # implying that there is *NO* parent lexical scope to search for. In this
    # case, silently reduce to a noop by returning the empty dictionary.
    if func_scope_names_search_len == 0:
        return FROZENDICT_EMPTY
    # If a *NEGATIVE* number of unignorable lexical scopes encapsulate that
    # callable, the caller erroneously insists that there exist more ignorable
    # lexical scopes encapsulating that callable than there actually exist
    # lexical scopes encapsulating that callable. The caller is profoundly
    # mistaken. Whereas the prior branch is a non-erroneous condition that
    # commonly occurs, this current branch is an erroneous condition that should
    # *NEVER* occur. In this case...
    elif func_scope_names_search_len < 0:
        # Number of parent lexical scopes containing that callable.
        func_scope_parents_len = func_scope_names_len - 1

        # Raise an exception.
        raise exception_cls(
            f'Callable name "{func_name_qualified}" contains only '
            f'{func_scope_parents_len} parent lexical scope(s) but '
            f'"ignore_func_scope_names" parameter ignores '
            f'{ignore_func_scope_names} parent lexical scope(s), leaving '
            f'{func_scope_names_search_len} parent lexical scope(s) to be '
            f'searched for {func_name_qualified}() locals.'
        )
    # Else, there are one or more unignorable lexical scopes to be searched.

    # Unqualified basename of the parent callable or module directly lexically
    # containing the passed callable.
    #
    # Note that that the parent callable's local runtime scope transitively
    # contains *ALL* local variables accessible to this nested callable
    # (including the local variables directly contained in the body of that
    # parent callable as well as the local variables directly contained in the
    # bodies of all parent callables of that callable in the same lexical
    # scope). Since that parent callable's local runtime scope is exactly the
    # dictionary to be returned, iteration below searches up the runtime call
    # stack for a stack frame embodying that parent callable and no further.
    func_scope_name = func_scope_names[func_scope_names_index]
    # print(f'Searching for parent {func_scope_name}() local scope...')

    # ..................{ SEARCH                             }..................
    # While at least one frame remains on the call stack, iteratively search up
    # the call stack for a stack frame embodying the parent callable directly
    # declaring this nested callable, whereupon that parent callable's local
    # runtime scope is returned as is.
    #
    # Note that, by default, this getter ignores *ALL* scopes that either:
    # * Do *NOT* derive from a pure-Python object.
    # * Originate inside the "beartype" package.
    # * Originate outside a module.
    for func_frame in iter_frames(
        # 0-based index of the first non-ignored frame following the last
        # ignored frame, ignoring an additional frame embodying the current call
        # to this getter.
        ignore_frames=ignore_frames + 1,
        **kwargs
    ):
        # Code object underlying this frame's scope.
        func_frame_codeobj = get_func_codeobj(func_frame)

        # Unqualified name of this scope.
        func_frame_name = func_frame_codeobj.co_name

        # Fully-qualified name of the module defining this scope if any *OR*
        # "None" otherwise (i.e., if this scope is defined outside a module).
        func_frame_module_name = get_frame_module_name_or_none(func_frame)
        # print(f'{func_frame_name}() detected on call stack...')
        # print(f'func_frame_name == func_scope_name? {func_frame_name == func_scope_name}')
        # print(f'func_frame_module_name == func_module_name? {func_frame_module_name == func_module_name}')
        # print(f'{func_frame_name}() locals: {repr(func_frame.f_locals)}')

        # If this scope is the placeholder string assigned by Python to *ALL*
        # lexical scopes encapsulating the top-most lexical scope of a module
        # declaration in the current call stack, this search has just crossed a
        # module declaration boundary and is thus no longer searching within the
        # module declaring this nested callable and has thus failed to find the
        # lexical scope of the parent declaring this nested callable. Why?
        # Because this scope *MUST* necessarily be in the same module as that of
        # this nested callable. In this case, raise an exception.
        if func_frame_name == FUNC_CODEOBJ_NAME_MODULE:
            raise _BeartypeUtilCallableScopeNotFoundException(
                f'{func_name_qualified}() parent lexical scope '
                f'"{func_scope_name}" not found on call stack.'
            )
        # Else, that scope is *NOT* a module.
        #
        # If...
        elif (
            # That callable's name is that of the current lexical scope to be
            # found *AND*...
            func_frame_name == func_scope_name and
            # That callable's module is that of this nested callable's and thus
            # resides in the same lexical scope...
            func_frame_module_name == func_module_name
        ):
        # Then that callable embodies the lexical scope to be found. In this
        # case, that callable is the parent callable directly declaring this
        # nested callable.
        #
        # Note that this scope *CANNOT* be validated to declare this nested
        # callable. Why? Because this getter function is called by the
        # @beartype decorator when decorating this nested callable, which has
        # yet to be declared until @beartype creates and returns a new wrapper
        # function and is thus unavailable from this scope: e.g.,
        #     # This conditional *ALWAYS* raises an exception, because this
        #     # nested callable has yet to be declared.
        #     if func_name not in func_locals:
        #         raise exception_cls(
        #             f'{func_label} not declared by lexically scoped parent '
        #             f'callable(s) that declared local variables:\n{repr(func_locals)}'
        #         )
        #
        # Ergo, we have *NO* alternative but to blindly assume the above
        # algorithm correctly collected this scope, which we only do because we
        # have exhaustively tested this with *ALL* edge cases.

            # Local scope of the passed callable. Since this nested callable is
            # directly declared in the body of this parent callable, the local
            # scope of this nested callable is *EXACTLY* the local scope of the
            # body of this parent callable. Well, isn't that special?
            func_scope = get_frame_locals(func_frame)
            # print(f'{func_frame_name}() locals: {repr(func_scope)}')

            # Halt iteration.
            break
        # Else, that callable does *NOT* embody the current lexical scope to be
        # found. In this case, silently ignore that callable and proceed to the
        # next frame in the call stack.

    # Return the local scope of the passed callable.
    return func_scope

# ....................{ ADDERS                             }....................
def add_func_scope_attr(
    # Mandatory parameters.
    attr: object,
    func_scope: LexicalScope,

    # Optional parameters.
    exception_prefix: str = 'Globally or locally scoped attribute ',
) -> str:
    '''
    Add a new **scoped attribute** (i.e., new key-value pair of the passed
    dictionary mapping from the name to value of each globally or locally scoped
    attribute externally accessed elsewhere, whose key is a machine-readable
    name internally generated by this function to uniquely refer to the passed
    object and whose value is that object) to the passed scope *and* return that
    name.

    Parameters
    ----------
    attr : object
        Arbitrary object to be added to this scope.
    func_scope : LexicalScope
        Local or global scope to add this object to.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to a reasonable human-readable string.

    Returns
    -------
    str
        Name of the passed object in this scope generated by this function.

    Raises
    ------
    _BeartypeUtilCallableScopeException
        If an attribute with the same name as that internally generated by
        this adder but having a different value already exists in this scope.
        This adder uniquifies names by object identifier and should thus
        *never* generate name collisions. This exception is thus intentionally
        raised as a private rather than public exception.
    '''
    assert isinstance(func_scope, dict), f'{repr(func_scope)} not dictionary.'
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # Possibly negative integer uniquely identifying the new attribute referring
    # to this object in this scope.
    attr_id = id(attr)

    # Name of the new attribute referring to this object in this scope, defined
    # as either...
    attr_name = (
        # If this integer is positive, embed this positive integer into this
        # name as is.
        f'{_ATTR_NAME_PREFIX_ID_POSITIVE}{attr_id}'
        if attr_id >= 0 else
        # Else, this integer is negative. In this case, instead embed the
        # absolute value of this negative integer rather than this negative
        # integer itself. The unary prefix "-" is prohibited in Python
        # identifiers. Since this integer is subsequently embedded in a Python
        # identifier, this integer *MUST* be coerced from a negative to
        # non-negative integer first.
        #
        # Note that this edge case *ONLY* applies to PyPy. Specifically, under:
        # * CPython, this integer is guaranteed to be a memory address and thus
        #   non-negative (i.e., "id(attr) >= 0" for all possible attributes).
        # * PyPy, this integer is typically (but *NOT* necessarily) a 0-based
        #   index into an internal object array and thus also non-negative.
        #   Unfortunately, this heuristic is *NOT* a universal guarantee. In a
        #   small handful of edge cases (for presumably exotic objects of
        #   unknown origin), this integer is negative under PyPy. This makes
        #   testing non-deterministic and thus infeasible.
        #
        # This must be what it feels like when code cries.
        f'{_ATTR_NAME_PREFIX_ID_NEGATIVE}{-attr_id}'  # pragma: no cover
    )

    # If an attribute with the same name but differing value already exists in
    # this scope, raise an exception.
    if func_scope.get(attr_name, attr) is not attr:
        raise _BeartypeUtilCallableScopeException(
            f'{exception_prefix}"{attr_name}" already exists with '
            f'differing value:\n'
            f'~~~~[ NEW VALUE ]~~~~\n{repr(attr)}\n'
            f'~~~~[ OLD VALUE ]~~~~\n{repr(func_scope[attr_name])}'
        )
    # Else, either no attribute with this name exists in this scope *OR* an
    # attribute with this name and value already exists in this scope.

    # Refer to the passed object in this scope with this name.
    func_scope[attr_name] = attr

    # Return this name.
    return attr_name

# ....................{ PRIVATE                            }....................
_ATTR_NAME_PREFIX_ID_POSITIVE = '__beartype_object_'
'''
Arbitrary substring prefixing names dynamically synthesized by the
:func:`.add_func_scope_attr` function for attributes whose **object ids** (i.e.,
the integers returned by the :func:`id` builtin) are positive.

See Also
--------
:data:`._ATTR_NAME_PREFIX_ID_NEGATIVE`
    Further details.
'''


# NegaBeartype: I challenge you!
_ATTR_NAME_PREFIX_ID_NEGATIVE = (
    f'{_ATTR_NAME_PREFIX_ID_POSITIVE}oh_pypy_you_sweet_summer_child_')
'''
Arbitrary substring prefixing names dynamically synthesized by the
:func:`.add_func_scope_attr` function for attributes whose **object ids** (i.e.,
the integers returned by the :func:`id` builtin) are negative.

That function coerces negative into positive attribute IDs. Doing so renders the
former suitable for embedding in attribute names that are valid Python
identifiers. That's good. Doing so naively, however, would invite name
collisions between negative and positive attribute IDs whose absolute values are
equal (e.g., ``|-42| == |42|``). To avoid this, the names of attributes whose
IDs are negative are prefixed by a different substring than those of attributes
whose IDs are positive. It's complicated. Did our hand-waving not convince you!?
'''
