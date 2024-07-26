#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural
collections abstract base class (ABC) type hint inferrers** (i.e., high-level
functions dynamically inferring standard :mod:`collections.abc` protocols that
best describe arbitrary classes satisfying those protocols).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
    Set,
    Union,
)
from beartype._data.kind.datakinddict import DICT_EMPTY
from beartype._data.hint.datahinttyping import (
    FrozenSetStrs,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.utilobject import get_object_methods_name_to_value_explicit

# ....................{ INFERERS                           }....................
#FIXME: Unit test us up, please.
@callable_cached
def infer_hint_type_collections_abc(cls: type) -> Optional[object]:
    '''
    Narrowest **collections protocol** (i.e., abstract base class published by
    the :mod:`collections.abc` subpackage) validating the passed class if at
    least one collections protocol validates this class *or* :data:`None`
    otherwise (i.e., if *no* collections protocol validates this class).

    This function returns the narrowest collections protocol, defined such that:

    * The passed class is a **virtual subclass** of (i.e., defines all methods
      required by) this protocol.
    * This protocol is **maximally narrow.** Formally:

      * The passed class is a virtual subclass of *no* other collections
        protocols that are themselves virtual subclasses of this protocol.
      * Equivalently, this protocol is **larger** (i.e., defines more abstract
        methods) than all other collections protocols that the passed class is
        also a virtual subclass of.

    This function does *not* return a type hint annotating the passed class.
    This function merely returns a subscriptable type hint factory suitable for
    the caller to subscript with a child type hint, which then produces the
    desired type hint annotating the passed class. Why this indirection? In a
    word: efficiency. If this function recursively inferred and returned a full
    type hint, this function would need to guard against infinite recursion by
    accepting the ``__beartype_obj_ids_seen__`` parameter also accepted by the
    parent :func:`beartype.door._func.infer.infermain.infer_hint` function;
    doing so would prevent memoization, substantially reducing efficiency.

    This function is memoized for efficiency.

    Design
    ------
    This function efficiently infers the narrowest :mod:`collections.abc` ABC
    applicable to the passed object by introspecting the set of all **dunder
    methods** (i.e., methods whose names are both prefixed and suffixed by the
    double-underscore substring ``"__"``). To do so, this function internally
    performs a graph theoretic traversal over a finite state machine (FSM)
    whose nodes are the set of all :mod:`collections.abc` ABCs and transitions
    between those nodes the dunder method names required by those ABCs. For
    example, given a passed object defining only the standard
    ``__contains__()``, ``__iter__()``, and ``__len__()`` dunder methods, this
    function (in order):

    #. Transitions from the start node of this FSM along the ``__contains__()``
       edge of this FSM to the corresponding :class:`collections.abc.Container`
       node.
    #. Transitions from that node along the grouped ``{__iter__(), __len__()}``
       edge of this FSM to the corresponding :class:`collections.abc.Collection`
       node.
    #. Halts there, thus inferring the type hint factory validating the passed
       object to be the :class:`collections.abc.Collection` ABC.

    Caveats
    -------
    This function exhibits:

    * **Best-case constant time complexity** :math:`O(n)` where ``n`` is the
      number of attributes bound to the passed class, which occurs when the
      passed class satisfies *no* :mod:`collections.abc` ABC.
    * **Average-case linear time complexity** :math:`O(n + k)` where ``n`` is the
      number of attributes bound to the passed class and ``k`` is the number of
      :mod:`collections.abc` ABCs subclassing the
      :class:`collections.abc.Container` superclass, which occurs when the
      passed class is that of a **standard container** (i.e., satisfies at least
      the root :class:`collections.abc.Container` ABC).
    * **Worst-case quadratic time complexity** :math:`O(n + jk)` where ``n`` is
      the number of attributes bound to the passed class, ``j`` is the number of
      :mod:`collections.abc` ABC superclasses (i.e., ABCs at the root of a
      hierarchy of ABCs), and ``k`` is the largest number of
      :mod:`collections.abc` ABCs subclassing such a superclass, which occurs
      when the passed class satisfies only an uncommon :mod:`collections.abc`
      ABC superclass.

    Parameters
    ----------
    obj : object
        Class to be introspected.

    Returns
    -------
    Optional[object]
        Either:

        * If at least one :mod:`collections.abc` protocol validates this class,
          the narrowest such protocol.
        * Else, :data:`None`.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'

    # ....................{ PREAMBLE                       }....................
    # List of the names of all attributes bound to this class.
    cls_attr_names = dir(cls)

    # If the intersection of the set of the names of all attributes bound to
    # this class with the set of the names of all requisite methods (i.e.,
    # methods required to transition from the start node to a transitional node)
    # is the empty set, then this class fails to define *ANY* methods required
    # by a "collections.abc" ABC. In this case, silently reduce to a noop.
    if not (set(cls_attr_names) & _START_NODE_TRANSITION_METHOD_NAMES):
        return None
    # Else, this intersection is non-empty. In this case, this class defines at
    # least one attribute whose name is that of a method required by a
    # "collections.abc" ABC.
    #
    # Note that this does *NOT* necessarily imply that this class defines at
    # least one such method. Clearly, an instance variable of the same name is
    # *NOT* a method: e.g.,
    #     # This class does *NOT* satisfy the "collections.abc.Sized" protocol
    #     # despite defining the "__sized__" attribute, as that attribute is
    #     # *NOT* a method.
    #     class FakeSized(object):
    #         __sized__: int
    #
    # Further detection is warranted to disambiguate this edge case.

    # ....................{ LOCALS                         }....................
    # Dictionary mapping from the names of all methods of the passed class to
    # those methods.
    cls_methods_name_to_method = get_object_methods_name_to_value_explicit(
        obj=cls, obj_dir=cls_attr_names)

    # Set of the names of all methods bound to this class.
    cls_method_names = cls_methods_name_to_method.keys()

    # Finite state machine (FSM) node currently visited by the search below.
    node_curr = _START_NODE

    # Finite state machine (FSM) node to be visited next by the search below if
    # any *OR* "None" if this is the last iteration of this search.
    node_next: Optional[_FiniteStateMachineNode] = None

    # ....................{ SEARCH                         }....................
    # print(f'Inferring {repr(cls)} "collections.abc" protocol...')

    # While some FSM node is still being visited by this search...
    while True:
        # print(f'Visiting FSM node {repr(node_curr.hint_factory)}...')

        #FIXME: *HEH.* Totally busted, sadly. Why? Because the root "object"
        #superclass defines an absurd number of dunder methods (e.g.,
        #__hash__(), __eq__()), which then guarantees this intersection to
        #almost always be non-empty -- especially when testing containers.
        #
        #Please resolve this by improving the
        #get_object_methods_name_to_value_explicit() getter defined above to
        #omit all "object" slot wrappers, which we already did and just need to
        #restore. Thankfully, this is only an optimization. Still, I sigh.

        # If the intersection of the set of the names of all methods bound to
        # this class with the set of the names of any methods required by one or
        # more "collections.abc" ABCs reachable from the current FSM node is
        # empty, no further FSM transitions can be made. In this case, the
        # current "collections.abc" ABC validating this class is the narrowest
        # such ABC. Halt searching and return this ABC.
        if not (cls_method_names & node_curr.nodes_next_method_names):
            break
        # Else, this intersetion is non-empty. In this case, at least one FSM
        # transition can be made. In this case, the current "collections.abc"
        # ABC validating this class is *NOT* the narrowest such ABC. Continue
        # searching for the narrowest such ABC.

        # For the string or frozen set of all transition methods *AND* FSM nodes
        # to which those methods transition...
        for node_next_method_names, node_next_possible in (
            node_curr.nodes_next.items()):
            # print(f'Considering transitioning to FSM node {repr(node_next_possible.hint_factory)}...')

            # If this transition method name(s) is a string...
            if node_next_method_names.__class__ is str:
                # If this class defines a method with this name, this class
                # satisfies this target "collections.abc" ABC. In this case...
                if node_next_method_names in cls_method_names:
                    # Set the next FSM node to this node.
                    node_next = node_next_possible
                    # print(f'Transitioning to FSM node {repr(node_next.hint_factory)}...')

                    # Halt this inner iteration.
                    break
            # Else, this transition method name(s) is a frozen set of strings.
            # In this case...
            else:
                # print(f'Set intersection: {node_next_method_names & cls_method_names}...')
                # print(f'Expected set: {node_next_method_names}...')

                # If the intersection of the set of the names of all methods
                # bound to this class with this frozen set of the names of all
                # methods required by this protocol is exactly this frozen set,
                # then this class defines *ALL* methods in this set and thus
                # satisfies this target "collections.abc" ABC. In this case...
                if (
                    len(node_next_method_names & cls_method_names) ==
                    len(node_next_method_names)
                ):
                    # Set the next FSM node to this node.
                    node_next = node_next_possible
                    # print(f'Transitioning to FSM node {repr(node_next.hint_factory)}...')

                    # Halt this inner iteration.
                    break

        # If transitioning to *NO* next FSM node, halt iteration.
        if not node_next:
            break
        # Else, a next FSM node is being transitioned to.

        # Transition from the current to the next FSM node.
        node_curr = node_next

        # Nullify the next FSM node for safety.
        node_next = None

    # Narrowest "collections.abc" ABC validating this class if any *OR* "None".
    hint_factory = node_curr.hint_factory
    # hint_factory = node_curr.hint_factory if node_curr else None

    # Return this object.
    return hint_factory

# ....................{ PRIVATE ~ hints                    }....................
_FiniteStateMachine = Dict[
    Union[str, FrozenSetStrs], '_FiniteStateMachineNode']
'''
PEP-compliant type hint matching a :mod:`collections.abc` **fine state machine
(FSM)** as a dictionary whose:

* Keys describe the **transitions** (i.e., directed edges transitioning from one
  node to another) of this FSM. For both efficiency and flexibility, each
  transition is permitted to be either:

  * The name of a single **dunder method** (e.g., ``"__contains__"``). If the
    object passed to the :func:`.infer_hint_type_collections_abc` function defines this
    method, then this FSM transitions to the **node** (i.e.,
    :class:`._FiniteStateMachineNode` instance) given by the value associated with
    this key in this dictionary.
  * A frozen set containing the names of two or more **dunder methods** (e.g.,
    ``frozenset({"__iter__", "__len__"})``). If the object passed to the
    :func:`.infer_hint_type_collections_abc` function defines *all* of these methods,
    then this FSM performs a similar transition as in the prior case.

* Values describe the **nodes** (i.e., :class:`._FiniteStateMachineNode`
  instances) of this FSM to follow these transitions to.
'''

# ....................{ PRIVATE ~ classes                  }....................
class _FiniteStateMachineNode(object):
    '''
    :mod:`collections.abc` **finite state machine (FSM) node** (i.e., node of a
    FSM whose transitions infer the narrowest :mod:`collections.abc` ABC
    applicable to the class passed to the
    :func:`.infer_hint_type_collections_abc` function).

    Parameters
    ----------
    hint_factory : object
        Either:

        * If this is the **start node** of this FSM, :data:`None`. The start
          node is *only* a convenient abstraction defining the initial
          transitions to actual nodes containing meaningful content.
        * Else, the type hint factory validating the passed object (e.g.,
          :class:`collections.abc.Container` if that object is a container).
    nodes_next_method_names : FrozenSet[str]
        Frozen set of the names of all **transition methods** (i.e., one or more
        methods required to be defined by the passed object for this FSM to
        transition from this node to another node). This frozen set is a
        non-negligible optimization enabling this FSM to exhibit non-amortized
        best-case constant :math:`O(1)` time complexity. Why? Because, in the
        best case, the :func:`.infer_hint_type_collections_abc` function is
        passed an object whose type defines *no* methods in this frozen set and
        thus immediately reduces to a noop.
    nodes_next : _FiniteStateMachine
        Either:

        * If this is a **stop node** of this FSM, the empty dictionary.
        * Else, this is a **transitionary node** of this FSM. In this case, this
          is the **transitionary FSM** (i.e., proper subset of the full FSM,
          mapping the transitions directed out of this node to the neighbouring
          nodes those transitions transition to) of this node.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize this slots list with the implementations of:
    # * The __new__() dunder method.
    # CAUTION: Subclasses declaring uniquely subclass-specific instance
    # variables *MUST* additionally slot those variables. Subclasses violating
    # this constraint will be usable but unslotted, which defeats our purposes.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'hint_factory',
        'nodes_next_method_names',
        'nodes_next',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        hint_factory: object
        nodes_next_method_names: FrozenSetStrs
        nodes_next: _FiniteStateMachine

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Optional parameters.
        hint_factory: object = None,
        nodes_next: _FiniteStateMachine = DICT_EMPTY,
    ) -> None:
        '''

        Parameters
        ----------
        hint_factory: object
            Either:

            * If this is the **start node** of this FSM, :data:`None`. The start
              node is *only* a convenient abstraction defining the initial
              transitions to actual nodes containing meaningful content.
            * Else, the type hint factory validating the passed object (e.g.,
              :class:`collections.abc.Container` if that object is a container).

            Defaults to :data:`None`.
        finite_state_machine: _FiniteStateMachine
            Either:

            * If this is a **stop node** of this FSM, the empty dictionary.
            * Else, the proper subset of the full FSM mapping the transitions
              directed out of this node to the neighbouring nodes those
              transitions transition to.

            Defaults to the empty dictionary.
        '''
        assert isinstance(nodes_next, dict), (
            f'{repr(nodes_next)} not dictionary.')

        # Classify all passed parameters.
        self.hint_factory = hint_factory
        self.nodes_next = nodes_next

        # Frozen set of the names of all transition methods, initialized to the
        # empty set.
        nodes_next_method_names: Set[str] = set()

        # For the string or frozen set of all transition methods *AND* FSM nodes
        # to which those methods transition...
        for node_next_method_names, node_next in nodes_next.items():
            # Validate the types of this key-value pair.
            assert isinstance(
                node_next_method_names, _NODE_TRANSITION_KEY_TYPES), (
                f'{repr(node_next_method_names)} neither string nor frozen set.')
            assert isinstance(node_next, _FiniteStateMachineNode), (
                f'{repr(node_next)} not "_FiniteStateMachineNode".')

            # If this transition method name(s) is a string, add this name to
            # this set.
            if node_next_method_names.__class__ is str:
                nodes_next_method_names.add(node_next_method_names)  # type: ignore[arg-type]
            # Else, this transition method name(s) is a frozen set of strings.
            # In this case, update this set with this names.
            else:
                nodes_next_method_names.update(node_next_method_names)

        # Classify this set as a frozen set for safety.
        self.nodes_next_method_names = frozenset(nodes_next_method_names)

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:
        '''
        Machine-readable representation of this finite state machine (FSM) node.
        '''

        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    hint_factory={repr(self.hint_factory)},',
            f'    nodes_next_method_names={repr(self.nodes_next_method_names)},',
            f'    nodes_next={repr(self.nodes_next)},',
            f')',
        ))

# ....................{ PRIVATE ~ globals                  }....................
_NODE_TRANSITION_KEY_TYPES = (str, frozenset)
'''
**Transition methods type tuple** (i.e., tuple of the types of all keys of the
``nodes_next`` parameter accepted by the
:meth:`_FiniteStateMachineNode.__init__` method).
'''


# Initialized below by the _init() function.
_START_NODE: _FiniteStateMachineNode = None  # type: ignore[assignment]
'''
:mod:`collections.abc` **finite state machine (FSM)**.

See Also
--------
:data:`._FiniteStateMachine`
    Further details.
'''


# Initialized below by the _init() function.
_START_NODE_TRANSITION_METHOD_NAMES: FrozenSetStrs = None  # type: ignore[assignment]
'''
Frozen set of the names of all **requisite start methods** (i.e., methods
required to transition from the start node to a transitional node).

If the class passed to the :func:`.infer_hint_type_collections_abc` function
does *not* define at least one method in this set, then that class satisfies
*no* :mod:`collections.abc` ABC. This set enables that function to exhibit
best-case constant time complexity :math:`O(n)`, where ``n`` is the number of
attributes bound to that class.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer function-specific imports.
    from beartype.typing import (
        AsyncGenerator,
        AsyncIterable,
        AsyncIterator,
        Awaitable,
        Collection,
        Container,
        Coroutine,
        Generator,
        Iterable,
        Iterator,
        Mapping,
        MutableMapping,
        MutableSequence,
        MutableSet,
        Reversible,
        Sequence,
        Sized,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12

    # ....................{ LOCALS                         }....................
    # Dictionary mapping the transitions directed out of the start node of this
    # finite state machine (FSM) to the neighbouring nodes of those transitions.
    # Note that:
    # * A "collections.abc.ByteString" FSM is intentionally *NOT* defined. Why?
    #   Because the "collections.abc.ByteString" protocol has been deprecated as
    #   of Python >= 3.12 and scheduled for removal under Python 3.14.
    # * A "collections.abc.Callable" FSM is intentionally *NOT* defined. Why?
    #   Because the sibling "_infercallable" submodule already deeply infers
    #   callable type hints for arbitrary objects satisfying the
    #   "collections.abc.Callable" protocol in a *MUCH* more intelligent manner.
    # * A "collections.abc.Hashable" FSM is intentionally *NOT* defined. Why?
    #   Because the root "object" superclass defines the __hash__() method to
    #   return the integer uniquely identifying the current object. Almost all
    #   classes thus trivially satisfy the "collections.abc.Hashable" protocol.
    #   The only exception are mutable classes redefining the "__hash__"
    #   attribute as class variables set to "None". Since the majority of
    #   classes still trivially satisfy the "collections.abc.Hashable" protocol,
    #   attempting to infer hashability (i.e., compliance with this protocol)
    #   would uselessly infer the type hint factory for almost all classes as
    #   the universally broad and unsubscriptable "collections.abc.Hashable" ABC
    #   rather than as those specifically narrow classes themselves. Since
    #   everyone prefers and expects specifically narrow type hints rather than
    #   universally broad and unsubscriptable type hints, we ignore hashability.
    # * Dictionary-based views FSMs are intentionally *NOT* defined. Why?
    #   Because:
    #   * The "collections.abc.MappingView" protocol is indistinguishable from
    #     the "collections.abc.Sized" protocol.
    #   * The "collections.abc.ItemsView" protocol are indistinguishable from
    #     the "collections.abc.Collection" protocol.
    #   * The "collections.abc.KeysView" and "ValuesView" protocols are
    #     indistinguishable from the "collections.abc.Set" protocol.
    _START_NODE_NODES_NEXT: _FiniteStateMachine = {
        # ....................{ CONTAINER                  }....................
        # "collections.abc.Container" FSM, intentionally defined first to
        # prioritize this most useful ABC over relatively useless alternatives.
        '__contains__': _FiniteStateMachineNode(
            hint_factory=Container,
            nodes_next={
                # ....................{ COLLECTION         }....................
                # "collections.abc.Collection" FSM.
                frozenset(('__iter__', '__len__')): _FiniteStateMachineNode(
                    hint_factory=Collection,
                    nodes_next={
                        # ....................{ SEQUENCE   }....................
                        # "collections.abc.Sequence" FSM, intentionally defined
                        # first to prioritize this most useful ABC over
                        # relatively useless alternatives.
                        frozenset((
                            '__getitem__',
                            '__reversed__',
                            'count',
                            'index',
                        )): _FiniteStateMachineNode(
                            hint_factory=Sequence,
                            nodes_next={
                                # "collections.abc.MutableSequence" FSM.
                                frozenset((
                                    '__delitem__',
                                    '__iadd__',
                                    '__setitem__',
                                    'append',
                                    'clear',
                                    'extend',
                                    'insert',
                                    'pop',
                                    'remove',
                                    'reverse',
                                )): _FiniteStateMachineNode(
                                    hint_factory=MutableSequence),
                            },
                        ),
                        # ....................{ MAPPING    }....................
                        # "collections.abc.Mapping" FSM, intentionally defined
                        # nearly first to prioritize this more useful ABC over
                        # relatively useless alternatives.
                        frozenset((
                            '__eq__',
                            '__ne__',
                            '__getitem__',
                            'get',
                            'items',
                            'keys',
                            'values',
                        )): _FiniteStateMachineNode(
                            hint_factory=Mapping,
                            nodes_next={
                                # "collections.abc.MutableMapping" FSM.
                                frozenset((
                                    '__delitem__',
                                    '__setitem__',
                                    'clear',
                                    'pop',
                                    'popitem',
                                    'setdefault',
                                    'update',
                                )): _FiniteStateMachineNode(
                                    hint_factory=MutableMapping),
                            },
                        ),
                        # ....................{ SET        }....................
                        # "collections.abc.Set" FSM, intentionally defined
                        # midway to prioritize this more useful ABC over
                        # relatively useless alternatives.
                        frozenset((
                            '__and__',
                            '__eq__',
                            '__ge__',
                            '__gt__',
                            '__le__',
                            '__lt__',
                            '__ne__',
                            '__or__',
                            '__sub__',
                            '__xor__',
                            'isdisjoint',
                        )): _FiniteStateMachineNode(
                            hint_factory=Set,
                            nodes_next={
                                # "collections.abc.MutableSet" FSM.
                                frozenset((
                                    '__iand__',
                                    '__ior__',
                                    '__isub__',
                                    '__ixor__',
                                    'clear',
                                    'pop',
                                    'remove',
                                )): _FiniteStateMachineNode(
                                    hint_factory=MutableSet),
                            },
                        ),
                    },
                ),
            },
        ),
        # ....................{ ITERABLE                   }....................
        # "collections.abc.Iterable" FSM, intentionally defined nearly first to
        # prioritize this more useful ABC over relatively useless alternatives.
        '__iter__': _FiniteStateMachineNode(
            hint_factory=Iterable,
            nodes_next={
                # "collections.abc.Iterator" FSM, intentionally defined first to
                # prioritize this more useful ABC over relatively useless
                # alternatives.
                '__next__': _FiniteStateMachineNode(
                    hint_factory=Iterator,
                    nodes_next={
                        # "collections.abc.Generator" FSM.
                        frozenset((
                            'close',
                            'send',
                            'throw',
                        )): _FiniteStateMachineNode(
                            hint_factory=Generator,
                            nodes_next={
                            },
                        ),
                    },
                ),
                # ....................{ REVERSIBLE         }....................
                # "collections.abc.Reversible" FSM, intentionally defined nearly
                # last to deprioritize this relatively useless ABC over more
                # useful alternatives.
                '__reversed__': _FiniteStateMachineNode(
                    hint_factory=Reversible),
            },
        ),
        # ....................{ AWAITABLE                  }....................
        # "collections.abc.Awaitable" FSM, intentionally defined midway to
        # prioritize this more useful ABC over relatively useless alternatives.
        '__await__': _FiniteStateMachineNode(
            hint_factory=Awaitable,
            nodes_next={
                # "collections.abc.Coroutine" FSM.
                frozenset((
                    'close',
                    'send',
                    'throw',
                )): _FiniteStateMachineNode(hint_factory=Coroutine),
            },
        ),
        # ....................{ ASYNCITERABLE              }....................
        # "collections.abc.AsyncIterable" FSM, intentionally defined nearly last
        # to prioritize this less useful ABC over relatively useless
        # alternatives.
        '__aiter__': _FiniteStateMachineNode(
            hint_factory=AsyncIterable,
            nodes_next={
                # "collections.abc.AsyncIterator" FSM.
                '__anext__': _FiniteStateMachineNode(
                    hint_factory=AsyncIterator,
                    nodes_next={
                        # "collections.abc.AsyncGenerator" FSM.
                        frozenset((
                            'aclose',
                            'asend',
                            'athrow',
                        )): _FiniteStateMachineNode(
                            hint_factory=AsyncGenerator),
                    },
                ),
            },
        ),
        # ....................{ SIZED                      }....................
        # "collections.abc.Sized" FSM, intentionally defined last to
        # deprioritize this almost entirely useless ABC over more useful
        # alternatives. Since *ALMOST* all classes satisfying this ABC also
        # satisfy the "collections.abc.Collection" ABC, this ABC is (in and of
        # itself) both largely useless and exceedingly uncommon.
        '__len__': _FiniteStateMachineNode(hint_factory=Sized),
    }

    # If the active Python interpreter targets Python >= 3.12...
    if IS_PYTHON_AT_LEAST_3_12:
        # Defer version-specific imports.
        from collections.abc import Buffer  # type: ignore[attr-defined]

        # Add the "collections.abc.Buffer" FSM.
        _START_NODE_NODES_NEXT['__buffer__'] = _FiniteStateMachineNode(
            hint_factory=Buffer)
    # Else, the active Python interpreter targets Python < 3.12.

    # ....................{ GLOBALS                        }....................
    # Allow these global variables to be redefined.
    global \
        _START_NODE, \
        _START_NODE_TRANSITION_METHOD_NAMES

    # "collections.abc" finite state machine (FSM).
    _START_NODE = _FiniteStateMachineNode(nodes_next=_START_NODE_NODES_NEXT)

    # Frozen set of the names of all requisite start methods.
    _START_NODE_TRANSITION_METHOD_NAMES = _START_NODE.nodes_next_method_names


# Initialize this submodule.
_init()
