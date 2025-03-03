import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/verification'))
sys.path.insert(0, fraud_detection_grpc_path)
import verification_pb2 as verification
import verification_pb2_grpc as verification_grpc
import grpc

class VerificationService(verification_grpc.VerifyServicer):
    def CheckOrder(self, request:verification.Order, context):
         response = verification.verificationResponse()
         response.statusCode = 0
         response.statusMsg = "all good"
         return response

def server():
     server = grpc.server()
     verification_grpc.add_VerifyServicer_to_server(VerificationService(),server)
     port = "50052"
     server.add_insecure_port("[::]:" + port)
     server.start()
     print(f'Verification service started on port {port}')
     server.wait_for_termination()

     if __name__ == '__main__':
          server()
