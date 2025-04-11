from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OK(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthDeclaration(_message.Message):
    __slots__ = ("status", "msg")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    status: bool
    msg: str
    def __init__(self, status: bool = ..., msg: _Optional[str] = ...) -> None: ...

class VoteRequest(_message.Message):
    __slots__ = ("senderUUID", "sender_name", "term")
    SENDERUUID_FIELD_NUMBER: _ClassVar[int]
    SENDER_NAME_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    senderUUID: str
    sender_name: str
    term: int
    def __init__(self, senderUUID: _Optional[str] = ..., sender_name: _Optional[str] = ..., term: _Optional[int] = ...) -> None: ...

class VoteResponse(_message.Message):
    __slots__ = ("senderUUID", "sender_name", "confirmation")
    SENDERUUID_FIELD_NUMBER: _ClassVar[int]
    SENDER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIRMATION_FIELD_NUMBER: _ClassVar[int]
    senderUUID: str
    sender_name: str
    confirmation: bool
    def __init__(self, senderUUID: _Optional[str] = ..., sender_name: _Optional[str] = ..., confirmation: bool = ...) -> None: ...
