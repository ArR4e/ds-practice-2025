import sys
import os
from typing import Iterable

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/verification'))
sys.path.insert(0, fraud_detection_grpc_path)

from verification_pb2 import VerificationRequest, VerificationResponse, \
CreditCard, OrderData, VerifyData, ClearDataRequest
import verification_pb2 as verification_pb2
import verification_pb2_grpc as verification_pb2_grpc
import grpc
import datetime
from concurrent import futures
import logging.config
from pathlib import Path
from json import load

global logger
logger = logging.getLogger("verification_logger")
path = Path(__file__).parent/"config.json"
with open(path) as file:
    config = load(file)
logging.config.dictConfig(config=config)

class VerificationService(verification_pb2_grpc.VerifyServicer):

     data_store: dict[str, VerificationRequest]
     shipping_methods: list[str]

     def __init__(self):
        super().__init__()
        self.data_store = {}
        self.shipping_methods = ['Standard', 'Express', 'Next-Day']

     def InitializeRequestData(self, request: VerificationRequest, context) -> VerificationResponse:
          self.data_store[request.orderId] = request
          return generate_success_message()
     

     def VerifyOrderData(self, request: VerifyData, context) -> VerificationResponse:
          full_order: VerificationRequest = self.data_store[request.orderId]
          order_data: OrderData = full_order.orderData
          items: Iterable[OrderData.OrderItem] = order_data.orderItems
          discount_code: str = order_data.discountCode
          shipping_method: str = order_data.shippingMethod

          if any(item.quantity < 1 for item in items):
               return generate_failure_message(message='quantity cannot be less than 1')
          #TODO implement discount code check from known codes
          if discount_code.__eq__('testingerror'):
               return generate_failure_message(message='FOR TESTING: failed at discount_code check')
          if not self.shipping_methods.__contains__(shipping_method):
               return generate_failure_message(message="bad shipping method")
          return generate_success_message(message='SUCCESS')
     
     def VerifyUserData(self, request: VerifyData, context) -> VerificationResponse:
          request: VerificationRequest = self.data_store[request.orderId]
          logger.info(f"verifing order from user {request.user}")
          name = request.user.name
          email = request.user.contact
          creditcard = request.creditCard
          if any(char.isdigit() for char in name):
             logger.info(f"validation for {request} has failed")
             return generate_failure_message("found numbers in name")
          if '@' not in email:
             logger.info(f"FAILURE: validation for {request} has failed")
             return generate_failure_message("invalid email")
          if len(creditcard.cvv) != 3:
              logger.info(f"FAILURE: validation for {request} has failed")
              return generate_failure_message("invalid CVV")
          if not check_expiration_date(creditcard):
             logger.info(f"FAILURE: validation for {request} has failed")
             return generate_failure_message("invalid expiration date")
          logger.info(f"SUCCESS: validation for {request} was successful")
          return generate_success_message(message='SUCCESS')
        
     def ClearData(self, request: ClearDataRequest, context):
         self.data_store.pop(request.orderId)
         return generate_success_message(message='SUCCESS')

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
     verification_pb2_grpc.add_VerifyServicer_to_server(VerificationService(),server)
     port = "50052"
     server.add_insecure_port("[::]:" + port)
     server.start()
     logger.info(f'Verification service started on port {port}')
     server.wait_for_termination()

def generate_success_message(message: str = "all good") -> VerificationResponse:
     response = verification_pb2.VerificationResponse()
     response.status = True
     response.msg = message
     return response

def generate_failure_message(message: str) -> VerificationResponse:
    response = VerificationResponse()
    response.status = False
    response.msg = message
    return response

if __name__ == '__main__':
    server()
