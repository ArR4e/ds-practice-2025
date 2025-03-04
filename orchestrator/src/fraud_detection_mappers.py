from fraud_detection_pb2 import FraudDetectionRequest
from checkout_request import CheckoutRequest, Item
import verification_pb2

def compose_fraud_detection_request(checkout_request: CheckoutRequest) -> FraudDetectionRequest:
    print(f"Processing {checkout_request}")

    fraud_detection_request = FraudDetectionRequest(
        user=FraudDetectionRequest.User(**checkout_request['user']),
        orderData=FraudDetectionRequest.OrderData(
            orderItems=compose_order_items(checkout_request['items']),
            shippingMethod=checkout_request['shippingMethod']
        ),
        creditCard=FraudDetectionRequest.CreditCard(**checkout_request['creditCard']),
        billingAddress=FraudDetectionRequest.BillingAddress(**checkout_request['billingAddress']),
        telemetry=FraudDetectionRequest.Telemetry()
    )
    if 'discountCode' in checkout_request:
        fraud_detection_request.orderData.discountCode = checkout_request['discountCode']
    if 'browser' in checkout_request:
        fraud_detection_request.telemetry.browser=FraudDetectionRequest.Telemetry.Browser(**checkout_request['browser']),
    if 'device' in checkout_request:
        fraud_detection_request.telemetry.device = FraudDetectionRequest.Telemetry.Device(**checkout_request['device'])
    
    return fraud_detection_request

def compose_order_items(items: list[Item]) -> list[FraudDetectionRequest.OrderData.OrderItem]:
    return [*map(lambda item: FraudDetectionRequest.OrderData.OrderItem(**item), items)]

def compose_verificaiton_items(items: list[Item]) -> list[verification_pb2.OrderData.OrderItem]:
    return [*map(lambda item: verification_pb2.OrderData.OrderItem(**item), items)]

def compose_verification_request(checkout_request: CheckoutRequest) -> verification_pb2.verificationRequest:
    print(f"processing {checkout_request}")
    verification_request = verification_pb2.verificationRequest(
        user=verification_pb2.User(**checkout_request['user']),
        orderData=verification_pb2.OrderData(
            orderItems=compose_verificaiton_items(checkout_request['items']),
            shippingMethod=checkout_request['shippingMethod']
        ),
        creditCard=verification_pb2.CreditCard(**checkout_request['creditCard']),
        billing=verification_pb2.BillingAddress(**checkout_request['billingAddress'])
    )
    return verification_request