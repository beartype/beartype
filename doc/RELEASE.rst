.. # ------------------( SYNOPSIS                           )------------------

=========
Releasing
=========

Stable releases are manually published with a rigorous procedure. The tl;dr is:

#. A stable commit is **tagged** with an annotated Git tag of the proper format
   expected by the automation triggered by...
#. That tag is **pushed** to GitHub_, which triggers the automated publication
   of both source tarballs and binary wheels of this stable commit in various
   popular formats to both GitHub_ itself and `PyPI`_ using the GitHub_ Actions
   CI/CD workflow configured by the ``.github/workflows/pythonrelease.yml``
   file. (\ *Phew!*\ )

While technically optional, this procedure reduces the likelihood of
installation and usage woes by downstream consumers (\ *e.g.,* end users,
package maintainers) and is thus effectively mandatory.

.. # ------------------( TABLE OF CONTENTS                  )------------------
.. # Blank line. By default, Docutils appears to only separate the subsequent
.. # table of contents heading from the prior paragraph by less than a single
.. # blank line, hampering this table's readability and aesthetic comeliness.

|

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Contents**
   :local:

.. # ------------------( DESCRIPTION                        )------------------

Procedure
============

beartype is releasable to all supported platforms as follows:

#. (\ *Optional*\ ) **Validate reStructuredText (reST) rendering.** The
   human-readable description for this release derives directly from `the
   top-level README.rst file <readme_>`__ for this project. Sadly, PyPI's reST
   renderer supports only a proper subset of the syntax supported by the reST
   standard – itself only a proper subset of the syntax supported by Sphinx. If
   `this file <readme_>`__ contains syntax unsupported by PyPI's reST renderer,
   PyPI erroneously preserves this file as plaintext rather than rendering this
   file as HTML. To avoid this:

   #. Install the ``collective.checkdocs`` Python package.

      .. code-block:: shell-session

         $ sudo pip3 install collective.checkdocs

   #. Validate the PyPI-specific compatilibility of `this file <readme_>`__.

      .. code-block:: shell-session

         $ python3 setup.py checkdocs

   #. After submitting this release to PyPI below, manually browse to `the
      PyPI-hosted page <PyPI beartype_>`__ for this project and verify by
      cursory inspection that this project's description is rendered as HTML.

#. (\ *Optional*\ ) **Install** wheel_, a third-party pure-Python package
   permitting this release to be packaged into a cross-platform pre-compiled
   binary distribution supported by both PyPI_ and ``pip``. This optional
   dependency augments setuptools with the ``bdist_wheel`` subcommand invoked
   below when locally testing the generation of binary wheels.

   .. code-block:: shell-session

      $ sudo pip3 install wheel

#. (\ *Optional*\ ) **Test packaging both a source tarball and binary wheel.**

   .. code-block:: shell-session

      $ python3 setup.py sdist bdist_wheel

#. (\ *Optional*\ ) **List the contents of this source tarball,** where
   ``${version}`` is the purely numeric version of this release (e.g.,
   ``0.4.1``). Verify by inspection that no unwanted paths were packaged.

   .. code-block:: shell-session

      $ tar -tvzf dist/beartype-${version}.tar.gz | less

#. (\ *Optional*\ ) **Test the local installation of this release.** If
   installation of this release differs from that of prior releases, testing
   *before* publishing this release to PyPI_ and elsewhere is advisable.

   #. **Test this source tarball locally.**

      #. **Create a new empty (venv)** (i.e., virtual environment).

         .. code-block:: shell-session

            $ python3 -m venv --clear /tmp/beartype-sdist

      #. **Install this source tarball into this venv.**\ [#venv]_

         .. code-block:: shell-session

            $ /tmp/beartype-sdist/bin/pip3 install wheel
            $ /tmp/beartype-sdist/bin/pip3 install dist/beartype-${version}.tar.gz

      #. **Test this release from this venv.**

         .. code-block:: shell-session

            $ cd /tmp && /tmp/beartype-sdist/bin/beartype try

      #. **Remove this venv and return to the prior directory.**

         .. code-block:: shell-session

            $ rm -rf /tmp/beartype-sdist && cd -

   #. **Test this binary wheel locally.**

      #. **Create a new empty venv.**

         .. code-block:: shell-session

            $ python3 -m venv --clear /tmp/beartype-wheel

      #. **Install this binary wheel into this venv.**\ [#venv]_

         .. code-block:: shell-session

            $ /tmp/beartype-wheel/bin/pip3 install \
              dist/beartype-${version}-py3-none-any.whl

      #. **Test this release from this venv.**

         .. code-block:: shell-session

            $ cd /tmp && /tmp/beartype-wheel/bin/beartype try

      #. **Remove this venv and sample simulation and return to the prior
         directory.**

         .. code-block:: shell-session

            $ rm -rf /tmp/beartype-wheel /tmp/sample_sim && cd -

#. (\ *Optional*\ ) **Bump release metadata.** Assuming the prior release
   followed these instructions, release metadata has already been bumped in
   preparation for the next (i.e., this) release. If another bump is required
   (e.g., to upgrade this release from a patch to a minor or even major
   update), this bump should be performed *before* tagging this release. For
   details, see the eponymous *"Bump release metadata."* instructions below.
#. (\ *Optional*\ ) **List all existing tags.** For reference, listing all
   previously created tags *before* creating new tags is often advisable.

   .. code-block:: shell-session

      $ git tag

#. **Create an announcement commit,** ideally as an **empty commit** (i.e.,
   commit containing only a message rather than both changes *and* a message).
   Empty announcements reduce the likelihood of introducing last-minute
   instability into an otherwise stable release. Of course, this assumes that
   the prior non-empty commit passed all continuous integration (CI) hosts.

   .. code-block:: shell-session

      $ git commit --allow-empty

   This commit should have a message whose:

   * First line is of the format ``"beartype {version} released."``, where
     ``{version}`` is the current value of the ``beartype.__version__`` global.
   * Remaining lines are a changelog synopsizing the significant changes
     implemented by this release -- ideally in GitHub-flavoured Markdown (GHFM)
     format, as depicted below. Note that this format requires enabling the
     ``[commit] cleanup = scissors`` setting in the ``~/.gitconfig`` file, as
     ``git`` otherwise treats lines prefixed by "#" characters (e.g., Markdown
     headers) in commit messages as ignorable comments to be removed.

   For example:

   .. code-block:: markdown

      beartype 0.0.1 released.

      Changes include:

      ## Compatibility Improved

      * **Python >= 3.9.0.** This release officially supports the first stable
        release of the Python 3.9.x series (i.e., Python 3.9.0).

      ## Compatibility Broken

      * **None.** This release preserves backward compatibility with the prior
        stable release.

      ## Dependencies Bumped

      * **`setuptools` >= 38.2.0,** just 'cause.

      ## Features Added

      * **Type library,** just 'cause.

      ## Features Improved

      * **`@beartype` performance,** just 'cause.

      ## Features Deprecated

      * **`@beartype.moar` submodule,** to be removed in `beartype` 0.1.0.

      ## Features Removed

      * **None.**

      ## Issues Resolved

      * **#3,** just 'cause.
      * **pypa/pip#6163,** just 'cause.

      ## Tests Improved

      * **GitLab CI + `tox`,** just 'cause.

      ## Documentation Revised

      * **Installation instructions,** just 'cause.

      ## API Changed

      * Renamed:
        * `beartype.roar` subpackage to `beartype.hoar`.
      * Added:
        * `beartype.soar` submodule.
      * Improved:
        * `beartype.lore` subpackage.
      * Removed:
        * `beartype._boar` submodule.

#. **Tag this commit.** An annotated tag\ [#tags]_ should be created whose:

   * Name is ``v{version}``, where ``{version}`` is the current value of the
     ``beartype.__version__`` global.
   * Message is the same commit message created above.

   .. code-block:: shell-session

      $ git tag -a v{version}

#. **Bump release metadata.** In preparation for developing the next release,
   the ``beartype.meta.VERSION`` global should be incremented according to
   the `best practices <Version Nomenclature_>`__ detailed below.

#. **Create another announcement commit.** This commit should have a message
   whose first line is of the format ``"beartype {version} started."``, where
   ``{version}`` is the new value of the ``beartype.__version__`` global.
   Since no changelog for this release yet exists, a single-line message
   suffices for this commit. For example::

       beartype 0.4.1 started.

#. **Push these commits and tags.** After doing so, GitHub will automatically
   publish source tarballs and binary wheels in various popular formats (e.g.,
   ``.zip``, ``.tar.bz2``) containing the contents of this repository at this
   tagged commit to this project's `GitHub releases page <tarballs_>`__ and
   `PyPI releases portal <PyPI beartype_>`__. No further work is required to
   distribute this release to *any* service – excluding third-party package
   managers (e.g., Anaconda_) and platforms (e.g., Linux distributions), which
   typically require manual intervention. **This release has now been
   officially distributed to GitHub and PyPI.**

   .. code-block:: shell-session

      $ git push && git push --tags

#. **Reinstall this package.** Doing so updates the setuptools-specific
   version associated with its internal installation of this package, ensuring
   that subsequent attempts to install downstream packages requiring this
   version (e.g., BETSE_, BETSEE_) will behave as expected.

   .. code-block:: shell-session

      $ pip3 install -e .

#. (\ *Optional*\ ) **Test the remote installation of this release.**

   #. **Test this release on** `Test PyPI`_. Note that, as this server is a
      moving target, the `official instructions <Test PyPI instructions_>`__
      *always* supersede those listed for convenience below.

      #. **Create a** `Test PyPI user`_.
      #. **Create a** ``~/.pypirc`` **dotfile,** ideally by following the
         `official instructions <Test PyPI instructions_>`__ for doing so.
      #. **Register this project with** `Test PyPI`_.

         .. code-block:: shell-session

            $ python3 setup.py register -r testpypi

      #. **Browse to this project on** `Test PyPI`_. Verify by inspection all
         identifying metadata at the following URL:

         https://testpypi.python.org/pypi/beartype

      #. **Upload this source tarball and binary wheel to** `Test PyPI`_.

         .. code-block:: shell-session

            $ twine upload -r testpypi dist/beartype-${version}*

      #. **Create a new empty venv.**

         .. code-block:: shell-session

            $ python3 -m venv --clear /tmp/beartype-pypi

      #. **Install this release into this venv.**\ [#venv]_

         .. code-block:: shell-session

            $ /tmp/beartype-pypi/bin/pip3 install \
              install -i https://testpypi.python.org/pypi beartype

      #. **Test this release from this venv.**

         .. code-block:: shell-session

            $ cd /tmp && /tmp/beartype-pypi/bin/beartype try

      #. **Remove this venv and sample simulation and return to the prior
         directory.**

         .. code-block:: shell-session

            $ rm -rf /tmp/beartype-pypi /tmp/sample_sim && cd -

#. (\ *Obsolete*\ ) **Manually publish this release to** `PyPI`_.
   
   .. note::
    
      The following instructions have been obsoleted by the GitHub_ Actions
      CI/CD workflow configured by the ``.github/workflows/pythonrelease.yml``
      file, which now automates publication of both source tarballs and binary
      wheels of this this stable release in various popular formats to both
      GitHub_ itself and `PyPI`_ when pushing the tag for this release above.

   #. **Create a** `PyPI user`_.
   #. **Validate the primary e-mail address associated with this account,**
      which `PyPI`_ requires as a hard prerequisite to performing the first
      upload (and hence creation) for this project.
   #. **Create a** ``~/.pypirc`` **dotfile,** ideally by following the
      `official instructions <Test PyPI instructions_>`__ for doing so.
   #. **Package both a source tarball and binary wheel.**

      .. code-block:: shell-session

         $ python3 setup.py sdist bdist_wheel

   #. **Upload this source tarball and binary wheel to** `PyPI`_. If this is
      the first such upload for this project, a `PyPI`_-hosted project page
      will be implicitly created by this upload. `PyPI` neither requires,
      recommends, nor supports end user intervention in this process.

      .. code-block:: shell-session

         $ twine upload dist/beartype-${version}*

   #. (\ *Optional*\ ) **Browse to this project on** `PyPI`_. Verify by
      inspection all identifying metadata at the following URL:

      https://pypi.python.org/pypi/beartype

   #. (\ *Optional*\ ) **Test the installation of this release from** `PyPI`_.

      #. **Create a new empty venv.**

         .. code-block:: shell-session

            $ python3 -m venv --clear /tmp/beartype-pypi

      #. **Install this release into this venv.**\ [#venv]_

         .. code-block:: shell-session

            $ /tmp/beartype-pypi/bin/pip3 install beartype

      #. **Test this release from this venv.**

         .. code-block:: shell-session

            $ cd /tmp && /tmp/beartype-pypi/bin/beartype try

      #. **Remove this venv and sample simulation and return to the prior
         directory.**

         .. code-block:: shell-session

            $ rm -rf /tmp/beartype-pypi /tmp/sample_sim && cd -

#. (\ *Optional*\ ) **Update third-party packages.** As of this writing, these
   include (in no particular order):

   * Our official `Anaconda package`_, automatically produced for all supported
     platforms from the `conda recipe`_ hosted at the `conda-forge feedstock`_
     maintained by the maintainer of beartype. Updating this package thus
     reduces to updating this recipe. To do so, avoid directly pushing to any
     branch (including ``master``) of the `feedstock repository`_, as doing so
     conflicts with `conda-forge`_ automation; instead (in order):

     #. Remotely create a `GitHub`_ account.
     #. Remotely login to this account.
     #. Remotely fork our `feedstock repository`_.
     #. Locally clone this forked feedstock repository.
     #. Locally create a new branch of this repository specific to this update.

        .. code-block:: shell-session

           $ git checkout -b beartype-${version}

     #. Locally update this recipe from this branch (typically, by editing the
        ``recipe/meta.yaml`` file). When doing so, note that:

        * The sha256 hash of the updated tarball *must* be manually embedded in
          this recipe. To obtain this hash remotely (in order):

          * Browse to `the PyPI-hosted page <PyPI beartype_>`__ for this project.
          * Click the *Download Files* link.
          * Click the *SHA256* link to the right of the updated tarball.
          * Paste the resulting string as the value of the ``sha256`` Jinja2
            templated variable in this recipe.

     #. Locally stage and commit these changes.

        .. code-block:: shell-session

           $ git commit --all

     #. Locally push these changes to the upstream fork.

        .. code-block:: shell-session

           $ git push --set-upstream origin beartype-v${version}

     #. Remotely open a pull request (PR) from the upstream fork against the
        `original repository <feedstock repository_>`__.

     See also the `conda-forge FAQ`_ entry `"Using a fork vs a branch when
     updating a recipe." <conda-forge update recipe_>`__

   * Our official `Gentoo Linux ebuild`_, currently hosted at the `raiagent
     overlay`_ maintained by the maintainer of beartype.

Thus begins the dawn of a new scientific epoch.

.. [#tags]
   Do *not* create a lightweight tag, which omits critical metadata (e.g.,
   author identity, descriptive message). *Always* create an annotated tag
   containing this metadata by explicitly passing the ``-a`` option to the
   ``git tag`` subcommand.
.. [#venv]
   Installing this release into a venv requires installing *all* mandatory
   dependencies of this release into this venv from either binary wheels or
   source tarballs. In either case, expect installation to consume non-trivial
   space and time. The cheese shop was not instantiated in a day.

Version Nomenclature
====================

This application should be **versioned** (i.e., assigned a new version)
according to the `Semantic Versioning`_ schema. Each version *must* consist of
three ``.``-delimited integers ``{major}.{minor}.{patch}``, where:

* ``{major}`` is the **major version,** incremented only when either:

  * **Breaking backward compatibility with existing simulation configurations.**
    The public API of this application is its configuration file format rather
    than the public subset of its codebase (e.g., public submodules or classes).
    No codebase change can be considered to break backward compatibility unless
    also changing the simulation configuration file format in a manner
    rendering existing files in the prior format unusable. Note that doing so
    is unequivocally bad and hence *much* discouraged.
  * **Implementing headline-worthy functionality** (e.g., a GUI). Technically,
    this condition breaks the `Semantic Versioning`_ schema, which stipulates
    that *only* changes breaking backward compatibility warrant major bumps.
    But this is the real world. In the real world, significant improvements
    are rewarded with significant version changes.

  In either case, the minor and patch versions both reset to 0.

* ``{minor}`` is the **minor version,** incremented only when implementing
  customary functionality in a manner preserving backward compatibility. In
  this case, only the patch version resets to 0.
* ``{patch}`` is the **patch version,** incremented only when correcting
  outstanding issues in a manner preserving backward compatibility.

When in doubt, bump only the minor version and reset only the patch version.

.. # ------------------( LINKS ~ beartype                   )------------------
.. _readme:
   https://github.com/beartype/beartype/blob/master/README.rst
.. _tarballs:
   https://github.com/beartype/beartype/releases
.. _PyPI beartype:
   https://pypi.python.org/pypi/beartype

.. # ------------------( LINKS ~ beartype : gentoo          )------------------
.. _Gentoo Linux ebuild:
   https://github.com/leycec/raiagent/tree/master/dev-python/beartype
.. _raiagent overlay:
   https://github.com/leycec/raiagent

.. # ------------------( LINKS ~ beartype : conda           )------------------
.. _Anaconda package:
   https://anaconda.org/conda-forge/beartype
.. _conda recipe:
   https://github.com/leycec/beartype-feedstock/blob/master/recipe/meta.yaml
.. _conda-forge feedstock:
.. _feedstock repository:
   https://github.com/leycec/beartype-feedstock

.. # ------------------( LINKS ~ py                         )------------------
.. _Semantic Versioning:
   http://semver.org
.. _twine:
   https://pypi.python.org/pypi/twine
.. _wheel:
   https://wheel.readthedocs.io

.. # ------------------( LINKS ~ py : conda                 )------------------
.. _conda-forge:
   https://conda-forge.org
.. _conda-forge FAQ:
   https://conda-forge.org/docs/conda-forge_gotchas.html
.. _conda-forge update recipe:
   https://conda-forge.org/docs/conda-forge_gotchas.html#using-a-fork-vs-a-branch-when-updating-a-recipe

.. # ------------------( LINKS ~ py : package               )------------------
.. _BETSE:
   https://gitlab.com/betse/betse
.. _BETSEE:
   https://gitlab.com/betse/betsee

.. # ------------------( LINKS ~ py : pypi                  )------------------
.. _Test PyPI:
   https://testpypi.python.org/pypi
.. _Test PyPI instructions:
   https://wiki.python.org/moin/TestPyPI
.. _Test PyPI user:
   https://testpypi.python.org/pypi?%3Aaction=register_form
.. _PyPI:
   https://pypi.python.org/pypi
.. _PyPI user:
   https://pypi.python.org/pypi?%3Aaction=register_form

.. # ------------------( LINKS ~ service                    )------------------
.. _GitHub:
   https://github.com
