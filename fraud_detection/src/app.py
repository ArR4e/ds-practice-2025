import sys
import os


# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
common_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/common'))
sys.path.insert(0, common_grpc_path)
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
from common_pb2 import VectorClock
from fraud_detection_pb2 import FraudDetectionData, InitializeRequestDataResponse, \
    QuickFraudDetectionRequest, QuickFraudDetectionResponse, \
    ComprehensiveFraudDetectionRequest, ComprehensiveFraudDetectionResponse, \
    ClearFraudDetectionDataRequest, ClearFraudDetectionDataResponse
from fraud_detection_pb2_grpc import FraudDetectionServiceServicer, add_FraudDetectionServiceServicer_to_server
from typing_support import OrderFraudDetectionData
import grpc
from concurrent import futures

import logging.config
from pathlib import Path
from json import load
from typing import Iterable
from threading import Lock

global logger
logger = logging.getLogger("fraud_logger")
path = Path(__file__).parent / "config.json"
with open(path) as file:
    config = load(file)
logging.config.dictConfig(config=config)


class FraudDetectionServiceService(FraudDetectionServiceServicer):
    detection_data_store: dict[str, OrderFraudDetectionData]

    def __init__(self, service_idx: int, total_services: int):
        super().__init__()
        self.service_idx = service_idx
        self.total_services = total_services
        self.detection_data_store = {}

    def InitializeRequestData(self, request: FraudDetectionData, context) -> InitializeRequestDataResponse:
        self.detection_data_store[request.orderId] = {"data": request, "vector_clock": [0] * self.total_services,
                                                      "lock": Lock()}
        return InitializeRequestDataResponse()

    def DetectFraudQuick(self, request: QuickFraudDetectionRequest, context) -> QuickFraudDetectionResponse:
        logger.debug(f"Incoming quick fraud detection request {request}")
        fraud_detection_data = self.detection_data_store[request.orderId]
        vector_clock = self.merge_and_increment(fraud_detection_data["lock"], fraud_detection_data["vector_clock"],
                                                request.vectorClock.clock)
        return QuickFraudDetectionResponse(
            isFraudulent=fraud_detection_data["data"].telemetry.browser.name == "IE",
            reason="We do not support IE (based)",
            vectorClock=VectorClock(clock=vector_clock)
        )

    def DetectFraudComprehensive(self, request: ComprehensiveFraudDetectionRequest,
                                 context) -> ComprehensiveFraudDetectionResponse:
        logger.debug(f"Incoming comprehensive fraud detection request {request}")
        fraud_detection_data = self.detection_data_store[request.orderId]
        vector_clock = self.merge_and_increment(fraud_detection_data["lock"], fraud_detection_data["vector_clock"],
                                                request.vectorClock.clock)
        return ComprehensiveFraudDetectionResponse(
            isFraudulent=fraud_detection_data["data"].telemetry.device == "Raspberry",
            reason="Suspicious device detected",
            vectorClock=VectorClock(clock=vector_clock)
        )

    def ClearData(self, request: ClearFraudDetectionDataRequest, context) -> ClearFraudDetectionDataResponse:
        # TODO: check vector clock <=
        self.detection_data_store.pop(request.orderId, None)
        return ClearFraudDetectionDataResponse()

    def merge_and_increment(self, lock: Lock, local_vector_clock: list[int], incoming_vector_clock: Iterable[int]) -> \
    list[int]:
        with lock:
            for i, (local_clock, incoming_clock) in enumerate(zip(local_vector_clock, incoming_vector_clock)):
                local_vector_clock[i] = max(local_clock, incoming_clock)
            local_vector_clock[self.service_idx] += 1
            logging.debug(f"Received event; updated vector clock: {local_vector_clock}")
            return local_vector_clock.copy()


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    add_FraudDetectionServiceServicer_to_server(FraudDetectionServiceService(1, 3), server)
    port = "50051"
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info(f"Server started. Listening on port {port}.")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
