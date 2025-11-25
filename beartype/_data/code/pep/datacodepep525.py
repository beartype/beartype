#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`525` **type-checking expression snippets** (i.e.,
triple-quoted pure-Python string constants formatted and concatenated together
to dynamically generate boolean expressions type-checking arbitrary objects
against :pep:`525`-compliant asynchronous generator factories).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.code.datacodename import VAR_NAME_PITH_ROOT
from beartype._data.typing.datatyping import CallableStrFormat

# ....................{ CODE                               }....................
#FIXME: Conditionally assign this string to the
#"self.func_wrapper_code_return_prefix" instance variable in the
#BeartypeDecorMeta.reinit() method, please.
CODE_PEP525_RETURN_PREFIX = f'''
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # [BEGIN "async yield from"] What follows is the pure-Python implementation
    # of the "async yield from" expression... if that existed, which it doesn't.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Attempt to...
    try:
        # Prime the inner generator by awaiting the value yielded by iterating
        # the inner generator once. Note that *ALL* generators are intrinsically
        # iterable without needing to call either the iter() or aiter()
        # builtins, both of which simply return the passed generator as is.
        __beartype_agen_yield_pith = await anext({VAR_NAME_PITH_ROOT})

        # PEP 525-compliant bidirectional communication loop, shuttling values
        # and exceptions between the caller and inner generator.
        while True:
            # Attempt to...
            try:
                # Yield the value previously yielded by the inner generator up
                # to the caller *AND* capture any value sent in from the caller.
                __beartype_agen_send_pith = yield __beartype_agen_yield_pith

                # Attempt to...
                try:
                    # If the caller did *NOT* send a value into this outer
                    # generator, the caller iterated this outer generator.
                    # Iterate the inner generator *AND* capture the value
                    # yielded in response. This is the common case.
                    if __beartype_agen_send_pith is None:
                        __beartype_agen_yield_pith = await anext(
                            {VAR_NAME_PITH_ROOT})
                    # Else, the caller sent a value into this outer generator.
                    # Propagate this value to the inner generator *AND* capture
                    # the value yielded in response. This is an edge case.
                    else:
                        __beartype_agen_yield_pith = await asend(
                            __beartype_agen_send_pith)
                # If doing so raised a PEP 525-compliant "StopAsyncIteration"
                # exception, the inner generator finished immediately without
                # yielding anything further. This is a valid use case. Squelch
                # this exception and halt looping.
                #
                # Note that this exception handling *CANNOT* be merged into the
                # exception handling performed by the parent "try:" block. The
                # latter handles exceptions thrown into this outer generator by
                # the caller calling either the aclose() or athrow() methods on
                # this outer generator. Catching this "StopAsyncIteration"
                # exception in the parent "try:" block would allow the caller to
                # erroneously halt the inner generator by passing this exception
                # to the athrow() method of this outer generator. Generators may
                # be prematurely halted *ONLY* by calling the aclose() method.
                except StopAsyncIteration:
                    break
            # If the caller threw a PEP 525-compliant "GeneratorExit" exception
            # into this outer generator, the caller instructed this outer
            # generator to prematurely close prior to completion by calling the
            # aclose() method on this outer generator. This is a valid use case.
            except GeneratorExit as exception:
                # Propagate this closure request to the inner generator.
                await {VAR_NAME_PITH_ROOT}.aclose()

                # Re-raise this exception for orthogonality with PEP 380.
                raise
            # If the caller threw an exception into this outer generator by
            # passing this exception to the athrow() method of this outer
            # generator...
            except BaseException as __beartype_agen_exception:
                # Propagate this exception to the inner generator *AND*, if the
                # inner generator also catches this exception and then resumes
                # operation by yielding a value, capture this value.
                try:
                    __beartype_agen_yield_pith = await athrow(
                        __beartype_agen_exception)
                # If doing so raised a PEP 525-compliant "StopAsyncIteration"
                # exception, the inner generator caught this exception and then
                # finished immediately without yielding anything further. This
                # is a valid use case. Squelch this exception and halt looping.
                except StopAsyncIteration:
                    break
    # If doing so raised a PEP 525-compliant "StopAsyncIteration" exception,
    # the inner generator finished immediately without yielding anything. This
    # is a valid use case. Squelch this exception and silently reduce to a noop.
    except StopAsyncIteration:
        pass
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # [END "async yield from"]
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''
'''
:pep:`525`-compliant code snippet prefixing the values to be iteratively yielded
to the caller after calling the decorated asynchronous generator factory in the
body of the wrapper function wrapping that factory with type checking.

This pure-Python code snippet safely implements the hypothetical equivalent of
the ``"async yield from "`` expression -- if that expression existed, which it
does not. Although :pep:`525` claims either pure-Python or C-based
implementations of this expression to currently be infeasible, this snippet
trivially proves that to *not* be the case:

    While it is theoretically possible to implement "yield from" support for
    asynchronous generators, it would require a serious redesign of the
    generators implementation.

See Also
--------
https://github.com/beartype/beartype/issues/592#issuecomment-3559076610
    GitHub issue thread strongly inspiring this implementation. In this thread,
    GitHub users @rboredi and @Glinte present a brilliant first-draft
    pure-Python decorator performing the hypothetical syntactic equivalent of
    the ``"async yield from "`` expression. This code snippet owes a
    considerable debt to @rboredi in particular, who would soon go on to
    extrapolate this explosion of elegance into a full-fledged Python package
    named ``future-async-yield-from``. See below.
https://github.com/rbroderi/future-async-yield-from
    Pure-Python package generalizing the above commentary into a general-purpose
    solution applicable throughout the wider Python ecosystem.
'''

# ....................{ FORMATTERS                         }....................
# str.format() methods, globalized to avoid inefficient dot lookups elsewhere.
# This is an absurd micro-optimization. *fight me, github developer community*
CODE_PEP525_RETURN_PREFIX_format: CallableStrFormat = (
    CODE_PEP525_RETURN_PREFIX.format)
