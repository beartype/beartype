#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking callable signature factory classes** (i.e., subclasses
thread-safely generating pure-Python functions detecting whether arbitrary
objects passed to those functions satisfy the type hints passed to those
factories and either returning those results as their boolean return *or*
raising fatal exceptions or emitting non-fatal warnings if those results are
:data:`False`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cache.cls.cacheclsmega import CacheMegaStrongABC
from beartype._check.cls.call.calldataexternal import (
    BEARTYPE_CALL_EXTERNAL_META)
from beartype._check.cls.hint.hintsane import HINT_SANE_IGNORABLE
from beartype._check.cls.scope.checkexprscope import BeartypeCheckExprScope
from beartype._check.code.codemain import CodeGenerated
from beartype._check.convert.convmain import sanify_hint_root_statement
from beartype._check.forward.reference.fwdrefset import (
    set_beartype_ref_proxies_exception_prefix)
from beartype._check.make.checkmakesig import make_func_signature
from beartype._conf.confmain import BeartypeConf
from beartype._conf.conftest import die_unless_conf
from beartype._data.check.code.datacodename import (
    ARG_NAME_CALL_META,
    FUNC_CHECKER_NAME_PREFIX,
)
from beartype._data.check.code.func.datacodefunccheck import (
    CODE_CHECKER_SIGNATURE)
from beartype._data.check.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.typing.datatyping import CallableRaiserOrTester
from beartype._data.typing.datatypingport import Hint
from beartype._util.error.utilerrraise import reraise_exception_placeholder
from beartype._util.error.utilerrwarn import reissue_warnings_placeholder
from beartype._util.func.utilfuncmake import make_func
from collections.abc import Callable
from itertools import count
from warnings import catch_warnings

# ....................{ SUBCLASSES                         }....................
#FIXME: *BEGIN TESTING FREE-THREADING BUILDS IN "tox.ini"*. Somewhat non-trivial
#as this will necessitate changes to "pyproject.toml". Whatevahs! Mandatory now.
#FIXME: Actually, we can't even do that yet, because PEP 780 has yet to be
#accepted. So lame! So Python. *sigh*

#FIXME: Unit test us up, please.
class BeartypeFuncCheckerFactoryCache(CacheMegaStrongABC):
    '''
    **Type-checking function factory** (i.e., thread-safe cache dynamically
    generating a pure-Python function detecting whether an arbitrary object
    passed to that function satisfies the type hint passed to this factory and
    either returning that result as its boolean return *or* raising a fatal
    exception or emitting a non-fatal warning if that result is :data:`False`).

    This factory underlies both the public
    :func:`beartype.door.die_if_unbearable` and
    :func:`beartype.door.is_bearable` statement-level type-checking functions.

    This factory is strongly inspired by the competing
    :class:`beartype._cache.cls.cacheclsmega.CacheMegaStrongSubclassABC`
    subclass, whose class design ultimately proved too rigid to support the
    domain-specific caching logic warranted by this subclass.

    All methods explicitly defined by this factory are thread-safe.
    '''

    # ..................{ CACHERS                            }..................
    def cache_func_checker(
        self,
        hint: Hint,
        conf: BeartypeConf,
        exception_prefix: str,
        make_code_check: Callable[..., CodeGenerated],
    ) -> CallableRaiserOrTester:
        '''
        **Thread-safe type-checking function factory** (i.e., low-level method
        thread-safely generating a pure-Python function detecting whether an
        arbitrary object passed to that function satisfies the type hint passed
        to this factory and either returning that result as its boolean return
        *or* raising a fatal exception or emitting a non-fatal warning if that
        result is :data:`False`).

        This factory method is thread-safe and memoized for the proper subset of
        type hints whose type-checking code is memoizable.

        Caveats
        -------
        **This factory method intentionally avoids raising a** :exc:`TypeError`
        **when the passed type hint is unhashable.** If this hint is
        unhashable, this method instead creates and returns a new type-checking
        function by calling a lower-level factory method *without* attempting to
        cache that hint. Although non-ideal, generality and stability is
        preferable to specificity and instability by unexpected exceptions.

        **This factory method intentionally accepts no** ``exception_cls``
        **parameter.** Doing so would only ambiguously obscure context-sensitive
        exceptions raised by lower-level utility functions called by this
        higher-level factory method.

        **This factory method dynamically resolves all** :pep:`484`-compliant
        **forward reference type hints visitable from this type hint** against
        the first external lexical scope on the call stack originating from a
        third-party module or package. For efficiency, this factory method does
        so by internally delegating forward hint resolution to the **beartype
        external call metadata singleton** (i.e.,
        :data:`.BEARTYPE_CALL_EXTERNAL_META` global).

        Parameters
        ----------
        hint : Hint
            Type hint to be type-checked.
        conf : BeartypeConf
            **Beartype configuration** (i.e., self-caching dataclass
            encapsulating all settings configuring type-checking for the passed
            type hint).
        exception_prefix : str
            Human-readable substring prefixing raised exception messages.
        make_code_check : Callable[..., CodeGenerated]
            **Type-checking code factory** (i.e., function dynamically
            generating a code snippet of a function type-checking an arbitrary
            object against the passed type hint under the passed beartype
            configuration).

        Returns
        -------
        CallableRaiserOrTester
            Function type-checking this hint against this configuration under
            this beartype call metadata.

        Raises
        ------
        All exceptions raised by the lower-level :func:`.make_check_expr`
        factory. Additionally, this factory also raises:

        BeartypeConfException
            If this configuration is *not* a :class:`.BeartypeConf` instance.
        BeartypeDecorHintForwardRefException
            If this hint contains one or more relative forward references, which
            this factory explicitly prohibits to improve both the efficiency and
            portability of calls by users to the resulting type-checker.
        _BeartypeUtilCallableException
            If this function erroneously generates a syntactically invalid
            type-checking function. That should *never* happen, but let's admit
            that you're still reading this for a reason.

        Warns
        -----
        All warnings emitted by the lower-level :func:`.make_check_expr`
        factory.
        '''
        # assert isinstance(key, Hashable), f'{repr(key)} unhashable.'
        # assert callable(value_factory), f'{repr(value_factory)} uncallable.'

        # Thread-safely...
        with self._lock:
            # ....................{ CACHE                  }....................
            # True only if the function dynamically generated by this factory is
            # safely memoizable back into this cache, defaulting to true.
            is_func_cacheable = True

            # Object with which to cache the function dynamically generated by
            # this factory. Since that function conditionally depends on these
            # parameters, this is the 3-tuple aggregating these objects.
            #
            # Note that this tuple is hashable if and only if this hint is
            # hashable. Since a proper subset of PEP-compliant hints are
            # unhashable (e.g., "Annotated[str, []]"), this tuple *COULD* be
            # unhashable.
            cache_key = (hint, conf, exception_prefix)

            # Attempt to...
            try:
                # Either:
                # * If this hint is safely memoizable *AND* this function
                #   factory has already been passed the same parameters, the
                #   function previously generated by that call.
                # * Else, "None".
                func_checker = self._key_to_value_get(cache_key)

                # If a prior call to this factory has already generated a
                # function type-checking these parameters, return that function.
                if func_checker:
                    return func_checker  # type: ignore[return-value]
                # Else, this is the first prior call to this factory passed
                # these parameters.
            # If the dictionary lookup above raised the standard "TypeError"
            # exception, this hint is unhashable. In this case...
            except TypeError:
                # Record that the function dynamically generated by this factory
                # *CANNOT* be safely memoized back into this cache.
                is_func_cacheable = False

            # ....................{ FACTORY                }....................
            # Attempt to...
            #
            # Note that the passed "exception_prefix" is intentionally *NOT*
            # passed to functions in the body of this "try" block. Why?
            # Memoization efficiency. Instead, the placeholder
            # "EXCEPTION_PLACEHOLDER" is intentionally passed. The "except"
            # block then catches and replaces that with "exception_prefix".
            try:
                # With a context manager "catching" *ALL* non-fatal warnings
                # emitted during this logic for subsequent "playback" below...
                with catch_warnings(record=True) as warnings_issued:
                    # Type-checking function to be returned and the expression
                    # local scope describing that function.
                    func_checker, func_scope_frozen = self._make_func_checker(
                        hint=hint,
                        conf=conf,
                        exception_prefix=exception_prefix,
                        make_code_check=make_code_check,
                    )

                    # If...
                    if (
                        # That function is *SUPERFICIALLY* memoizable *AND*...
                        is_func_cacheable and
                        # The lower-level make_check_expr() code factory
                        # internally called by the above call to the passed
                        # higher-level make_func() code factory memoized the
                        # type-checking expression it dynamically generated
                        # against this hint and configuration, then that
                        # function is *ACTUALLY* memoizable.
                        func_scope_frozen.is_check_expr_cacheable
                        # Else, make_check_expr() refused to memoize this
                        # expression. Ergo, either this root hint itself *OR*
                        # one or more child hints transitively subscripting this
                        # root hint are unmemoizable (e.g., due to conditionally
                        # depending on caller-specific context). In either case,
                        # that function embedding this unmemoizable expression
                        # is also unmemoizable.
                    # Then memoize that function.
                    ):
                        self._key_to_value_set(cache_key, func_checker)
                    # Else, that function is *NOT* safely memoizable.

                # ....................{ WARNING            }....................
                # If one or more warnings were issued, reissue these warnings
                # with each placeholder substring (i.e., "EXCEPTION_PLACEHOLDER"
                # instance) replaced by a human-readable description of this
                # callable and annotated return.
                if warnings_issued:
                    reissue_warnings_placeholder(
                        warnings=warnings_issued, target_str=exception_prefix)
                # Else, *NO* warnings were issued.
            # ....................{ EXCEPTION              }....................
            # If doing so raises *ANY* exception, reraise this exception with
            # each placeholder substring (i.e., "EXCEPTION_PLACEHOLDER"
            # instance) replaced by an explanatory prefix.
            except Exception as exception:
                reraise_exception_placeholder(
                    exception=exception, target_str=exception_prefix)

            # ....................{ RETURN                 }....................
            # Return that type-checking function.
            return func_checker

    # ..................{ PRIVATE ~ factories                }..................
    def _make_func_checker(
        self,
        hint: Hint,
        conf: BeartypeConf,
        exception_prefix: str,
        make_code_check: Callable[..., CodeGenerated],
    ) -> tuple[CallableRaiserOrTester, BeartypeCheckExprScope]:
        '''
        **Non-thread-safe type-checking function factory** (i.e., low-level
        method non-thread-safely generating a pure-Python function detecting
        whether an arbitrary object passed to that function satisfies the type
        hint passed to this factory and either returning that result as its
        boolean return *or* raising a fatal exception or emitting a non-fatal
        warning if that result is :data:`False`).

        This low-level private factory method is non-thread-safe and intended to
        be called *only* by the higher-level public :meth:`.cache_func_checker`
        factory method.

        Parameters
        ----------
        hint : Hint
            Type hint to be type-checked.
        conf : BeartypeConf
            **Beartype configuration** (i.e., self-caching dataclass
            encapsulating all settings configuring type-checking for the passed
            object).
        exception_prefix : str
            Human-readable substring prefixing raised exception messages.
        make_code_check : Callable[..., CodeGenerated]
            **Type-checking code factory** (i.e., function dynamically
            generating a code snippet of a function type-checking an arbitrary
            object against the passed type hint under the passed beartype
            configuration).

        Returns
        -------
        tuple[CallableRaiserOrTester, BeartypeCheckExprScope]
            2-tuple ``(func_checker, func_checker_locals)`` such that:

            * ``func_checker`` is the **type-checking function** (i.e.,
              low-level callable dynamically generated by this factory,
              type-checking an arbitrary user-defined object against this hint).
            * ``func_checker_locals`` is the **type-checking function parameter
              scope** (i.e., dictionary mapping from the name to default value
              of each hidden optional parameter passed to ``func_checker``).
        '''
        assert callable(make_code_check), f'{repr(make_code_check)} uncallable.'
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # ....................{ VALIDATE                   }....................
        # If "conf" is *NOT* a configuration, raise an exception.
        die_unless_conf(conf)
        # Else, "conf" is a configuration.

        # ....................{ LOCALS                     }....................
        #FIXME: This "call_curr" local variable should *DEFINITELY* be
        #refactored into a new full-blown mandatory "call_curr" parameter passed
        #to the higher-level cache_func_checker() method. This current
        #hard-coded approach is "fine" for now, but will almost certainly cease
        #to be fine sometime soon. We sigh.

        # Beartype external call metadata singleton, enabling logic below to
        # dynamically resolve *ALL* PEP 484-compliant forward reference type
        # hints visitable from this hint against the first external lexical
        # scope on the call stack originating from a third-party package.
        call_curr = BEARTYPE_CALL_EXTERNAL_META

        # Metadata encapsulating the sanification of this possibly insane hint
        # if this hint is supported by @beartype *OR* raise an exception
        # otherwise (i.e., if this hint is unsupported).
        #
        # Do this first *BEFORE* passing this hint to any further callables.
        hint_sane = sanify_hint_root_statement(
            call_curr=call_curr,
            conf=conf,
            hint=hint,
            exception_prefix=EXCEPTION_PLACEHOLDER,
        )
        # print(f'Reduced tester root hint {repr(hint)} to hint or metadata {repr(hint_sane)}.')

        # If this hint is ignorable, all objects satisfy this hint. In this
        # case, return a trivial function unconditionally returning true.
        if hint_sane is HINT_SANE_IGNORABLE:
            # print(f'[_make_func_checker] Ignoring ignorable hint {hint} with conf {conf}!')
            return _FUNC_CHECKER_IGNORABLE
        # Else, this hint is unignorable.

        # ....................{ CODE                       }....................
        # Python code snippet comprising a single boolean expression
        # type-checking an arbitrary object against this hint.
        #
        # Note that this call (and *ONLY* this call) is intentionally passed the
        # "exception_prefix" parameter rather than the "EXCEPTION_PLACEHOLDER"
        # placeholder. Why? Because this call dynamically generates code raising
        # type-checking violations prefixed by this prefix at a later time
        # rather than *NOW*. Passing "EXCEPTION_PLACEHOLDER" would, in
        # particular, erroneously cause the public
        # beartype.door.die_if_unbearable() type-checker to raise unreadable
        # type-checking violations prefixed by "EXCEPTION_PLACEHOLDER" (which is
        # an unreadable placeholder).
        code_check, func_scope_frozen = make_code_check(
            call_curr,
            hint,
            hint_sane,
            conf,
            exception_prefix,
        )
        # print(f'func_scope: {func_scope}')

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with similar logic in
        # make_code_raiser_func_pith_check() below.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # If this hint is annotated by one or more forward references *NOT*
        # resolvable at decoration time, these references have all been proxied
        # by beartype-specific forward reference proxies. In this case...
        if func_scope_frozen.beartype_ref_proxies:
            # Overwrite the default value of the "__exception_prefix_beartype__"
            # class variables bound to these proxies with a specific exception
            # prefix contextually defined by the caller, improving the
            # readability of exceptions raised at type-checking wrapper call
            # time if one of these proxies fails to resolve the reference it
            # proxies.
            set_beartype_ref_proxies_exception_prefix(
                ref_proxies=func_scope_frozen.beartype_ref_proxies,
                exception_prefix=exception_prefix,
            )
        # Else, this hint is annotated by *NO* such references.

        # ....................{ SCOPE                      }....................
        # Mutable dictionary coerced from this immutable frozen dictionary if
        # this dictionary is *NOT* already mutable.
        func_scope = dict(func_scope_frozen)

        # Expose this beartype external call metadata singleton to this wrapper
        # function as a beartype-specific hidden parameter passed to this
        # wrapper function, whose default value is that metadata. Doing so
        # simplifies calls to the get_hint_object_violation() getter in the body
        # of this wrapper function by enabling this metadata to be passed as a
        # single unified parameter (rather than individually as multiple
        # distinct parameters).
        func_scope[ARG_NAME_CALL_META] = call_curr

        # Type-checking expression lexical scope to be returned.
        func_scope_refrozen = func_scope_frozen.refreeze(func_scope)

        # ....................{ FUNCTION                   }....................
        # Unqualified basename of this type-checking function to be created,
        # uniquified by suffixing an arbitrary integer unique to this function.
        func_checker_name = (
            f'{FUNC_CHECKER_NAME_PREFIX}{next(_func_checker_name_counter)}')

        # Python code snippet declaring the signature of the type-checking
        # function function to be defined and returned by this factory.
        code_signature = make_func_signature(
            func_name=func_checker_name,
            func_scope=func_scope,
            code_signature_format=CODE_CHECKER_SIGNATURE,
            conf=conf,
        )

        # Python code snippet defining this type-checking function in full.
        func_checker_code = f'{code_signature}{code_check}'

        # Type-checking function to be returned.
        # print(f'Making checker {repr(func_checker_name)} with conf {conf}...')
        func_checker = make_func(
            func_name=func_checker_name,
            func_code=func_checker_code,
            func_locals=func_scope,
            func_label=EXCEPTION_PLACEHOLDER,
            is_debug=conf.is_debug,
        )

        # ....................{ RETURN                     }....................
        # Return that type-checking function and expression lexical scope.
        return func_checker, func_scope_refrozen

# ....................{ PRIVATE ~ globals                  }....................
_func_checker_name_counter = count(start=0, step=1)
'''
**Type-checking function name uniquifier** (i.e., iterator yielding the next
integer incrementation starting at 0, leveraged by the
:func:`.make_func_checker` factory to uniquify the names of the type-checking
functions dynamically generated by that factory).
'''

# ....................{ PRIVATE ~ testers                  }....................
def _func_checker_ignorable(obj: object) -> bool:
    '''
    **Ignorable type-checking tester function singleton** (i.e., function
    unconditionally returning :data:`True`, semantically equivalent to a tester
    testing whether an arbitrary object passed to this tester satisfies an
    ignorable type hint).

    The :func:`make_func_tester` factory efficiently returns this singleton when
    passed an ignorable type hint rather than inefficiently regenerating a
    unique ignorable type-checking tester function for that hint.
    '''

    return True


_FUNC_CHECKER_IGNORABLE = (
    _func_checker_ignorable,
    BeartypeCheckExprScope(is_check_expr_cacheable=True),
)
'''
**Ignorable type-checking function data** (i.e., 2-tuple ``(func_checker,
func_scope_frozen)`` encapsulating an ignorable type-checking tester function
singleton and metadata trivially describing that singleton).

The :meth:`BeartypeFuncCheckerFactoryCache._make_func_checker` method returns this
global constant when passed an ignorable type hint, an optimization
substantially improving the efficiency of that method in common edge cases.
'''
