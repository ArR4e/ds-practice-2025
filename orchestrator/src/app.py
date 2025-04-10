import asyncio
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

from fraud_detection_pb2 import QuickFraudDetectionRequest, QuickFraudDetectionResponse, \
    ComprehensiveFraudDetectionRequest, ComprehensiveFraudDetectionResponse, \
    ClearFraudDetectionDataRequest, ClearFraudDetectionDataResponse
from fraud_detection_pb2_grpc import FraudDetectionServiceStub

from utils.pb.verification.verification_pb2 import VerificationResponse, VerifyData
from utils.pb.verification.verification_pb2_grpc import VerifyStub

from suggestions_pb2 import BookSuggestionResponse, BookSuggestionRequest, SuggestionsData, \
    ClearSuggestionsDataRequest, ClearSuggestionsDataResponse
from suggestions_pb2_grpc import SuggestionsServiceStub

from checkout_request import CheckoutRequest, OrderStatusResponse, Book
from fraud_detection_mappers import compose_fraud_detection_data
from order_verification_mappers import compose_verification_request

from contextlib import contextmanager
from random import randint
from asyncio import gather, create_task
import hashlib
import grpc
import logging.config
from pathlib import Path
from json import load
from uuid import uuid4

global logger
logger = logging.getLogger("orchestrator_logger")
path = Path(__file__).parent / "config.json"
with open(path) as file:
    config = load(file)
logging.config.dictConfig(config=config)

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


# TODO when nothing to do:
#  Use message templates + args in logs
#  use only one type of '"
#  use UUIDv4 for order id

@app.route('/', methods=['GET'])
def index():
    return "Hello"


@app.route('/checkout', methods=['POST'])
async def checkout() -> [OrderStatusResponse, int]:
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    request_data: CheckoutRequest = json.loads(request.data)
    logger.info("Serving checkout request")
    logger.debug(f"Request Data: {request_data}")

    # TODO: [DS-LOGS] add order id to context + add log filter
    with order_data_context_manager() as order_id:
        await initialize_order_data(order_id, request_data)
        suggested_books = await process_order(order_id)

        logger.debug(f"Generated order_id {order_id}")
        order_status_response: OrderStatusResponse = {
            'orderId': order_id,
            'status': 'Order Approved',
            'suggestedBooks': suggested_books
        }
        logger.info(f"Confirmed purchace for order: {order_id}")

        # TODO: [DS-QUEUE] Queue For Processing
        return order_status_response, 200


@contextmanager
async def order_data_context_manager():
    order_id = str(uuid4())
    try:
        yield order_id
    finally:
        await clear_order_data(order_id)


async def initialize_order_data(order_id: str, request: CheckoutRequest):
    logger.info("Initializing order data in services")
    async with asyncio.TaskGroup as tg:
        await gather(
            tg.create_task(initialize_verify_order_data(order_id, request)),
            tg.create_task(initialize_detect_fraud_data(order_id, request)),
            tg.create_task(initialize_suggest_books_data(order_id, request))
        )


async def initialize_verify_order_data(order_id: str, request: CheckoutRequest) -> None:
    logger.debug("Initializing data in verification service")
    async with grpc.insecure_channel('order_verification:50052') as channel:
        stub = VerifyStub(channel)
        await stub.InitializeRequestData(compose_verification_request(checkout_request=request, orderId=order_id))

async def initialize_detect_fraud_data(order_id: str, request: CheckoutRequest) -> None:
    logger.debug("Initializing data in fraud detection service")
    async with grpc.aio.insecure_channel('fraud_detection:50051') as channel:
        stub = FraudDetectionServiceStub(channel)
        await stub.InitializeRequestData(compose_fraud_detection_data(order_id, request))


async def initialize_suggest_books_data(order_id: str, _: CheckoutRequest) -> None:
    logger.debug("Initializing data in book suggestions service")
    async with grpc.aio.insecure_channel('book_suggestions:50053') as channel:
        stub = SuggestionsServiceStub(channel)
        await stub.InitializeRequestData(
            SuggestionsData(
                orderId=order_id,
                # As currently there is no users and database with books and no book ids
                # for POC we just generate some ids
                userId="1",
                boughtBookIds=[str(randint(0, 63)) for _ in range(5)]
            )
        )


async def process_order(order_id: str):
    """
    We have events:
    a) Verification of order data
    b) Verification of user data
    c) Lightweight (faster model) fraud detection
    d) Heavyweight (slower model) fraud detection
    e) Book suggestions

    events a and b can be run in parallel (a||b)
    event c runs only after event a (a -> c, b || c), may run in parallel with b, if a finishes early
    event d runs only after event events a and b (a -> d, b -> d, d || c), may run in parallel with c
    event e runs only after event d and c (d -> e, c -> e)
    """
    logger.info(f"Processing order with id {order_id}")
    with asyncio.TaskGroup as tg:
        # a || b
        order_data_verification = tg.create_task(verify_order_data(order_id))
        user_data_verification = tg.create_task(verify_user_data(order_id))

        order_data_verification_response = await order_data_verification  # a -> c
        quick_fraud_detection = tg.create_task(detect_fraud_quick(order_id))

        user_data_verification_response = await user_data_verification  # a -> d, b -> d
        comprehensive_fraud_detection = tg.create_task(detect_fraud_comprehensive(order_id))

        # d || c
        quick_fraud_detection_response, comprehensive_fraud_detection_response = await gather(
            quick_fraud_detection,
            comprehensive_fraud_detection
        )
        # TODO: needs rework
        #   Easiest is to do method create_error_event that raises custom exception (to pass data through),
        #   then try-catch it in checkout
        # if fraud_detection_response.isFraudulent:
        #     return create_error_message("FRADULENT_REQUEST", fraud_detection_response.reason), 400
        # if fraud_detection_response.isFraudulent:
        #     return create_error_message("FRADULENT_REQUEST", fraud_detection_response.reason), 400
        # if verification_response.statusCode != 0:
        #     return create_error_message("FAILED_VERIFICATION", verification_response.statusMsg), 400
        # if fraud_detection_response.isFraudulent:
        #     return create_error_message("FRADULENT_REQUEST", fraud_detection_response.reason), 400

        # d -> e, c -> e
        return await suggest_books(order_id)


# Event a
async def verify_order_data(order_id: str) -> VerificationResponse:
    logger.debug("Executing event: order data verification")
    async with grpc.aio.insecure_channel('order_verification:50052') as channel:
        stub = VerifyStub(channel=channel)
        return await stub.VerifyOrderData(
            VerifyData(orderId=order_id)
        )


# Event b
async def verify_user_data(order_id: str):
    logger.debug("Executing event: user data verification")
    async with grpc.aio.insecure_channel('order_verification:50052') as channel:
        stub = VerifyStub(channel=channel)
        return await stub.VerifyUserData(
            VerifyData(orderId=order_id)
        )


# Event c
async def detect_fraud_quick(order_id: str) -> QuickFraudDetectionResponse:
    logger.debug("Executing event: quick fraud detection")
    async with grpc.aio.insecure_channel('fraud_detection:50051') as channel:
        stub = FraudDetectionServiceStub(channel)
        response: QuickFraudDetectionResponse = await stub.DetectFraudQuick(
            QuickFraudDetectionRequest(orderId=order_id)
        )
        return response


# Event d
async def detect_fraud_comprehensive(order_id: str) -> ComprehensiveFraudDetectionResponse:
    logger.debug("Executing event: comprehensive fraud detection")
    async with grpc.aio.insecure_channel('fraud_detection:50051') as channel:
        stub = FraudDetectionServiceStub(channel)
        response: ComprehensiveFraudDetectionResponse = await stub.DetectFraudComprehensive(
            ComprehensiveFraudDetectionRequest(orderId=order_id)
        )
        return response


# Event e
async def suggest_books(order_id: str) -> list[Book]:
    logger.debug("Executing event: book suggestion")
    async with grpc.aio.insecure_channel('book_suggestions:50053') as channel:
        stub = SuggestionsServiceStub(channel)
        response: BookSuggestionResponse = await stub.SuggestBooks(BookSuggestionRequest(orderId=order_id))
        return [*map(to_book, response.suggestedBooks)]


async def clear_order_data(order_id: str):
    await gather(
        clear_fraud_detection_data(order_id),
        clear_verification_data(order_id),
        clear_suggestions_data(order_id)
    )


async def clear_fraud_detection_data(order_id: str) -> None:
    logger.debug("Executing event: book suggestion")
    async with grpc.aio.insecure_channel('fraud_detection:50051') as channel:
        stub = FraudDetectionServiceStub(channel)
        await stub.ClearData(ClearSuggestionsDataRequest(orderId=order_id))


async def clear_verification_data(order_id: str) -> None:
    logger.debug("Removing data from transaction verification ")
    async with grpc.aio.insecure_channel('order_verification:50052') as channel:
        ...


async def clear_suggestions_data(order_id: str) -> None:
    logger.debug("Executing event: book suggestion")
    async with grpc.aio.insecure_channel('book_suggestions:50053') as channel:
        stub = SuggestionsServiceStub(channel)
        await stub.ClearData(ClearSuggestionsDataRequest(orderId=order_id))


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


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
