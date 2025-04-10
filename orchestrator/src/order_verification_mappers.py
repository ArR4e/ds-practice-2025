from checkout_request import CheckoutRequest, Item
from verification_pb2 import VerificationRequest, User, OrderData, CreditCard, BillingAddress

def compose_verificaiton_items(items: list[Item]) -> list[OrderData.OrderItem]:
    return [*map(lambda item: OrderData.OrderItem(**item), items)]


# Verification Request:
# User
# Order data:
#     List<items> order items
#     Discount code
#     shipping method
# credit card
# billing address
def compose_verification_request(checkout_request: CheckoutRequest, orderId: str) -> VerificationRequest:
    print(checkout_request)
    verification_request = VerificationRequest(
        orderId=orderId,
        user=User(**checkout_request['user']),
        orderData=OrderData(
            orderItems=compose_verificaiton_items(checkout_request['items']),
            shippingMethod=checkout_request.get('shippingMethod'),
            discountCode=checkout_request.get('discountCode')
        ),
        creditCard=CreditCard(**checkout_request['creditCard']),
        billing=BillingAddress(**checkout_request['billingAddress'])
    )
    return verification_request