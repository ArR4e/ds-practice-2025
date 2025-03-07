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
suggestions_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, suggestions_grpc_path)

from fraud_detection_pb2 import FraudDetectionResponse
from fraud_detection_pb2_grpc import FraudDetectionServiceStub
from verification_pb2 import VerificationResponse
from verification_pb2_grpc import VerifyStub
from suggestions_pb2 import BookSuggestionResponse, BookSuggestionRequest
from suggestions_pb2_grpc import SuggestionsServiceStub

from checkout_request import CheckoutRequest, OrderStatusResponse, Book
from fraud_detection_mappers import compose_fraud_detection_request
from order_verification_mappers import compose_verification_request

from random import randint
from concurrent.futures import ThreadPoolExecutor, Future
import hashlib
import grpc
import signal


executor = ThreadPoolExecutor(thread_name_prefix="orchestrator-exec", max_workers=10)

def verify_order(request_data: CheckoutRequest) -> VerificationResponse:
    with grpc.insecure_channel('order_verification:50052') as channel:
        stub = VerifyStub(channel=channel)
        return stub.CheckOrder(compose_verification_request(checkout_request=request_data))
    

def detect_fraud(request: CheckoutRequest) -> FraudDetectionResponse:
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        stub = FraudDetectionServiceStub(channel)
        return stub.DetectFraud(compose_fraud_detection_request(request))

def suggest_books(request: CheckoutRequest) -> list[Book]:
    with grpc.insecure_channel('book_suggestions:50053') as channel:
        stub = SuggestionsServiceStub(channel)
        response: BookSuggestionResponse = stub.SuggestBooks(
            BookSuggestionRequest(
                # As currently there is no users and database with books and no book ids for POC we just generate some ids
                userId = "1",
                boughtBookIds=[str(randint(0, 63)) for _ in range(5)]
            )
        )
        return [*map(to_book, response.suggestedBooks)]

def to_book(suggested_book: BookSuggestionResponse.SuggestedBook) -> Book:
    return {
        'bookId': suggested_book.bookId,
        'title': suggested_book.title,
        'author': suggested_book.author
    }

def create_error_message(code: str, message: str):
    return {
        "error": {
            "code": code,
            "message": message
        }
    }

def get_order_id(request_data: CheckoutRequest):
    order_id = hashlib.new('sha256')
    order_id.update(json.dumps(request_data.get('user')).encode())
    order_id.update(os.urandom(8))
    return order_id.hexdigest()

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
    request_data: CheckoutRequest = json.loads(request.data)
    print("Request Data:", request_data.get('items'))

    futures = [
        executor.submit(verify_order, request_data),
        executor.submit(detect_fraud, request_data),
        executor.submit(suggest_books, request_data)
    ]
    verification_response, fraud_detection_response, suggested_books = map(Future.result, futures)

    if verification_response.statusCode != 0:
        return create_error_message("FAILED_VERIFICATION", verification_response.statusMsg), 400
    if fraud_detection_response.isFraudulent:
        return create_error_message("FRADULENT_REQUEST", fraud_detection_response.reason), 400

    order_id = get_order_id(request_data=request_data)
    order_status_response: OrderStatusResponse = {
        'orderId': order_id,
        'status': 'Order Approved',
        'suggestedBooks': suggested_books
    }
    return order_status_response, 200


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')


def clean_up():
    print("Received SIGTERM, shutting down executor...")
    executor.shutdown(wait=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, clean_up)