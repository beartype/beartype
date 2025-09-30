#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook decorator-hostile intraprocess unit tests** (i.e.,
exercising edge cases of :mod:`beartype.claw` import hooks unique to
**decorator-hostile decorators** (i.e., decorators hostile to other decorators
by prohibiting other decorators from being applied after they are applied in a
chain of one or more decorators) within the active Python process).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: Isolate each unit test defined below to its own subprocess. Why?
# Module imports. Since each unit test defined below tends to reimport the same
# (or, at least, similar) modules as previously run unit tests defined below,
# module imports and thus unit tests *MUST* be isolated to their own
# subprocesses to ensure these tests may be run in any arbitrary order.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest

# ....................{ TESTS                              }....................
@pytest.mark.run_in_subprocess
def test_claw_intraprocess_decorator_hostile() -> None:
    '''
    Test the :mod:`beartype.claw.beartype_package` import hook against a single
    data subpackage in this test suite exercising *all* edge cases associated
    with this import hook unique to **decorator-hostile decorators** (i.e.,
    decorators hostile to other decorators by prohibiting other decorators from
    being applied after they are applied in a chain of one or more decorators).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.claw import beartype_package
    from beartype.claw._clawstate import (
        claw_lock,
        claw_state,
    )
    from beartype.roar import BeartypeDecorWrappeeException
    from beartype._conf.decorplace.confplacetrie import (
        BeartypeDecorPlacePackagesTrie,
        BeartypeDecorPlacePackageTrie,
    )
    from beartype._data.conf import dataconfplace
    from beartype_test.a00_unit.data.func.data_decor import decorator_hostile
    from pytest import raises

    # ....................{ MONKEY-PATCH                   }....................
    #FIXME: *TRASH.* This is crude, unsafe, and frankly dumb. Instead, we should
    #just define a new "BeartypeConf" recognizing this testing-specific
    #decorator-hostile decorator as such. Sadly, "BeartypeConf" currently fails
    #to provide an option enabling this. *sigh*

    # Monkey-patch this testing-specific decorator-hostile decorator into this
    # decorator-hostile decorator attribute name trie. *ALL* other
    # decorator-hostile decorators are defined by third-party packages and thus
    # unsuitable for general-purpose unit testing.
    #
    # Note that this monkey-patch is intentionally isolated to this
    # test-specific subprocess and thus implicitly safe.
    dataconfplace.DECOR_HOSTILE_ATTR_NAME_TRIE |= (
        BeartypeDecorPlacePackagesTrie({
            'beartype_test': BeartypeDecorPlacePackageTrie({
                'a00_unit': BeartypeDecorPlacePackageTrie({
                    'data': BeartypeDecorPlacePackageTrie({
                        'func': BeartypeDecorPlacePackageTrie({
                            'data_decor': BeartypeDecorPlacePackageTrie({
                                'decorator_hostile': None,
                            })
                        })
                    })
                })
            })
        })
    )
    # print(dataconfplace.DECOR_HOSTILE_ATTR_NAME_TRIE)

    # With a submodule-specific thread-safe reentrant lock, reset our import
    # hook state back to its initial defaults to respect the above monkey-patch.
    with claw_lock:
        claw_state.reinit()

    # ....................{ PREAMBLE                       }....................
    # Validate that the decorator-hostile decorator leveraged by the package
    # hooked below is a decorator-hostile decorator *BEFORE* importing from that
    # package. Since the @beartype decorator is permissive by both design and
    # necessity, defining decorator-hostile decorators unsupported by the
    # @beartype decorator is surprisingly non-trivial. Prove we actually did so.
    with raises(BeartypeDecorWrappeeException):
        @beartype
        @decorator_hostile
        def even_now_while_Saturn() -> None:
            '''
            Arbitrary callable decorated by a decorator-hostile decorator.
            '''

            pass

    # ....................{ LOCALS                         }....................
    # Name of the single package defining submodules defining callables and
    # types decorated by one or more decorator-hostile decorators to be subject
    # to beartype import hooks below.
    PACKAGE_NAME = (
        'beartype_test.a00_unit.data.claw.intraprocess.hookable_package.decor_hostile')

    # ....................{ PASS                           }....................
    # Explicitly subject this single package to a beartype import hook
    # configured by the default beartype configuration.
    beartype_package(PACKAGE_NAME)

    #FIXME: Uncomment after this actually works, please. *sigh*
    # Import the package hooked above, which then imports all submodules of that
    # package, exercising that these submodules are transitively subject to that
    # import hook.
    from beartype_test.a00_unit.data.claw.intraprocess.hookable_package import (
        decor_hostile)
