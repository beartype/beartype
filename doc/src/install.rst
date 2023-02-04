.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Root reStructuredText (reST) document transitively referencing all other
.. # child reST documents for this project.

.. # ------------------( MAIN                                )------------------

#######
Install
#######

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

Linux
#####

Let's install beartype with ``emerge`` on Gentoo_ courtesy `a third-party
overlay <beartype Gentoo_>`__, because source-based Linux distributions are the
CPU-bound nuclear option:

.. code-block:: bash

   emerge --ask app-eselect/eselect-repository
   mkdir -p /etc/portage/repos.conf
   eselect repository enable raiagent
   emerge --sync raiagent
   emerge beartype

*What could be simpler?* O_o

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
