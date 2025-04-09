from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SuggestionsData(_message.Message):
    __slots__ = ("orderId", "userId", "boughtBookIds")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    USERID_FIELD_NUMBER: _ClassVar[int]
    BOUGHTBOOKIDS_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    userId: str
    boughtBookIds: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, orderId: _Optional[str] = ..., userId: _Optional[str] = ..., boughtBookIds: _Optional[_Iterable[str]] = ...) -> None: ...

class InitializeRequestDataResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BookSuggestionRequest(_message.Message):
    __slots__ = ("orderId",)
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    def __init__(self, orderId: _Optional[str] = ...) -> None: ...

class BookSuggestionResponse(_message.Message):
    __slots__ = ("suggestedBooks",)
    class SuggestedBook(_message.Message):
        __slots__ = ("bookId", "title", "author")
        BOOKID_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        AUTHOR_FIELD_NUMBER: _ClassVar[int]
        bookId: str
        title: str
        author: str
        def __init__(self, bookId: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...
    SUGGESTEDBOOKS_FIELD_NUMBER: _ClassVar[int]
    suggestedBooks: _containers.RepeatedCompositeFieldContainer[BookSuggestionResponse.SuggestedBook]
    def __init__(self, suggestedBooks: _Optional[_Iterable[_Union[BookSuggestionResponse.SuggestedBook, _Mapping]]] = ...) -> None: ...

class ClearSuggestionsDataRequest(_message.Message):
    __slots__ = ("orderId",)
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    def __init__(self, orderId: _Optional[str] = ...) -> None: ...

class ClearSuggestionsDataResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
