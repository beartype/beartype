.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Root reStructuredText (reST) document transitively referencing all other
.. # child reST documents for this project.
.. #
.. # ------------------( SEO                                 )------------------
.. # Metadata converted into HTML-specific meta tags parsed by search engines.
.. # Note that:
.. # * The "description" should be no more than 300 characters and ideally no
.. #   more than 150 characters, as search engines may silently truncate this
.. #   description to 150 characters in edge cases.

.. meta::
   :description lang=en:
     Beartype is an open-source pure-Python PEP-compliant constant-time runtime
     type checker emphasizing efficiency and portability.

.. # ------------------( MAIN                                )------------------

=================
|beartype-banner|
=================

.. parsed-literal::

   Look for the bare necessities,
     the simple bare necessities.
   Forget about your worries and your strife.

                           — `The Jungle Book`_.

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Project-wide tables of contents (TOCs). See also official documentation on
.. # the Sphinx-specific "toctree::" directive:
.. #     https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree

Let's Type This
---------------

.. # Leading TOC entry self-referentially referring back to this document,
.. # enabling users to trivially navigate back to this document from elsewhere.
.. #
.. # Note that the ":hidden:" option adds this entry to the TOC sidebar while
.. # omitting this entry from the TOC displayed inline in this document. This is
.. # sensible; since any user currently viewing this document has *NO* need to
.. #  navigate to the current document, the inline TOC omits this entry.
.. toctree::
   :hidden:
   :caption: Contents

   Bear with Us <self>

.. # FIXME: Obsolete, but momentarily preserved for reference.
.. # .. toctree::
.. #    :hidden:
.. #    :caption: Package
.. #
.. #    changes
.. #    reference
.. #
.. # .. toctree::
.. #    :hidden:
.. #    :caption: Guide
.. # 
.. #    tutorial

.. toctree::
   :caption: Beartype API reference

   API </api/beartype/index>

Would You Like to Know More?
----------------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
