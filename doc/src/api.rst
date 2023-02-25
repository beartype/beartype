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
   deserts. Do `endorheic basins`_ mean nothing to you, beartype?

   Wikipedia: *the more you click, the less you know.*

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Project-wide tables of contents (TOCs). See also official documentation on
.. # the Sphinx-specific "toctree::" directive:
.. #     https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree

.. # Child TOC tree.
.. toctree::
   :hidden:
   :caption: Bear with Us

   Beartype Decorator <api/decor>
   Beartype Validators <api/vale>
   Beartype DOOR <api/door>
   Beartype Errors <api/roar>

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
