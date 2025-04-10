import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/queue'))
sys.path.insert(0, fraud_detection_grpc_path)

from queue_pb2_grpc import QueueServicer, add_QueueServicer_to_server
from queue_pb2 import *
from verification_pb2 import VerificationRequest, OrderData

import grpc
from concurrent import futures
import logging.config
from pathlib import Path
from json import load
import threading
import heapq

global logger
logger = logging.getLogger("queue_logger")
path = Path(__file__).parent/"config.json"
with open(path) as file:
    config = load(file)
logging.config.dictConfig(config=config)


class QueueService(QueueServicer):
    def __init__(self):
        self._lock = threading.Lock()
        self.queue: list[VerificationRequest] = []
        self.counter = 0

    def Enqueue(self, request: VerificationRequest, context) -> OrderConfirmation:
        with self._lock:
            priority = self.calculatePriority(request)
            heapq.heappush(self.queue, (-priority, self.counter, request))
            self.counter += 1
            logger.info(f'SUCCESS: added order {request.orderId} to queue')
            return OrderConfirmation(status=True, msg="SUCCESS")


    #TODO have a better response to executor
    def Dequeue(self, request: OrderRequest, context) -> VerificationRequest:
        with self._lock:
            if not self.queue:
                return VerificationRequest(orderId='0')
            else:
                _, _, order = heapq.heappop(self.queue)
                logger.info(f'SUCCESS: order {order.orderId} was extracted')
                return order

    #TODO fix pricing
    def calculatePriority(self, request: VerificationRequest) -> float:
        order_items: list[OrderData.OrderItem] = request.orderData.orderItems
        return sum(item.quantity * 1 for item in order_items)

def server():
     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
     add_QueueServicer_to_server(QueueService(),server)
     port = "50055"
     server.add_insecure_port("[::]:" + port)
     server.start()
     logger.info(f'Queue service started on port {port}')
     server.wait_for_termination()

if __name__ == '__main__':
    server()
