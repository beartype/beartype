#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide LangChain integration tests.

This submodule functionally tests the :mod:`beartype` package against the
third-party LangChain package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('langchain')
def test_langchain_baseretriever() -> None:
    '''
    Integration test validating that the :mod:`beartype` package raises *no*
    unexpected exceptions when type-checking instances of the third-party
    :class:`langchain_core.retrievers.BaseRetriever` superclass, itself a
    subclass of the third-party :class:`pydantic.BaseModel` superclass known to
    be hostile to runtime type-checking.

    Consequently, this integration test transitively tests Pydantic as well.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.typing import List
    from langchain_core.callbacks import CallbackManagerForRetrieverRun
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever

    # ....................{ CLASSES                        }....................
    @beartype
    class CustomRetriever(BaseRetriever):
        '''
        Arbitrary :func:`beartype.beartype`-decorated LangChain retriever
        subclassing the third-party :class:`pydantic.BaseModel` superclass known
        to be hostile to runtime type-checking.
        '''

        def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
        ) -> List[Document]:
            '''
            Arbitrary implementation of this abstract method required to be
            implemented by concrete subclasses of the abstract
            :class:`.BaseRetriever` superclass.

            This method retrieves documents relevant to a query.

            Parameters
            ----------
            query : str
                Query to find relevant documents for.
            run_manager : CallbackManagerForRetrieverRun
                Callbacks handler to use.

            Returns
            -------
            list[Document]
                List of relevant documents.
            '''

            # Justice never sleeps. Neither does QA.
            return []

    # ....................{ LOCALS                         }....................
    # Arbitrary instance of this concrete subclass, implicitly validating that
    # @beartype permissively decorates "pydantic.BaseModel" subclasses hostile
    # to runtime type-checking.
    CustomRetriever()
