.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document detailing installation instructions.

.. # ------------------( MAIN                                )------------------

#######
Install
#######

.. # FIXME: Non-ideal. Ideally, this should be fully refactored from the ground
.. # up to leverage React-style tabs implemented by the high-quality third-party
.. # "sphinx-design" extension, available here:
.. #     https://github.com/executablebooks/sphinx-design
.. #
.. # The idea here is that rather than enumerate all instructions as an
.. # iterative series of subsections, we instead isolate each platform-specific
.. # set of instructions to its own tab. The default tab displays "pip"
.. # instructions, of course. Users are then free to switch tabs to an alternate
.. # platform listing instructions for that platform. Score one for sanity.

Install beartype with pip_, because `PyPI <beartype PyPI_>`__ is the `cheese
shop <PyPI cheese shop_>`__ and you too enjoy a `fine Venezuelan beaver cheese
<cheese shop sketch_>`__ while mashing disconsolately on your keyboard late on
a rain-soaked Friday evening. Wherever expensive milk byproducts ferment,
beartype will be there.

.. code-block:: bash

   pip3 install beartype

Install beartype with Anaconda_, because package managers named after venomous
South American murder reptiles have finally inspired your team to embrace more
mammal-friendly packages. Your horoscope also reads: "Avoid reckless ecotourism
in places that rain alot."

.. code-block:: bash

   conda config --add channels conda-forge
   conda install beartype

`Commemorate this moment in time <Badge_>`__ with |bear-ified|, our
over\ *bear*\ ing project shield. What says quality like `a bear on a badge
<Badge_>`__, amirite?

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

********
Platform
********

Beartype is also installable with platform-specific package managers, because
sometimes you just need this thing to work.

macOS
#####

Let's install beartype with Homebrew_ on macOS_ courtesy `our third-party
tap <beartype Homebrew_>`__:

.. code-block:: bash

   brew install beartype/beartype/beartype

Let's install beartype with MacPorts_ on macOS_:

.. code-block:: bash

   sudo port install py-beartype

A big bear hug to `our official macOS package maintainer @harens <harens_>`__
for `packaging beartype for our Apple-appreciating audience <beartype
MacPorts_>`__.

Arch Linux
##########

Let's install beartype with ``pacman`` on `Arch Linux`_ – where beartype is now
`officially packaged <beartype Arch_>`__ in the `Arch User Repository (AUR)
<AUR_>`__ itself:

.. code-block:: bash

   git clone https://aur.archlinux.org/python-beartype.git
   cd python-beartype
   makepkg -si

Truly, Arch Linux has now seen the face of quality assurance. It looks like a
grizzled bear with patchy fur, one twitchy eye, and a gimpy leg that
spasmodically flails around.

Gentoo Linux
############

Let's install beartype with ``emerge`` on `Gentoo Linux`_ – where beartype is
now `officially packaged <beartype Gentoo_>`__ in the Portage tree itself:

.. code-block:: bash

   emerge beartype

Source-based Linux distributions are the CPU-bound nuclear option. *What could
be simpler?* O_o

*****
Badge
*****

If you're feeling the quality assurance and want to celebrate, consider
signaling that you're now publicly *bear-*\ ified:

  YummySoft is now |bear-ified|!

All this magic and possibly more can be yours with:

* **Markdown**:

  .. code-block:: md

     YummySoft is now [![bear-ified](https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg)](https://beartype.readthedocs.io)!

* **reStructuredText**:

  .. code-block:: rst

     YummySoft is now |bear-ified|!

     .. # See https://docutils.sourceforge.io/docs/ref/rst/directives.html#image
     .. |bear-ified| image:: https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg
        :align: top
        :target: https://beartype.readthedocs.io
        :alt: bear-ified

* **Raw HTML**:

  .. code-block:: html

     YummySoft is now <a href="https://beartype.readthedocs.io"><img
       src="https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg"
       alt="bear-ified"
       style="vertical-align: middle;"></a>!

Let a soothing pastel bear give your users the reassuring **OK** sign.
