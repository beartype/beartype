#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide functional beartype-in-Sphinx tests.**

This submodule functionally tests the :func:`beartype.beartype` decorator to
conditionally reduce to a noop when the active Python interpreter is building
documentation for the third-party :mod:`sphinx` package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import (
    skip,
    skip_unless_package,
)

# ....................{ TESTS                              }....................
#FIXME: Reenable this once we resolve how to actually do so. Currently, the
#make_app() call below is failing with a low-level exception raised from the
#third-party "autoapi" Sphinx extension, seemingly due to a deprecation:
#    sphinx.errors.ExtensionError: Handler <function run_autoapi at 0x7f82568552d0> for event 'builder-inited' threw an exception (exception: The 'Module.doc' attribute is deprecated, use 'Module.doc_node' instead.)
#FIXME: For the benefit of the community, externally document how to do this
#for others at this open issue:
#    https://github.com/sphinx-doc/sphinx/issues/7008
#Note the trivial "conftest" submodule in this directory. Since this is all
#surprisingly easy, a simple comment describing this should easily suffice.
@skip('Currently broken by Sphinx "autoapi" deprecations.')
@skip_unless_package('sphinx')
def test_sphinx_build(make_app, tmp_path) -> None:
    '''
    Functional test validating that the third-party :mod:`sphinx` package
    successfully builds documentation for this project (i.e., residing in the
    top-level ``doc/`` subdirectory).

    To do so, this test externally runs the ``sphinx-build`` command against
    our ``doc/source/` Sphinx document tree.

    Parameters
    ----------
    make_app : sphinx.testing.util.SphinxTestApp
        Factory fixture creating and returning a :mod:`pytest`-friendly Sphinx
        object encapsulating the process of running the ``sphinx-build``
        command with the passed parameters.
    tmp_path : pathlib.Path
        Abstract path encapsulating a temporary directory unique to this unit
        test, created in the base temporary directory.
    '''

    # Defer test-specific imports.
    from beartype_test._util.path.pytpathmain import get_main_sphinx_source_dir
    from sphinx.testing.path import path

    #FIXME: Pass "parallel=CPUS_LEN" as well, where "CPUS_LEN" is the number of
    #CPU cores available to the active Python interpreter. We can't be bothered
    #to decide how to query that at the moment. It's probably trivial. *shrug*

    # "pytest"-friendly Sphinx object encapsulating the process of running the
    # "sphinx-build" command with the passed parameters. For reproducibility,
    # emulate the options passed to the root "sphinx" script locally building
    # this project's documentation as much as allowed by this API.
    sphinx_build = make_app(
        buildername='html',
        srcdir=str(get_main_sphinx_source_dir()),
        # "sphinx.testing"-specific path object encapsulating the absolute or
        # relative dirname of a test-specific temporary directory to which
        # Sphinx will emit ignorable rendered documentation files.
        #
        # Yes, this is *INSANE.* Sphinx should *ABSOLUTELY* be leveraging the
        # portable and standard "pathlib.Path" class rather than attempting to
        # roll its own non-standard (and thus probably non-portable) class.
        builddir=path(str(tmp_path)),
        # Instruct Sphinx to cache as little as possible.
        freshenv=True,
    )

    #FIXME: Re-enable this once Sphinx no longer emits warnings. Currently, the
    #third-party "autoapi" extension is emitting a consider number of warnings.
    # # Instruct Sphinx to raise a fatal exception rather than emitting a
    # # non-fatal warning on the first warning (identical to the "-W" option).
    # sphinx_build.warningiserror = True

    # Assert that building this project's documentation succeeds *WITHOUT*
    # raising any exceptions or emitting any warnings.
    sphinx_build.build()
