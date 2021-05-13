#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`563` **unit tests.**

This submodule unit tests :pep:`563` support implemented in the
:func:`beartype.beartype` decorator.

.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# WARNING: The "from __future__ import annotations" import appears to be
# subtly broken under Python >= 3.10, where performing this import prevents
# the "f_locals" attribute of stack frames from capturing locals defined by
# parent callables and accessed *ONLY* in type hints annotating one or more
# parameters of nested callables contained in those parent callables. Oddly,
# this breakage does *NOT* extend to type hints annotating returns of those
# nested callables -- only parameters. Ergo, we can only conclude this to be a
# subtle bug. We should probably issue an upstream CPython report. For now,
# conditionally disable *ALL* PEP 563-specific tests importing from another
# module containing an "from __future__ import annotations" import. Note that,
# since PEP 563 is mandatory under Python >= 3.10, our entire test suite is
# effectively run under PEP 563 on Python >= 3.10; ergo, conditionally
# disabling these tests imposes no meaningful loss in coverage.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import (
    skip_if_pypy,
    skip_if_python_version_greater_than_or_equal_to,
    skip_if_python_version_less_than,
)
# from pytest import raises

# ....................{ TESTS                             }....................
@skip_if_python_version_less_than('3.7.0')
def test_pep563_module() -> None:
    '''
    Test module-scoped :pep:`563` support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter
    targets Python >= 3.7 *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype_test.a00_unit.data.data_pep563 import (
        get_minecraft_end_txt,
        get_minecraft_end_txt_stanza,
    )

    # Dictionary of these callables' annotations, localized to enable debugging
    # in the likely event of unit test failure. *sigh*
    GET_MINECRAFT_END_TXT_ANNOTATIONS = get_minecraft_end_txt.__annotations__
    GET_MINECRAFT_END_TXT_STANZA_ANNOTATIONS = (
        get_minecraft_end_txt_stanza.__annotations__)

    # Assert that all annotations of a callable *NOT* decorated by @beartype
    # are postponed under PEP 563 as expected.
    assert all(
        isinstance(param_hint, str)
        for param_name, param_hint in (
            GET_MINECRAFT_END_TXT_ANNOTATIONS.items())
    )

    # Assert that *NO* annotations of a @beartype-decorated callable are
    # postponed, as @beartype implicitly resolves all annotations.
    assert all(
        not isinstance(param_hint, str)
        for param_name, param_hint in (
            GET_MINECRAFT_END_TXT_STANZA_ANNOTATIONS.items())
    )

    # Assert that a @beartype-decorated callable works under PEP 563.
    assert get_minecraft_end_txt_stanza(
        player_name='Notch', stanza_index=33) == 'Notch. Player of games.'

    # Test that @beartype silently accepts callables with one or more
    # non-postponed annotations under PEP 563, a technically non-erroneous edge
    # case that needlessly complicates code life.
    #
    # Manually resolve all postponed annotations on a callable.
    get_minecraft_end_txt.__annotations__ = {
        param_name: eval(param_hint, get_minecraft_end_txt.__globals__)
        for param_name, param_hint in (
            get_minecraft_end_txt.__annotations__.items())
    }

    # Manually decorate this callable with @beartype.
    get_minecraft_end_txt_typed = beartype(get_minecraft_end_txt)

    # Assert that this callable works under PEP 563.
    assert isinstance(get_minecraft_end_txt_typed(player_name='Notch'), str)


@skip_if_python_version_less_than('3.7.0')
def test_pep563_closure_nonnested() -> None:
    '''
    Test non-nested closure-scoped :pep:`563` support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter
    targets Python >= 3.7 *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype_test.a00_unit.data.data_pep563 import (
        get_minecraft_end_txt_closure)

    # Assert that declaring a @beartype-decorated closure works under PEP 563.
    get_minecraft_end_txt_substr = get_minecraft_end_txt_closure(
        player_name='Julian Gough')
    assert callable(get_minecraft_end_txt_substr)

    # Assert that this closure works under PEP 563.
    minecraft_end_txt_substr = get_minecraft_end_txt_substr('player')
    assert isinstance(minecraft_end_txt_substr, list)
    assert 'You are the player.' in minecraft_end_txt_substr


#FIXME: *REPORT AN UPSTREAM ISSUE WITH THE PYPY TRACKER AT:*
#    https://foss.heptapod.net/pypy/pypy/-/issues
#So, what's going on here? What's going on here is that PyPy appears to be
#slightly broken with respect to the "FrameType.f_locals" dictionary. Whereas
#CPython provides the actual dictionary of lexically scoped locals required by
#the current frame, PyPy only dynamically computes that dictionary on-the-fly.
#This dynamic computation is known to fail cross-thread but was assumed to be
#fully compliant with CPython expectations when running in the same thread.
#
#This does *NOT* appear to be the case. Specifically, the "IntLike" local
#variable declared by the top-level get_minecraft_end_txt_closure_factory()
#function is:
#* Correctly accessible to the lowest-level
#  get_minecraft_end_txt_closure_inner() closure with respect to actual
#  interpretation of statements and thus declaration of closures by PyPy.
#* Incorrectly omitted from the "FrameType.f_locals" dictionary of the frame
#  object for the mid-level get_minecraft_end_txt_closure_outer() closure
#  declaring the lowest-level get_minecraft_end_txt_closure_inner() closure.
#  What's bizarre is that that dictionary correctly includes the "player_name"
#  parameter accepted by the top-level get_minecraft_end_txt_closure_factory()
#  function.
#
#Clearly, what's happening here is that PyPy developers failed to add local
#variables of lexical scopes declared by distant parent callables (i.e.,
#callables that are *NOT* the direct parent of the lowest-level closure in
#question) when those local variables are *ONLY* accessed in annotations.
#Moreover, when those local variables are accessed outside annotations (as
#with the "player_name" parameter) in the body of the lowest-level closure,
#those variables are correctly added to the "FrameType.f_locals" dictionary.
#Ergo, this is an annotation-specific issue in the internal algorithm PyPy
#uses to dynamically construct that dictionary on-the-fly. Admittedly, this was
#an edge case that basically didn't matter until PEP 563 landed -- at which
#point this edge case *REALLY* mattered.
#FIXME: CPython is subtly broken with respect to "from __future__ import
#annotations" imports under Python >= 3.10. Until resolved, disable this.

@skip_if_pypy()
@skip_if_python_version_greater_than_or_equal_to('3.10.0')
@skip_if_python_version_less_than('3.7.0')
def test_pep563_closure_nested() -> None:
    '''
    Test nested closure-scoped :pep:`563` support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter
    targets Python >= 3.7 *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype_test.a00_unit.data.data_pep563 import (
        get_minecraft_end_txt_closure_factory)

    # Assert that declaring a @beartype-decorated closure factory works under
    # PEP 563.
    get_minecraft_end_txt_closure_outer = (
        get_minecraft_end_txt_closure_factory(player_name='Markus Persson'))
    assert callable(get_minecraft_end_txt_closure_outer)

    # Assert that declaring a @beartype-decorated closure declared by a
    # @beartype-decorated closure factory works under PEP 563.
    get_minecraft_end_txt_closure_inner = get_minecraft_end_txt_closure_outer(
        stanza_len_min=65)
    assert callable(get_minecraft_end_txt_closure_inner)

    # Assert that this closure works under PEP 563.
    minecraft_end_txt_inner = get_minecraft_end_txt_closure_inner(
        stanza_len_max=65, substr='thought')
    assert isinstance(minecraft_end_txt_inner, list)
    assert len(minecraft_end_txt_inner) == 1
    assert minecraft_end_txt_inner[0] == (
        'It is reading our thoughts as though they were words on a screen.')


@skip_if_python_version_less_than('3.7.0')
def test_pep563_class() -> None:
    '''
    Test class-scoped :pep:`563` support implemented in the
    :func:`beartype.beartype` decorator if the active Python interpreter
    targets Python >= 3.7 *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype_test.a00_unit.data.data_pep563 import (
        MinecraftEndTxtUnscrambler)

    # Assert that instantiating a class with a @beartype-decorated __init__()
    # method declaring a @beartype-decorated method closure works.
    minecraft_end_txt_unscrambler = MinecraftEndTxtUnscrambler(
        unscrambling='dream')

    # Assert that that __init__() method declared that method closure.
    get_minecraft_end_txt_unscrambled_stanza = (
        minecraft_end_txt_unscrambler.get_minecraft_end_txt_unscrambled_stanza)
    assert callable(get_minecraft_end_txt_unscrambled_stanza)

    # Assert that this method closure works under PEP 563.
    minecraft_end_txt_unscrambled_stanza = (
        get_minecraft_end_txt_unscrambled_stanza(
            minecraft_end_txt_unscrambler, is_stanza_last=True))
    assert isinstance(minecraft_end_txt_unscrambled_stanza, str)
    assert minecraft_end_txt_unscrambled_stanza.count('dream') == 5

# ....................{ TESTS ~ limit                     }....................
#FIXME: Hilariously, we can't even unit test whether the
#beartype._decor._pep563._die_if_hint_repr_exceeds_child_limit() function
#behaves as expected. See commentary in the
#"beartype_test.a00_unit.data.data_pep563" submodule for all the appalling details.

# @skip_if_python_version_less_than('3.7.0')
# def test_die_if_hint_repr_exceeds_child_limit() -> None:
#     '''
#     Test the private
#     :func:`beartype._decor._pep563._die_if_hint_repr_exceeds_child_limit`
#     function if the active Python interpreter targets at least Python 3.7.0
#     (i.e., the first major Python version to support PEP 563) *or* skip
#     otherwise.
#     '''
#
#     # Defer heavyweight imports.
#     from beartype import beartype
#     from beartype.roar import BeartypeDecorHintPepException
#     from beartype_test.a00_unit.data.data_pep563 import player_was_love
#
#     # Assert @beartype raises the expected exception when decorating a
#     # callable violating this limit.
#     with raises(BeartypeDecorHintPepException):
#         beartype(player_was_love)
