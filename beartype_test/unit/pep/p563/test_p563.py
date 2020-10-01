#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 563`_ **unit tests.**

This submodule unit tests `PEP 563`_ support implemented in the
:func:`beartype.beartype` decorator.

.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import skip_if_python_version_less_than
# from pytest import raises

# ....................{ TESTS ~ type                      }....................
@skip_if_python_version_less_than('3.7.0')
def test_p563() -> None:
    '''
    Test **PEP 563** (i.e., "Postponed Evaluation of Annotations") support
    implemented in the :func:`beartype.beartype` decorator if the active Python
    interpreter targets at least Python 3.7.0 (i.e., the first major Python
    version to support PEP 563) *or* skip otherwise.
    '''

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype_test.unit.data.data_p563 import (
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
        stanza_index=33, player_name='Notch') == 'Notch. Player of games.'

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


#FIXME: Hilariously, we can't even unit test whether the
#beartype._decor._pep563._die_if_hint_repr_exceeds_child_limit() function
#behaves as expected. See commentary in the
#"beartype_test.unit.data.data_p563" submodule for all the appalling details.

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
#     from beartype_test.unit.data.data_p563 import player_was_love
#
#     # Assert @beartype raises the expected exception when decorating a
#     # callable violating this limit.
#     with raises(BeartypeDecorHintPepException):
#         beartype(player_was_love)
