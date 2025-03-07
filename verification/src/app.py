import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/verification'))
sys.path.insert(0, fraud_detection_grpc_path)

from verification_pb2 import VerificationRequest
import verification_pb2
import verification_pb2_grpc
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

    def CheckOrder(self, request:VerificationRequest, context) -> verification_pb2.VerificationResponse:
        logger.info(f"verifing order from user {request.user}")
        name:str = request.user.name
        email:str = request.user.contact
        creditcard = request.creditCard
        if any(char.isdigit() for char in name):
             logger.info(f"FAILURE: validation for {request} has failed")
             return generate_failure_message("found numbers in name")
        if not email.__contains__('@'):
             logger.info(f"FAILURE: validation for {request} has failed")
             return generate_failure_message("invalid email")
        if len(creditcard.cvv) != 3:
              logger.info(f"FAILURE: validation for {request} has failed")
              return generate_failure_message("invalid CVV")
        if not check_expiration_date(creditcard):
             logger.info(f"FAILURE: validation for {request} has failed")
             return generate_failure_message("invalid expiration date")
        logger.info(f"SUCCESS: validation for {request} was successful")
        return generate_success_message()

def check_expiration_date(creditcard: VerificationRequest.creditCard) -> bool:
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

def generate_success_message(message: str = "all good") -> verification_pb2.VerificationResponse:
     response = verification_pb2.VerificationResponse()
     response.statusCode = 0
     response.statusMsg = message
     return response

def generate_failure_message(message: str) -> verification_pb2.VerificationResponse:
    response = verification_pb2.VerificationResponse()
    response.statusCode = 1
    response.statusMsg = message
    return response

if __name__ == '__main__':
    server()
