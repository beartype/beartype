#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **conditional statement abstract syntax tree (AST) transformer mixin**
(i.e., low-level superclass transforming :pep:`484`-compliant
``if TYPE_CHECKING:`` blocks in modules hooked by :mod:`beartype.claw` import
hooks).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    If,
    Import,
    ImportFrom,
    Pass,
    copy_location,
)
from beartype.roar import BeartypeClawTypeCheckingWarning
from beartype.typing import (
    TYPE_CHECKING,
    Optional,
    Union,
)
from beartype._data.typing.datatyping import NodeVisitResult
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_15
from warnings import warn

if TYPE_CHECKING:
    from beartype.claw._ast._scope.clawastscopes import BeartypeNodeScopes

# ....................{ PRIVATE ~ globals                  }....................
_TYPE_CHECKING_NAME = 'TYPE_CHECKING'
'''
Unqualified basename of the :pep:`484`-compliant ``TYPE_CHECKING`` global.
'''

# ....................{ CLASSES                            }....................
class BeartypeNodeTransformerIfMixin(object):
    '''
    Beartype **conditional statement AST transformer mixin** (i.e., visitor
    pattern detecting :pep:`484`-compliant ``if TYPE_CHECKING:`` blocks
    containing imports, which are runtime-hostile, as the ``TYPE_CHECKING``
    global is :data:`False` at runtime and those imports thus never occur).

    Under Python >= 3.15, this mixin transparently hoists those imports out of
    those blocks as equivalent :pep:`810`-compliant ``lazy`` imports, which both
    preserve the laziness intended by the author *and* are visible at runtime.
    Under older Python versions, no equivalent exists. This mixin instead issues
    a non-fatal warning advising the author how to refactor those imports.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Squelch false negatives from mypy. This is absurd. This is mypy.
    if TYPE_CHECKING:
        _module_name: str
        _scopes: 'BeartypeNodeScopes'

    # ..................{ VISITORS                           }..................
    def visit_If(self, node: If) -> NodeVisitResult:
        '''
        Transform the passed **conditional node** (i.e., node encapsulating an
        ``if`` statement) if this statement is an ``if TYPE_CHECKING:`` block
        containing one or more imports *or* preserve this node as is otherwise.

        Parameters
        ----------
        node : If
            Conditional node to be transformed.

        Returns
        -------
        NodeVisitResult
            Either:

            * If this node is such a block, the list of one or more nodes
              hoisting those imports as lazy imports followed by this node
              (minus those imports) if this node still has statements to run.
            * Else, this node as is.
        '''

        # List of all imports that are directly children of this block if this
        # is a "TYPE_CHECKING" block *OR* the empty list otherwise.
        imports = (
            [
                child for child in node.body
                if isinstance(child, (Import, ImportFrom))
            ]
            if _is_node_type_checking(node.test) else
            []
        )

        # If this is *NOT* a "TYPE_CHECKING" block containing imports, defer to
        # the superclass visitor method, recursively visiting child nodes.
        if not imports:
            return self.generic_visit(node)  # type: ignore[attr-defined]
        # Else, this is a "TYPE_CHECKING" block containing imports.

        # List of all imports that are lazily importable (i.e., excluding star
        # imports, which cannot be lazy).
        imports_lazy = [
            child for child in imports
            if not (
                isinstance(child, ImportFrom) and
                any(alias_node.name == '*' for alias_node in child.names)
            )
        ]

        # If the active Python interpreter targets Python >= 3.15, this node
        # resides in module scope (in which lazy imports are permitted), *AND*
        # one or more imports are lazily importable...
        if (
            IS_PYTHON_AT_LEAST_3_15 and
            self._scopes.is_scope_module and
            imports_lazy
        ):
            # Mark each such import as lazy.
            for import_node in imports_lazy:
                import_node.is_lazy = 1  # type: ignore[union-attr]

            # Set of the identifiers of these imports, for efficient removal.
            imports_lazy_ids = {id(import_node) for import_node in imports_lazy}

            # Remove these imports from the body of this block, which would
            # otherwise be left empty.
            node.body = [
                child for child in node.body
                if id(child) not in imports_lazy_ids
            ]

            # If this block is now empty of both statements and an "else"
            # branch, this block is entirely replaceable by these imports.
            nodes_new: list[AST] = list(imports_lazy)
            if node.body or node.orelse:
                # Preserve the remainder of this block, ensuring a non-empty
                # body. Note this block still runs only at type-checking time.
                if not node.body:
                    node.body = [copy_location(Pass(), node)]
                nodes_new.append(self.generic_visit(node))  # type: ignore[attr-defined]

            # Return these nodes in place of this block.
            return nodes_new  # type: ignore[return-value]
        # Else, lazy imports are unavailable or inapplicable.

        # Issue a non-fatal warning advising the author how to refactor.
        warn(
            BeartypeClawTypeCheckingWarning(
                f'Module "{self._module_name}" line {node.lineno} imports '
                f'type hints in an "if TYPE_CHECKING:" block, which is '
                f'runtime-hostile (because "TYPE_CHECKING" is "False" at '
                f'runtime and those imports thus never occur). '
                f'Packages willing to require Python >= 3.15 should refactor '
                f'those imports into PEP 810-style lazy imports (e.g., '
                f'"lazy from typing import Literal"). '
                f'Packages refusing to require Python >= 3.15 should instead '
                f'refactor those imports into PEP 484-style stringified '
                f'absolute forward references (e.g., '
                f'"Literal = \'typing.Literal\'").'
            ),
            stacklevel=2,
        )

        # Preserve this block as is.
        return self.generic_visit(node)  # type: ignore[attr-defined]

# ....................{ PRIVATE ~ testers                  }....................
def _is_node_type_checking(node: AST) -> bool:
    '''
    :data:`True` only if the passed expression node is the :pep:`484`-compliant
    ``TYPE_CHECKING`` global, either unqualified (e.g., ``TYPE_CHECKING``) or
    qualified by a module alias (e.g., ``typing.TYPE_CHECKING``).
    '''
    from ast import Attribute, Name

    return (
        (isinstance(node, Name) and node.id == _TYPE_CHECKING_NAME) or
        (isinstance(node, Attribute) and node.attr == _TYPE_CHECKING_NAME)
    )
