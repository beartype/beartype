.. # ------------------( LICENSE                             )------------------
.. # Copyright (c) 2014-2023 Beartype authors.
.. # See "LICENSE" for further details.
.. #
.. # ------------------( SYNOPSIS                            )------------------
.. # Child reStructuredText (reST) document answering frequently asked
.. # questions.

.. # ------------------( MAIN                                )------------------

.. _faq:faq:

##############################
Ask a Bear Bro Anything (ABBA)
##############################

Beartype now answers your many pressing questions about life, love, and typing.
Maximize your portfolio of crushed bugs by devoutly memorizing the answers to
these... **frequently asked questions (FAQ)!**

.. # ------------------( TABLES OF CONTENTS                  )------------------
.. # Project-wide tables of contents (TOCs). See also official documentation on
.. # the Sphinx-specific "toctree::" directive:
.. #     https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree

|

.. # Table of contents, excluding the above document heading. While the
.. # official reStructuredText documentation suggests that a language-specific
.. # heading will automatically prepend this table, this does *NOT* appear to
.. # be the case. Instead, this heading must be explicitly declared.

.. contents:: **Bear With Us**
   :local:

.. # ------------------( DESCRIPTION                         )------------------

*****************
What is beartype?
*****************

Why, it's the world's first ``O(1)`` runtime type-checker in any
`dynamically-typed`_ lang... oh, *forget it.*

You know typeguard_? Then you know beartype – more or less. beartype is
typeguard_'s younger, faster, and slightly sketchier brother who routinely
ingests performance-enhancing anabolic nootropics.

******************
What is typeguard?
******************

**Okay.** Work with us here, people.

You know how in low-level `statically-typed`_ `memory-unsafe <memory safety_>`__
languages that no one should use like C_ and `C++`_, the compiler validates at
compilation time the types of all values passed to and returned from all
functions and methods across the entire codebase?

.. code-block:: bash

   $ gcc -Werror=int-conversion -xc - <<EOL
   #include <stdio.h>
   int main() {
       printf("Hello, world!");
       return "Goodbye, world.";
   }
   EOL
   <stdin>: In function ‘main’:
   <stdin>:4:11: error: returning ‘char *’ from a function with return type
   ‘int’ makes integer from pointer without a cast [-Werror=int-conversion]
   cc1: some warnings being treated as errors

You know how in high-level `duck-typed <duck typing_>`__ languages that everyone
should use instead like Python_ and Ruby_, the interpreter performs no such
validation at any interpretation phase but instead permits any arbitrary values
to be passed to or returned from any function or method?

.. code-block:: bash

   $ python3 - <<EOL
   def main() -> int:
       print("Hello, world!");
       return "Goodbye, world.";  # <-- pretty sure that's not an "int".
   main()
   EOL

   Hello, world!

Runtime type-checkers like beartype_ and typeguard_ selectively shift the dial
on type safety in Python from `duck <duck typing_>`__ to `static typing
<statically-typed_>`__ while still preserving all of the permissive benefits of
the former as a default behaviour. Now you too can quack like a duck while
roaring like a bear.

.. code-block:: bash

   $ python3 - <<EOL
   from beartype import beartype
   @beartype
   def main() -> int:
       print("Hello, world!");
       return "Goodbye, world.";  # <-- pretty sure that's not an "int".
   main()
   EOL

   Hello, world!
   Traceback (most recent call last):
     File "<stdin>", line 6, in <module>
     File "<string>", line 17, in main
     File "/home/leycec/py/beartype/beartype/_decor/_code/_pep/_error/errormain.py", line 218, in get_beartype_violation
       raise exception_cls(
   beartype.roar.BeartypeCallHintPepReturnException: @beartyped main() return
   'Goodbye, world.' violates type hint <class 'int'>, as value 'Goodbye,
   world.' not int.

***************************
When should I use beartype?
***************************

Use beartype to assure the quality of Python code beyond what tests alone can
assure. If you have yet to test, do that first with a pytest_-based test suite,
tox_ configuration, and `continuous integration (CI) <continuous
integration_>`__. If you have any time, money, or motivation left,
:ref:`annotate callables and classes with PEP-compliant type hints <pep:pep>`
and :ref:`decorate those callables and classes with the @beartype.beartype
decorator <eli5:eli5>`.

Prefer beartype over other runtime and static type-checkers whenever you lack
perfect control over the objects passed to or returned from your callables –
*especially* whenever you cannot limit the size of those objects. This includes
common developer scenarios like:

* You are the author of an **open-source library** intended to be reused by a
  general audience.
* You are the author of a **public app** manipulating Bigly Data™ (i.e., data
  that is big) in app callables – especially when accepting data as input into
  *or* returning data as output from those callables.

If none of the above apply, prefer beartype over static type-checkers
whenever:

* You want to :ref:`check types decidable only at runtime <eli5:static>`.
* You want to write code rather than fight a static type-checker, because
  `static type inference <type inference_>`__ of a `dynamically-typed`_ language
  is guaranteed to fail and frequently does. If you've ever cursed the sky after
  suffixing working code incorrectly typed by mypy_ with non-portable
  vendor-specific pragmas like ``# type: ignore[{unreadable_error}]``, beartype
  was written for you.
* You want to preserve `dynamic typing`_, because Python is a
  `dynamically-typed`_ language. Unlike beartype, static type-checkers enforce
  `static typing`_ and are thus strongly opinionated; they believe `dynamic
  typing`_ is harmful and emit errors on `dynamically-typed`_ code. This
  includes common use patterns like changing the type of a variable by assigning
  that variable a value whose type differs from its initial value. Want to
  freeze a variable from a ``set`` into a ``frozenset``? That's sad, because
  static type-checkers don't want you to. In contrast:

    **Beartype never emits errors, warnings, or exceptions on dynamically-typed
    code,** because Python is not an error.

    **Beartype believes dynamic typing is beneficial by default,** because
    Python is beneficial by default.

    **Beartype is unopinionated.** That's because beartype :ref:`operates
    exclusively at the higher level of pure-Python callables and classes
    <eli5:static>` rather than the lower level of individual statements *inside*
    pure-Python callables and class. Unlike static type-checkers, beartype can't
    be opinionated about things that no one should be.

If none of the above *still* apply, still use beartype. It's `free as in beer
and speech <gratis versus libre_>`__, :ref:`cost-free at installation- and
runtime <eli5:comparison>`, and transparently stacks with existing type-checking
solutions. Leverage beartype until you find something that suites you better,
because beartype is *always* better than nothing.

*******************************
Does beartype do any bad stuff?
*******************************

**Beartype is free** – free as in beer, speech, dependencies, space complexity,
*and* time complexity. Beartype is the textbook definition of "free." We're
pretty sure the Oxford Dictionary now just shows the `beartype mascot`_ instead
of defining that term. Vector art that `a Finnish man <beartype mascot
artist_>`__ slaved for weeks over paints a thousand words.

Beartype might not do as much as you'd like, but it will always do *something* –
which is more than Python's default behaviour, which is to do *nothing* and then
raise exceptions when doing nothing inevitably turns out to have been a bad
idea. Beartype also cleanly interoperates with popular static type-checkers, by
which we mean mypy_ and pyright_. (The `other guys <pytype_>`__ don't exist.)

Beartype can *always* be safely added to *any* Python package, module, app, or
script regardless of size, scope, funding, or audience. Never worry about your
backend Django_ server taking an impromptu swan dive on St. Patty's Day just
because your frontend React_ client pushed a 5MB JSON file serializing a
doubly-nested list of integers. :superscript:`Nobody could have foreseen this!`

The idea of competing runtime type-checkers like typeguard_ is that they
compulsively do *everything.* If you annotate a function decorated by typeguard_
as accepting a triply-nested list of integers and pass that function a list of
1,000 nested lists of 1,000 nested lists of 1,000 integers, *every* call to that
function will check *every* integer transitively nested in that list – even when
that list never changes. Did we mention that list transitively contains
1,000,000,000 integers in total?

.. code-block:: bash

   $ python3 -m timeit -n 1 -r 1 -s '
   from typeguard import typechecked
   @typechecked
   def behold(the_great_destroyer_of_apps: list[list[list[int]]]) -> int:
       return len(the_great_destroyer_of_apps)
   ' 'behold([[[0]*1000]*1000]*1000)'

   1 loop, best of 1: 6.42e+03 sec per loop

Yes, ``6.42e+03 sec per loop == 6420 seconds == 107 minutes == 1 hour, 47
minutes`` to check a single list once. Yes, it's an uncommonly large list...
*but it's still just a list.* This is the worst-case cost of a single call to a
function decorated by a naïve runtime type-checker.

***********************************
Does beartype actually do anything?
***********************************

Generally, as little as it can while still satisfying the accepted definition of
"runtime type-checker." Specifically, beartype performs a `one-way random walk
over the expected data structure of objects passed to and returned from
@beartype-decorated functions and methods <Beartype just does random stuff?
Really?_>`__. Colloquially, beartype type-checks randomly sampled data.
RNGesus_, show your humble disciples the way. ``</ahem>``

Consider `the prior example of a function annotated as accepting a triply-nested
list of integers passed a list containing 1,000 nested lists each containing
1,000 nested lists each containing 1,000 integers <Does beartype do any bad
stuff?_>`__. When decorated by:

* typeguard_, every call to that function checks every integer nested in that
  list.
* beartype, every call to the same function checks only a single random integer
  contained in a single random nested list contained in a single random nested
  list contained in that parent list. This is what we mean by the quaint phrase
  "one-way random walk over the expected data structure."

.. code-block:: bash

   $ python3 -m timeit -n 1024 -r 4 -s '
   from beartype import beartype
   @beartype
   def behold(the_great_destroyer_of_apps: list[list[list[int]]]) -> int:
      return len(the_great_destroyer_of_apps)
   ' 'behold([[[0]*1000]*1000]*1000)'

   1024 loops, best of 4: 13.8 usec per loop

Yes, ``13.8 usec per loop == 13.8 microseconds = 0.0000138 seconds`` to
transitively check only a random integer nested in a single triply-nested list
passed to each call of that function. This is the worst-case cost of a single
call to a function decorated by an ``O(1)`` runtime type-checker.

*************************************
How much does all this *really* cost?
*************************************

What substring of `"Beartype is free we swear it would we lie" <Does beartype do
any bad stuff?_>`__ did you not grep?

*...very well.* Let's pontificate.

Beartype dynamically generates functions wrapping decorated callables with
constant-time runtime type-checking. This separation of concerns means that
beartype exhibits different cost profiles at decoration and call time. Whereas
standard runtime type-checking decorators are fast at decoration time and slow
at call time, beartype is the exact opposite.

At call time, wrapper functions generated by the ``@beartype`` decorator are
guaranteed to unconditionally run in **O(1) non-amortized worst-case time with
negligible constant factors** regardless of type hint complexity or nesting.
This is *not* an amortized average-case analysis. Wrapper functions really are
``O(1)`` time in the best, average, and worst cases.

At decoration time, performance is slightly worse. Internally, beartype
non-recursively iterates over type hints at decoration time with a
micro-optimized breadth-first search (BFS). Since this BFS is memoized, its
cost is paid exactly once per type hint per process; subsequent references to
the same hint over different parameters and returns of different callables in
the same process reuse the results of the previously memoized BFS for that
hint. The ``@beartype`` decorator itself thus runs in:

* **O(1) amortized average-case time.**
* **O(k) non-amortized worst-case time** for ``k`` the number of child type
  hints nested in a parent type hint and including that parent.

Since we generally expect a callable to be decorated only once but called
multiple times per process, we might expect the cost of decoration to be
ignorable in the aggregate. Interestingly, this is not the case. Although only
paid once and obviated through memoization, decoration time is sufficiently
expensive and call time sufficiently inexpensive that beartype spends most of
its wall-clock merely decorating callables. The actual function wrappers
dynamically generated by ``@beartype`` consume comparatively little wall-clock,
even when repeatedly called many times.

****************************************
Beartype just does random stuff? Really?
****************************************

**Yes.** Beartype just does random stuff. That's what we're trying to say here.
We didn't want to admit it, but the ugly truth is out now. Are you smirking?
Because that looks like a smirk. Repeat after this FAQ:

* Beartype's greatest strength is that it checks types in constant time.
* Beartype's greatest weakness is that it checks types in constant time.

Only so many type-checks can be stuffed into a constant slice of time with
negligible constant factors. Let's detail exactly what (and why) beartype
stuffs into its well-bounded slice of the CPU pie.

Standard runtime type checkers naïvely brute-force the problem by type-checking
*all* child objects transitively reachable from parent objects passed to and
returned from callables in ``O(n)`` linear time for ``n`` such objects. This
approach avoids false positives (i.e., raising exceptions for valid objects)
*and* false negatives (i.e., failing to raise exceptions for invalid objects),
which is good. But this approach also duplicates work when those objects remain
unchanged over multiple calls to those callables, which is bad.

Beartype circumvents that badness by generating code at decoration time
performing a one-way random tree walk over the expected nested structure of
those objects at call time. For each expected nesting level of each container
passed to or returned from each callable decorated by ``@beartype`` starting at
that container and ending either when a check fails *or* all checks succeed,
that callable performs these checks (in order):

#. A **shallow type-check** that the current possibly nested container is an
   instance of the type given by the current possibly nested type hint.
#. A **deep type-check** that an item randomly selected from that container
   itself satisfies the first check.

For example, given a parameter's type hint ``list[tuple[Sequence[str]]]``,
beartype generates code at decoration time performing these checks at call time
(in order):

#. A check that the object passed as this parameter is a list.
#. A check that an item randomly selected from this list is a tuple.
#. A check that an item randomly selected from this tuple is a sequence.
#. A check that an item randomly selected from this sequence is a string.

Beartype thus performs one check for each possibly nested type hint for each
annotated parameter or return object for each call to each decorated callable.
This deep randomness gives us soft statistical expectations as to the number of
calls needed to check everything. Specifically, `it can be shown that beartype
type-checks on average <Nobody Expects the Linearithmic Time_>`__ *all* child
objects transitively reachable from parent objects passed to and returned from
callables in ``O(n log n)`` calls to those callables for ``n`` such objects.
Praise RNGesus_!

Beartype avoids false positives and rarely duplicates work when those objects
remain unchanged over multiple calls to those callables, which is good. Sadly,
beartype also invites false negatives, because this approach only checks a
vertical slice of the full container structure each call, which is bad.

We claim without evidence that false negatives are unlikely under the
optimistic assumption that most real-world containers are **homogenous** (i.e.,
contain only items of the same type) rather than **heterogenous** (i.e.,
contain items of differing types). Examples of homogenous containers include
(byte-)strings, `ranges <range_>`__, `streams <io_>`__, `memory views
<memoryview_>`__, `method resolution orders (MROs) <mro_>`__, `generic alias
parameters`_, lists returned by the dir_ builtin, iterables generated by the
os.walk_ function, standard NumPy_ arrays, Pandas_ ``DataFrame`` columns,
PyTorch_ tensors, NetworkX_ graphs, and really all scientific containers ever.

.. _faq:realtime:

*************************************
What does "near-real-time" even mean?
*************************************

Beartype type-checks objects at runtime in around **1µs** (i.e., one
microsecond, one millionth of a second), the standard high-water mark for
`real-time software <real-time_>`__:

.. code-block:: pycon

   # Let's check a list of 181,320,382 integers in ~1µs.
   >>> from beartype import beartype
   >>> def sum_list_unbeartyped(some_list: list) -> int:
   ...     return sum(some_list)
   >>> sum_list_beartyped = beartype(sum_list_unbeartyped)
   >>> %time sum_list_unbeartyped([42]*0xACEBABE)
   CPU times: user 3.15 s, sys: 418 ms, total: 3.57 s
   Wall time: 3.58 s  # <-- okay.
   Out[20]: 7615456044
   >>> %time sum_list_beartyped([42]*0xACEBABE)
   CPU times: user 3.11 s, sys: 440 ms, total: 3.55 s
   Wall time: 3.56 s  # <-- woah.
   Out[22]: 7615456044

Beartype does *not* contractually guarantee this performance, as this example
demonstrates. Under abnormal processing loads (e.g., leycec_'s arthritic Athlon™
II X2 240, because you can't have enough redundant 2's in a product line) or
when passed edge-case type hints (e.g., classes whose metaclasses implement
stunningly awful ``__isinstancecheck__()`` dunder methods), beartype's
worst-case performance could exceed an average-case near-instantaneous response.

Beartype is therefore *not* real-time_; beartype is merely `near-real-time (NRT)
<near-real-time_>`__, also variously referred to as "pseudo-real-time,"
"quasi-real-time," or simply "high-performance." Real-time_ software guarantees
performance with a scheduler forcibly terminating tasks exceeding some deadline.
That's bad in most use cases. The outrageous cost of enforcement harms
real-world performance, stability, and usability.

**NRT.** It's good for you. It's good for your codebase. It's just good.

**********************
How do I type-check...
**********************

...yes? Go on.

...Boto3 types?
###############

**tl;dr:** You just want bearboto3_, a well-maintained third-party package
cleanly integrating beartype **+** Boto3_. But you're not doing that. You're
reading on to find out why you want bearboto3_, aren't you? I *knew* it.

Boto3_ is the official Amazon Web Services (AWS) Software Development Kit (SDK)
for Python. Type-checking Boto3_ types is decidedly non-trivial, because Boto3_
dynamically fabricates unimportable types from runtime service requests. These
types *cannot* be externally accessed and thus *cannot* be used as type hints.

**H-hey!** Put down the hot butter knife. Your Friday night may be up in flames,
but we're gonna put out the fire. It's what we do here. Now, you have two
competing solutions with concomitant tradeoffs. You can type-check Boto3_ types
against either:

* **Static type-checkers** (e.g., mypy_, pyright_) by importing Boto3_ stub
  types from an external third-party dependency (e.g., mypy-boto3_), enabling
  context-aware code completion across compliant IDEs (e.g., PyCharm_, `VSCode
  Pylance <Pylance_>`__). Those types are merely placeholder stubs; they do
  *not* correspond to actual Boto3_ types and thus break runtime type-checkers
  (including beartype) when used as type hints.
* **Beartype** by fabricating your own `PEP-compliant beartype validators
  <Beartype Validators_>`__, enabling beartype to validate arbitrary objects
  against actual Boto3_ types at runtime when used as type hints. You already
  require beartype, so no additional third-party dependencies are required.
  Those validators are silently ignored by static type-checkers; they do *not*
  enable context-aware code completion across compliant IDEs.

"B-but that *sucks*! How can we have our salmon and devour it too?", you demand
with a tremulous quaver. Excessive caffeine and inadequate gaming did you no
favors tonight. You know this. Yet again you reach for the hot butter knife.

**H-hey!** You can, okay? You can have everything that market forces demand.
Bring to *bear* :superscript:`cough` the combined powers of `PEP 484-compliant
type aliases <type aliases_>`__, the `PEP 484-compliant "typing.TYPE_CHECKING"
boolean global <typing.TYPE_CHECKING_>`__, and `beartype validators <Beartype
Validators_>`__ to satisfy both static and runtime type-checkers:

.. code-block:: python

   # Import the requisite machinery.
   from beartype import beartype
   from boto3 import resource
   from boto3.resources.base import ServiceResource
   from typing import TYPE_CHECKING

   # If performing static type-checking (e.g., mypy, pyright), import boto3
   # stub types safely usable *ONLY* by static type-checkers.
   if TYPE_CHECKING:
       from mypy_boto3_s3.service_resource import Bucket
   # Else, @beartime-based runtime type-checking is being performed. Alias the
   # same boto3 stub types imported above to their semantically equivalent
   # beartype validators accessible *ONLY* to runtime type-checkers.
   else:
       # Import even more requisite machinery. Can't have enough, I say!
       from beartype.vale import IsAttr, IsEqual
       from typing import Annotated   # <--------------- if Python ≥ 3.9.0
       # from typing_extensions import Annotated   # <-- if Python < 3.9.0

       # Generalize this to other boto3 types by copy-and-pasting this and
       # replacing the base type and "s3.Bucket" with the wonky runtime names
       # of those types. Sadly, there is no one-size-fits all common base class,
       # but you should find what you need in the following places:
       # * "boto3.resources.base.ServiceResource".
       # * "boto3.resources.collection.ResourceCollection".
       # * "botocore.client.BaseClient".
       # * "botocore.paginate.Paginator".
       # * "botocore.waiter.Waiter".
       Bucket = Annotated[ServiceResource,
           IsAttr['__class__', IsAttr['__name__', IsEqual["s3.Bucket"]]]]

   # Do this for the good of the gross domestic product, @beartype.
   @beartype
   def get_s3_bucket_example() -> Bucket:
       s3 = resource('s3')
       return s3.Bucket('example')

You're welcome.

...JAX arrays?
##############

You only have two options here. Choose wisely, wily scientist. If:

* You don't mind adding an **additional mandatory runtime dependency** to your
  app:

  * Require the `third-party "jaxtyping" package <jaxtyping_>`__.
  * Annotate callables with type hint factories published by ``jaxtyping``
    (e.g., ``jaxtyping.Float[jaxtyping.Array, '{metadata1 ... metadataN}']``).

  Beartype fully supports `typed JAX arrays <jaxtyping_>`__. Because `Google
  mathematician @patrick-kidger <patrick-kidger_>`__ did all the hard work, we
  didn't have to. Bless your runtime API, @patrick-kidger.

* You mind adding an additional mandatory runtime dependency to your app, prefer
  `beartype validators <Tensor Property Matching_>`__. Since `JAX declares a
  broadly similar API to that of NumPy with its "jax.numpy" compatibility layer
  <jax.numpy_>`__, most NumPy-specific examples cleanly generalize to JAX.
  Beartype is *no* exception.

Bask in the array of options at your disposal! :superscript:`...get it?
...array? I'll stop now.`

...NumPy arrays?
################

You have more than a few options here. If you want to type-check:

* The ``dtype`` of a NumPy array, prefer the `official
  "numpy.typing.NDArray[{dtype}]" type hint factory bundled with NumPy
  explicitly supported by beartype <NumPy Type Hints_>`__ – also referred to as
  a `typed NumPy array <NumPy Type Hints_>`__.
* The ``shape`` of a NumPy array (and possibly more), you have two additional
  sub-options here depending on whether:

  * You want **static type-checkers** to enforce that ``shape`` *and* you don't
    mind adding an **additional mandatory runtime dependency** to your app. In
    this case:

    * Require the `third-party "nptyping" package <nptyping_>`__.
    * Prefer the unofficial ``nptyping.NDArray[{nptyping.dtype},
      nptyping.Shape[...]]`` type hint factory implicitly supported by beartype.

    Beartype fully supports `typed NumPy arrays <NumPy Type Hints_>`__. Because
    beartype cares.

  * You don't mind static type-checkers ignoring that ``shape`` *or* you mind
    adding an additional mandatory runtime dependency to your app. In this case,
    prefer `beartype validators <Tensor Property Matching_>`__.

Options are good! Repeat this mantra in times of need.

...PyTorch tensors?
###################

You only have two options here. We're pretty sure two is better than none. Thus,
we give thanks. If:

* You don't mind adding an **additional mandatory runtime dependency** to your
  app:

  * Require the `third-party "TorchTyping" package <TorchTyping_>`__.
  * Annotate callables with type hint factories published by TorchTyping (e.g.,
    ``TorchTyping.TensorType['{metadata1}', ..., '{metadataN}']``).

  Beartype fully supports `typed PyTorch tensors <TorchTyping_>`__. Because
  `Google mathematician @patrick-kidger <patrick-kidger_>`__ did all the hard
  work, we didn't have to. Bless your runtime API, @patrick-kidger.

* You mind adding an additional mandatory runtime dependency to your app. In
  this case, prefer `beartype validators <Beartype Validators_>`__. For example,
  validate callable parameters and returns as either floating-point *or*
  integral PyTorch tensors via the `functional validator factory
  beartype.vale.Is[...] <beartype.vale.Is_>`__:

  .. code-block:: python

     # Import the requisite machinery.
     from beartype import beartype
     from beartype.vale import Is
     from typing import Annotated   # <--------------- if Python ≥ 3.9.0
     # from typing_extensions import Annotated   # <-- if Python < 3.9.0

     # Import PyTorch (d)types of interest.
     from torch import (
         float as torch_float,
         int as torch_int,
         tensor,
     )

     # PEP-compliant type hint matching only a floating-point PyTorch tensor.
     TorchTensorFloat = Annotated[tensor, Is[
         lambda tens: tens.type() is torch_float]]

     # PEP-compliant type hint matching only an integral PyTorch tensor.
     TorchTensorInt = Annotated[tensor, Is[
         lambda tens: tens.type() is torch_int]]

     # Type-check everything like an NLP babelfish.
     @beartype
     def deep_dream(dreamy_tensor: TorchTensorFloat) -> TorchTensorInt:
         return dreamy_tensor.type(dtype=torch_int)

  Since `beartype.vale.Is[...] <beartype.vale.Is_>`__ supports arbitrary
  Turing-complete Python expressions, the above example generalizes to typing
  the device, dimensionality, and other metadata of PyTorch tensors to whatever
  degree of specificity you desire.

  `beartype.vale.Is[...] <beartype.vale.Is_>`__: *it's lambdas all the way
  down.*

...mock types?
##############

Beartype fully relies upon the `isinstance() builtin <isinstance_>`__ under the
hood for its low-level runtime type-checking needs. If you can fool
``isinstance()``, you can fool beartype. Can you fool beartype into believing
an instance of a mock type is an instance of the type it mocks, though?

**You bet your bottom honey barrel.** In your mock type, just define a new
``__class__()`` property returning the original type: e.g.,

.. code-block:: pycon

   >>> class OriginalType: pass
   >>> class MockType:
   ...     @property
   ...     def __class__(self) -> type: return OriginalType

   >>> from beartype import beartype
   >>> @beartype
   ... def muh_func(self, muh_arg: OriginalType): print('Yolo, bro.')
   >>> muh_func(MockType())
   Yolo, bro.

This is why we beartype.

...under VSCode?
################

**Beartype fully supports VSCode out-of-the-box** – especially via Pylance_,
Microsoft's bleeding-edge Python extension for VSCode. Chortle in your joy,
corporate subscribers and academic sponsors! All the intellisense you can
tab-complete and more is now within your honey-slathered paws. Why? Because...

Beartype laboriously complies with pyright_, Microsoft's in-house static
type-checker for Python. Pylance_ enables pyright_ as its default static
type-checker. Beartype thus complies with Pylance_, too.

Beartype *also* laboriously complies with mypy_, Python's official static
type-checker. VSCode users preferring mypy_ to pyright_ may switch Pylance_ to
type-check via the former. Just:

#. `Install mypy <mypy install_>`__.
#. `Install the VSCode Mypy extension <VSCode Mypy extension_>`__.
#. Open the *User Settings* dialog.
#. Search for ``Type Checking Mode``.
#. Browse to ``Python › Analysis: Type Checking Mode``.
#. Switch the "default rule set for type checking" to ``off``.

|VSCode-Pylance-type-checking-setting|

:superscript:`Pretend that reads "off" rather than "strict". Pretend we took
this screenshot.`

There are tradeoffs here, because that's just how the code rolls. On:

* The one paw, pyright_ is *significantly* more performant than mypy_ under
  Pylance_ and supports type-checking standards currently unsupported by mypy_
  (e.g., recursive type hints).
* The other paw, mypy_ supports a vast plugin architecture enabling third-party
  Python packages to describe dynamic runtime behaviour statically.

Beartype: we enable hard choices, so that you can make them for us.

.. # ------------------( IMAGES ~ screenshot                 )------------------
.. |VSCode-Pylance-type-checking-setting| image:: https://user-images.githubusercontent.com/217028/164616311-c4a24889-0c53-4726-9051-29be7263ee9b.png
   :alt: Disabling pyright-based VSCode Pylance type-checking

...under [insert-IDE-name-here]?
################################

Beartype fully complies with mypy_, pyright_, :pep:`561`, and other community
standards that govern how Python is statically type-checked. Modern Integrated
Development Environments (IDEs) support these standards - hopefully including
your GigaChad IDE of choice.

...with type narrowing?
#######################

Beartype fully supports `type narrowing`_ with the :pep:`647`\ -compliant
typing.TypeGuard_ type hint. In fact, beartype supports type narrowing of *all*
PEP-compliant type hints and is thus the first maximal type narrower.

Specifically, the `procedural beartype.door.is_bearable() function
<is_bearable_>`__ and `object-oriented beartype.door.TypeHint.is_bearable()
method <beartype.door_>`__ both narrow the type of the passed test object (which
can be *anything*) to the passed type hint (which can be *anything*
PEP-compliant). Both soft-guarantee runtime performance on the order of less
than 1µs (i.e., less than one millionth of a second), preserving runtime
performance and your personal sanity.

Calling either `is_bearable() <is_bearable_>`__ *or* `TypeHint.is_bearable()
<beartype.door_>`__ in your code enables beartype to symbiotically eliminate
false positives from static type-checkers checking that code, substantially
reducing static type-checker spam that went rotten decades ago: e.g.,

.. code-block:: python

   # Import the requisite machinery.
   from beartype.door import is_bearable

   def narrow_types_like_a_boss_with_beartype(lst: list[int | str]):
       '''
       This function eliminates false positives from static type-checkers
       like mypy and pyright by narrowing types with ``is_bearable()``.

       Note that decorating this function with ``@beartype`` is *not*
       required to inform static type-checkers of type narrowing. Of
       course, you should still do that anyway. Trust is a fickle thing.
       '''

       # If this list contains integers rather than strings, call another
       # function accepting only a list of integers.
       if is_bearable(lst, list[int]):
           # "lst" has been though a lot. Let's celebrate its courageous story.
           munch_on_list_of_strings(lst)  # mypy/pyright: OK!
       # If this list contains strings rather than integers, call another
       # function accepting only a list of strings.
       elif is_bearable(lst, list[str]):
           # "lst": The Story of "lst." The saga of false positives ends now.
           munch_on_list_of_strings(lst)  # mypy/pyright: OK!

   def munch_on_list_of_strings(lst: list[str]): ...
   def munch_on_list_of_integers(lst: list[int]): ...

Beartype: *because you no longer care what static type-checkers think.*

***********************************************************************************
Why is it so cold in @leycec's poorly insulated cottage in the Canadian wilderness?
***********************************************************************************

Not even Poło the polar bear knows.

Also, anyone else notice that this question answers itself? Anybody? No? Nobody?
It is just me? ``</snowflakes_fall_silently>``