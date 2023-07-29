.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------

========
Synopsis
========

This subpackage contains test modules exercising import hooks installed by the
:mod:`beartype.claw` API into a Python subprocess forked from the active Python
process (rather than directly into the active Python process) and thus
"extraprocess."
