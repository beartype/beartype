.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document detailing all public-facing APIs
.. # exposed by this project.

.. # ------------------( TODO                                )------------------
.. # FIXME: Document the new "beartype.peps" subpackage as well, please!

.. # ------------------( MAIN                                )------------------

##################################
Beartype API: It Bears Bookmarking
##################################

Beartype isn't just the :func:`beartype.beartype` decorator.

Beartype is a menagerie of public APIs for type-checking, introspecting, and
manipulating type hints at runtime – all accessible under the ``beartype``
package installed when you installed beartype. But all beartype documentation
begins with :func:`beartype.beartype`, just like all rivers run to the sea.
[#endorheic_basins]_

.. [#endorheic_basins]
   That's a lie, actually. Numerous river tributaries just pour out into
   deserts. Do `endorheic basins`_ mean nothing to you, beartype? Wikipedia:
   *the more you click, the less you know.*

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Project-wide tables of contents (TOCs). See also official documentation on
.. # the Sphinx-specific "toctree::" directive:
.. #     https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree

.. # Child TOC tree.
.. #
.. # Note that child documents *MUST* reside in the same subdirectory as this
.. # parent document. Although Sphinx locally supports child documents residing
.. # in a different subdirectory (e.g., "doc/srcapi/"), Sphinx remotely fails
.. # when this is the case under ReadTheDocs (RTD) with fatal warnings ala:
.. #     WARNING: toctree contains reference to nonexisting document "api/decor"
.. #
.. # See also this StackOverflow post, where the only valid solution is to
.. # flatten the Sphinx document structure as we have necessarily done:
.. #     https://stackoverflow.com/a/51283544/2809027

.. toctree::
   :hidden:
   :caption: Bear with Us

   Beartype Decorator <api_decor>
   Beartype Validators <api_vale>
   Beartype DOOR <api_door>
   Beartype Errors <api_roar>

.. #FIXME: Uncomment *AFTER* re-enabling "autoapi" support in "conf.py" and
.. #resolving outstanding issues with that support. *gulp*
.. # .. toctree::
.. #    :caption: Beartype API reference
.. #
.. #    API </api/beartype/index>
.. #
.. # Would You Like to Know More?
.. # ----------------------------
.. #
.. # * :ref:`genindex`
.. # * :ref:`modindex`
.. # * :ref:`search`

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------
