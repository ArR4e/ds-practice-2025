import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
from fraud_detection_pb2 import FraudDetectionData, InitializeRequestDataResponse, \
    QuickFraudDetectionRequest, QuickFraudDetectionResponse, \
    ComprehensiveFraudDetectionRequest, ComprehensiveFraudDetectionResponse, \
    ClearFraudDetectionDataRequest, ClearFraudDetectionDataResponse
from fraud_detection_pb2_grpc import FraudDetectionServiceServicer, add_FraudDetectionServiceServicer_to_server
import grpc
from concurrent import futures

import logging.config
from pathlib import Path
from json import load

global logger
logger = logging.getLogger("fraud_logger")
path = Path(__file__).parent/"config.json"
with open(path) as file:
    config = load(file)
logging.config.dictConfig(config=config)

class FraudDetectionServiceService(FraudDetectionServiceServicer):
    detection_data_store: dict[str, FraudDetectionData]

    def __init__(self):
        super().__init__(self)
        self.detection_data_store = {}

    def InitializeRequestData(self, request: FraudDetectionData, context) -> InitializeRequestDataResponse:
        self.detection_data_store[request.orderId] = request
        return InitializeRequestDataResponse()

    def DetectFraudQuick(self, request: QuickFraudDetectionRequest, context) -> QuickFraudDetectionResponse:
        logger.debug(f"Incoming quick fraud detection request {request}")
        fraud_detection_data = self.detection_data_store[request.orderId]
        response = QuickFraudDetectionResponse()
        response.isFraudulent = fraud_detection_data.telemetry.browser.name == "IE"
        response.reason = "We do not support IE (based)"
        return response

    def DetectFraudComprehensive(self, request: ComprehensiveFraudDetectionRequest,
                                 context) -> ComprehensiveFraudDetectionResponse:
        logger.debug(f"Incoming comprehensive fraud detection request {request}")
        fraud_detection_data = self.detection_data_store[request.orderId]
        response = ComprehensiveFraudDetectionResponse()
        response.isFraudulent = fraud_detection_data.telemetry.device == "Raspberry"
        response.reason = "Suspicious device detected"
        return response

    def ClearData(self, request: ClearFraudDetectionDataRequest, context) -> ClearFraudDetectionDataResponse:
        self.detection_data_store.pop(request.orderId, None)
        return ClearFraudDetectionDataResponse()


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    add_FraudDetectionServiceServicer_to_server(FraudDetectionServiceService(), server)
    port = "50051"
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info(f"Server started. Listening on port {port}.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()