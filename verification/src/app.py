import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
common_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/common'))
sys.path.insert(0, common_grpc_path)
verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/verification'))
sys.path.insert(0, verification_grpc_path)

from common_pb2 import VectorClock
from verification_pb2 import InitializeRequestDataResponse, VerificationRequest, VerificationResponse, \
    CreditCard, OrderData, VerifyData, ClearDataRequest, ClearDataResponse
import verification_pb2_grpc as verification_pb2_grpc
from typing_support import VerificationOrderData

import grpc
import datetime
from concurrent import futures
import logging.config
from pathlib import Path
from json import load
from threading import Lock
from typing import Iterable

global logger
logger = logging.getLogger("verification_logger")
path = Path(__file__).parent/"config.json"
with open(path) as file:
    config = load(file)
logging.config.dictConfig(config=config)

class VerificationService(verification_pb2_grpc.VerifyServicer):

     data_store: dict[str, VerificationOrderData]
     shipping_methods: list[str]

     def __init__(self, service_idx: int, total_services: int):
        super().__init__()
        self.data_store = {}
        self.service_idx = service_idx
        self.total_services = total_services
        self.shipping_methods = ['Standard', 'Express', 'Next-Day']

     def InitializeRequestData(self, request: VerificationRequest, context) -> InitializeRequestDataResponse:
          self.data_store[request.orderId] =  {"data": request, "vector_clock": [0] * self.total_services, "lock": Lock()}
          return InitializeRequestDataResponse(confirmation=True)
     

     def VerifyOrderData(self, request: VerifyData, context) -> VerificationResponse:
          full_order: VerificationOrderData = self.data_store[request.orderId]
          vector_clock = self.merge_and_increment(full_order["lock"], full_order["vector_clock"], request.vectorClock.clock)
          order_data: OrderData = full_order["data"].orderData
          items: Iterable[OrderData.OrderItem] = order_data.orderItems
          discount_code: str = order_data.discountCode
          shipping_method: str = order_data.shippingMethod

          if any(item.quantity < 1 for item in items):
               return generate_failure_message(message='quantity cannot be less than 1', vector_clock=vector_clock)
          #TODO implement discount code check from known codes
          if discount_code.__eq__('testingerror'):
              logger.info(f"FAILURE: validation for ({request.orderId} has failed; testing error at discount code ")
              return generate_failure_message(message='FOR TESTING: failed at discount_code check', vector_clock=vector_clock)
          if not self.shipping_methods.__contains__(shipping_method):
              logger.info(f"FAILURE: validation for ({request.orderId} has failed: bad shipping method")
              return generate_failure_message(message="bad shipping method", vector_clock=vector_clock)
          return generate_success_message(message='SUCCESS', vector_clock=vector_clock)

     def VerifyUserData(self, request: VerifyData, context) -> VerificationResponse:
         verification_data: VerificationOrderData = self.data_store[request.orderId]
         vector_clock = self.merge_and_increment(verification_data["lock"], verification_data["vector_clock"], request.vectorClock.clock)
         user_data = verification_data["data"].user
         name = user_data.name
         email = user_data.contact
         creditcard = verification_data["data"].creditCard
         logger.info(f"Verifying order (oid:{request.orderId}) from user {user_data} with credit card {creditcard}")
         if any(char.isdigit() for char in name):
             logger.info(f"FAILURE: validation for ({request.orderId} has failed")
             return generate_failure_message("found numbers in name", vector_clock=vector_clock)
         if '@' not in email:
             logger.info(f"FAILURE: validation for ({request.orderId}) has failed")
             return generate_failure_message("invalid email", vector_clock=vector_clock)
         if len(creditcard.cvv) != 3:
             logger.info(f"FAILURE: validation for ({request.orderId}) has failed")
             return generate_failure_message("invalid CVV", vector_clock=vector_clock)
         if not check_expiration_date(creditcard):
             logger.info(f"FAILURE: validation for ({request.orderId}) has failed: invalid expiration date")
             return generate_failure_message("invalid expiration date", vector_clock=vector_clock)
         logger.info(f"SUCCESS: validation for {request.orderId} was successful")
         return generate_success_message(message='SUCCESS', vector_clock=vector_clock)

     def ClearData(self, request: ClearDataRequest, context) -> ClearDataResponse:
         if self.less_than(self.data_store[request.orderId]["lock"], self.data_store[request.orderId]["vector_clock"], request.vectorClock.clock):
             logging.info("Local vector clock is <= incoming vector clock, removing data")
             self.data_store.pop(request.orderId, None)
         else:
            logging.info("Local vector clock is not <= incoming vector clock; rejecting request for removing data")
         return ClearDataResponse()

     def merge_and_increment(self, lock: Lock, local_vector_clock: list[int], incoming_vector_clock: Iterable[int]) -> list[int]:
         with lock:
             for i, (local_clock, incoming_clock) in enumerate(zip(local_vector_clock, incoming_vector_clock)):
                 local_vector_clock[i] = max(local_clock, incoming_clock)
             local_vector_clock[self.service_idx] += 1
             logging.debug(f"Received event; updated vector clock: {local_vector_clock}")
             return local_vector_clock.copy()

     def less_than(self, lock: Lock, local_vector_clock: list[int], incoming_vector_clock: Iterable[int]) -> bool:
        with lock:
            return all(local_clock <= incoming_clock for (local_clock, incoming_clock) in zip(local_vector_clock, incoming_vector_clock))


def check_expiration_date(creditcard: CreditCard) -> bool:
    try:
        currenttime = datetime.datetime.now()
        expiration_date:list[str] = creditcard.expirationDate.split('/')
        month, year = int(expiration_date[0]), int(expiration_date[1])
        if currenttime.month <= month and currenttime.year <= year+2000:
            return True
        return False
    except:
        logger.error("error parsing expirationDate -->", creditcard.expirationDate)
        return False

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    verification_pb2_grpc.add_VerifyServicer_to_server(VerificationService(0, 3),server)
    port = "50052"
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info(f'Verification service started on port {port}')
    server.wait_for_termination()

def generate_success_message(message: str, vector_clock: list[int]) -> VerificationResponse:
    return VerificationResponse(
        status = True,
        msg=message,
        vectorClock=VectorClock(clock=vector_clock)
    )

def generate_failure_message(message: str, vector_clock: list[int]) -> VerificationResponse:
    return VerificationResponse(
        status=False,
        msg=message,
        vectorClock=VectorClock(clock=vector_clock)
    )

if __name__ == '__main__':
    server()
