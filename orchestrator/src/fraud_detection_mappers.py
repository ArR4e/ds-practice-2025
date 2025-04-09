from fraud_detection_pb2 import FraudDetectionData
from checkout_request import CheckoutRequest, Item


def compose_fraud_detection_data(order_id: str, checkout_request: CheckoutRequest) -> FraudDetectionData:
    fraud_detection_request = FraudDetectionData(
        orderId=order_id,
        user=FraudDetectionData.User(**checkout_request['user']),
        orderData=FraudDetectionData.OrderData(
            orderItems=compose_order_items(checkout_request['items']),
            shippingMethod=checkout_request['shippingMethod']
        ),
        creditCard=FraudDetectionData.CreditCard(**checkout_request['creditCard']),
        billingAddress=FraudDetectionData.BillingAddress(**checkout_request['billingAddress']),
        telemetry=FraudDetectionData.Telemetry()
    )
    if 'discountCode' in checkout_request:
        fraud_detection_request.orderData.discountCode = checkout_request['discountCode']
    if 'browser' in checkout_request:
        fraud_detection_request.telemetry.browser = FraudDetectionData.Telemetry.Browser(**checkout_request['browser']),
    if 'device' in checkout_request:
        fraud_detection_request.telemetry.device = FraudDetectionData.Telemetry.Device(**checkout_request['device'])
    
    return fraud_detection_request


def compose_order_items(items: list[Item]) -> list[FraudDetectionData.OrderData.OrderItem]:
    return [*map(lambda item: FraudDetectionData.OrderData.OrderItem(**item), items)]
