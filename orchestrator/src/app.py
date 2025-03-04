import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/verification'))
sys.path.insert(0, verification_grpc_path)
from fraud_detection_pb2 import FraudDetectionResponse
from fraud_detection_pb2_grpc import FraudDetectionServiceStub
from checkout_request import CheckoutRequest, OrderStatusResponse
from fraud_detection_mappers import compose_fraud_detection_request,compose_verification_request


from verification_pb2 import verificationResponse
from verification_pb2_grpc import VerifyStub

import hashlib
import grpc

def verify_order(request_data) -> verificationResponse:
    with grpc.insecure_channel('order_verification:50052') as channel:
        stub = VerifyStub(channel=channel)
        return stub.CheckOrder(compose_verification_request(checkout_request=request_data))
    

def detect_fraud(request: CheckoutRequest) -> FraudDetectionResponse:
    # Establish a connection with the fraud-detection gRPC service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = FraudDetectionServiceStub(channel)
        # Call the service through the stub object.
        return stub.DetectFraud(compose_fraud_detection_request(request))

def create_error_message(code: str, message: str):
    return {
        "error": {
            "code": code,
            "message": message
        }
    }

def get_orderID(request_data:CheckoutRequest):
    orderID = hashlib.new('sha256')
    orderID.update(json.dumps(request_data.get('user')).encode())
    orderID.update(os.urandom(8))
    return orderID.hexdigest()

# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request
from flask_cors import CORS
import json

# Create a simple Flask app.
app = Flask(__name__)
# Enable CORS for the app.
CORS(app, resources={r'/*': {'origins': '*'}})

# Define a GET endpoint.
@app.route('/', methods=['GET'])
def index():
    return "Hello"

@app.route('/checkout', methods=['POST'])
def checkout():
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    # Get request object data to json
    request_data: CheckoutRequest = json.loads(request.data)
    # Print request object data
    print("Request Data:", request_data.get('items'))

    verification_response = verify_order(request_data=request_data)
    if verification_response.statusCode != 0:
        return create_error_message("500", verification_response.statusMsg), 500

    fraud_detection_response = detect_fraud(request_data)
    if fraud_detection_response.isFraudulent:
        return create_error_message("FRADULENT_REQUEST", fraud_detection_response.reason), 400

    fraud_detection_response = detect_fraud(request_data)
    if fraud_detection_response.isFraudulent:
        return create_error_message("FRADULENT_REQUEST", fraud_detection_response.reason), 400

    
    orderID = get_orderID(request_data=request_data)

    # Dummy response following the provided YAML specification for the bookstore
    order_status_response: OrderStatusResponse = {
        'orderId': orderID,
        'status': 'Order Approved',
        'suggestedBooks': [
            {'bookId': '123', 'title': 'The Best Book', 'author': 'Author 1'},
            {'bookId': '456', 'title': 'The Second Best Book', 'author': 'Author 2'}
        ]
    }

    return order_status_response, 200


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
