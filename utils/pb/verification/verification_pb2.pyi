from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VerificationRequest(_message.Message):
    __slots__ = ("user", "orderData", "creditCard", "billing")
    USER_FIELD_NUMBER: _ClassVar[int]
    ORDERDATA_FIELD_NUMBER: _ClassVar[int]
    CREDITCARD_FIELD_NUMBER: _ClassVar[int]
    BILLING_FIELD_NUMBER: _ClassVar[int]
    user: User
    orderData: OrderData
    creditCard: CreditCard
    billing: BillingAddress
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ..., orderData: _Optional[_Union[OrderData, _Mapping]] = ..., creditCard: _Optional[_Union[CreditCard, _Mapping]] = ..., billing: _Optional[_Union[BillingAddress, _Mapping]] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("name", "contact")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONTACT_FIELD_NUMBER: _ClassVar[int]
    name: str
    contact: str
    def __init__(self, name: _Optional[str] = ..., contact: _Optional[str] = ...) -> None: ...

class OrderData(_message.Message):
    __slots__ = ("orderItems", "discountCode", "shippingMethod")
    class OrderItem(_message.Message):
        __slots__ = ("name", "quantity")
        NAME_FIELD_NUMBER: _ClassVar[int]
        QUANTITY_FIELD_NUMBER: _ClassVar[int]
        name: str
        quantity: int
        def __init__(self, name: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...
    ORDERITEMS_FIELD_NUMBER: _ClassVar[int]
    DISCOUNTCODE_FIELD_NUMBER: _ClassVar[int]
    SHIPPINGMETHOD_FIELD_NUMBER: _ClassVar[int]
    orderItems: _containers.RepeatedCompositeFieldContainer[OrderData.OrderItem]
    discountCode: str
    shippingMethod: str
    def __init__(self, orderItems: _Optional[_Iterable[_Union[OrderData.OrderItem, _Mapping]]] = ..., discountCode: _Optional[str] = ..., shippingMethod: _Optional[str] = ...) -> None: ...

class CreditCard(_message.Message):
    __slots__ = ("number", "expirationDate", "cvv")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    EXPIRATIONDATE_FIELD_NUMBER: _ClassVar[int]
    CVV_FIELD_NUMBER: _ClassVar[int]
    number: str
    expirationDate: str
    cvv: str
    def __init__(self, number: _Optional[str] = ..., expirationDate: _Optional[str] = ..., cvv: _Optional[str] = ...) -> None: ...

class BillingAddress(_message.Message):
    __slots__ = ("street", "city", "state", "zip", "country")
    STREET_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ZIP_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    street: str
    city: str
    state: str
    zip: str
    country: str
    def __init__(self, street: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., zip: _Optional[str] = ..., country: _Optional[str] = ...) -> None: ...

class VerificationResponse(_message.Message):
    __slots__ = ("statusCode", "statusMsg")
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    STATUSMSG_FIELD_NUMBER: _ClassVar[int]
    statusCode: int
    statusMsg: str
    def __init__(self, statusCode: _Optional[int] = ..., statusMsg: _Optional[str] = ...) -> None: ...
