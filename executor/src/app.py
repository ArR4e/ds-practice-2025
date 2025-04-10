import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

queue_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/priority_queue'))
sys.path.insert(0, queue_path)

verification_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/verification'))
sys.path.insert(0, verification_path)

pb_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, pb_path)


from verification_pb2 import VerificationRequest
from queue_service_pb2_grpc import QueueStub
from queue_service_pb2 import OrderRequest


import grpc
from concurrent import futures
import logging.config
from pathlib import Path
from json import load
import time
from uuid import uuid4

global logger
logger = logging.getLogger("queue_logger")
path = Path(__file__).parent/"config.json"
with open(path) as file:
    config = load(file)
logging.config.dictConfig(config=config)

class ExecutorService:
    def __init__(self, id, known_ids, queue_stub: str):
        self.id = id
        self.known_ids = known_ids
        self.queue_addr = queue_stub
        self.leader_id = None

    def start_leader_election(self):
        pass
    

    def run(self):
        while True:
            if self.leader_id.__eq__(self.id):
                with grpc.insecure_channel(self.queue_addr) as channel:
                    stub = QueueStub(channel=channel)
                    order: VerificationRequest = stub.Dequeue(OrderRequest())
                    logger.info(f'Processing order {order.orderId}')

            time.sleep(1)
                    



def server():
    queue_stub = 'queue_service:50055'
    executor = ExecutorService(id=uuid4(), known_ids=[], queue_stub=queue_stub)
    executor.start_leader_election()
    executor.run()
    logger.info(f'Queue service started on port XXX')

if __name__ == '__main__':
    server()
