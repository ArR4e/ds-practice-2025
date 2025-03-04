import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/verification'))
sys.path.insert(0, fraud_detection_grpc_path)

from verification_pb2 import verificationRequest
import verification_pb2
import verification_pb2_grpc
import grpc
import datetime
from concurrent import futures

class VerificationService(verification_pb2_grpc.VerifyServicer):
    
    def CheckOrder(self, request:verificationRequest, context) -> verification_pb2.verificationResponse:
         print(f'verifing order from user {request.user}')
         name:str = request.user.name
         email:str = request.user.contact
         creditcard = request.creditCard
         if any(char.isdigit() for char in name):
              print(f"FAILURE: validation for {request} has failed")
              return generate_failure_message("found numbers in name")
         if not email.__contains__('@'):
              print(f"FAILURE: validation for {request} has failed")
              return generate_failure_message("invalid email")
         if len(creditcard.cvv) != 3:
               print(f"FAILURE: validation for {request} has failed")
               return generate_failure_message("invalid CVV")
         if not check_expiration_date(creditcard):
              print(f"FAILURE: validation for {request} has failed")
              return generate_failure_message("invalid expiration date")
         print(f"SUCCESS: validation for {request} was successful\n\n")
         return generate_success_message()
         
def check_expiration_date(creditcard: verificationRequest.creditCard) -> bool:
     try:
          currenttime = datetime.datetime.now()
          expiration_date:list[str] = creditcard.expirationDate.split('/')
          month, year = int(expiration_date[0]), int(expiration_date[1])
          if currenttime.month <= month and currenttime.year <= year+2000:
               return True
          return False
     except:
          print("error parsing expirationDate -->", creditcard.expirationDate)
          return False

def server():
     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
     verification_pb2_grpc.add_VerifyServicer_to_server(VerificationService(),server)
     port = "50052"
     server.add_insecure_port("[::]:" + port)
     server.start()
     print(f'Verification service started on port {port}')
     server.wait_for_termination()

def generate_success_message(message: str = "all good") -> verification_pb2.verificationResponse:
     response = verification_pb2.verificationResponse()
     response.statusCode = 0
     response.statusMsg = message
     return response

def generate_failure_message(message: str) -> verification_pb2.verificationResponse:
         response = verification_pb2.verificationResponse()
         response.statusCode = 1
         response.statusMsg = message
         return response

if __name__ == '__main__':
    server()
